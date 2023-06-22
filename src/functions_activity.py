"""
Updates DataFrame with current activity.
"""
# pylint: disable=protected-access, broad-exception-caught
# pylint: disable=c-extension-no-member, import-error, no-name-in-module
import time
import re
from threading import Thread
from ctypes import windll
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, wait
from win32gui import GetWindowText, GetWindowRect
from win32process import GetWindowThreadProcessId
import pandas as pd
import numpy as np
from helper_server import format_long_duration
from helper_retry import try_to_run
from helper_io import load_dataframe, load_input_time, append_to_database, \
    save_dataframe, load_urls, clean_and_select_newest_url, load_config, \
    load_lastest_row, modify_latest_row, load_activity_between,\
    load_categories


def detect_activity() -> tuple[int, str, int, int, str, str, str]:
    """
    Detects user activity and returns tracking variables.

    Returns:
        tuple[int, str, str, int]: time of detection, \
            active window title, window handle, pid, \
                process name, url and domain in case of browser.
    """
    cfg = load_config()
    cfg2 = load_categories()
    retries = cfg['RETRY_ATTEMPS']

    handle = try_to_run(
        var='window',
        code='window = GetForegroundWindow()',
        error_check='not isinstance(window, int)',
        final_code='',
        retries=retries*10,
        environment=locals())

    title = GetWindowText(handle)
    assert isinstance(title, str)

    # Get process name
    pid = GetWindowThreadProcessId(handle)[1]

    process_name = try_to_run(
        var='process_name',
        code='process_name = ""\
            \nprocess_name = Process(pid).name()',
        error_check='process_name == "" or not isinstance(process_name, str)',
        final_code='',
        retries=retries,
        environment=locals())

    # Obtain URL in case of browser
    url = ""
    domain = ""
    if process_name == "brave.exe":
        url, domain = match_to_url(title)
    else:
        # Clean url files (clutters if this is not done)
        input_thread = Thread(target=clean_and_select_newest_url)
        input_thread.start()

    # Hide information from apps in HIDDEN_APPS list
    name = process_name.lower()
    if any(re.search(pattern, name) for pattern in cfg2['HIDDEN_APPS']):
        title = "HIDDEN APPLICATION INFO"

    # Detect fullscreen mode from apps in FULLSCREEN_APPS list
    if any(re.search(pattern, name) for pattern in cfg2['FULLSCREEN_APPS']):
        if detect_fullscreen(handle):
            save_dataframe(
                pd.DataFrame({'time': [int(time.time())]}), 'fullscreen')

    # Wait for thread finish
    return (int(time.time()), title, handle, pid, process_name, url, domain)


def match_to_url(title: str) -> tuple[str, str]:
    """
    Matches a window title to a browser tab's URL.

    Args:
        title (str): Title of the active window.

    Returns:
        str: URL of the tab.
        str: Domain of the tab.
    """
    urls = load_urls()

    # Compare window title with list of tab titles
    for current_url in urls:
        if current_url[0] == title.removesuffix(" - Brave"):
            # Get url and domain
            url = current_url[1]
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                domain = parsed.scheme + "://"
            else:
                domain = parsed.netloc
            return url, domain
    return "", ""


def detect_fullscreen(window: int) -> bool:
    """
    Detects if a window is fullscreen.

    Args:
        window (int): Window handle

    Returns:
        bool: True if window is fullscreen.
    """
    user32 = windll.user32
    fullscreen_rect = (
        0, 0,
        user32.GetSystemMetrics(0),
        user32.GetSystemMetrics(1)
    )
    return GetWindowRect(window) == fullscreen_rect


def detect_idle() -> tuple[int, str, int, int, str, str, str]:
    """
    if idle, return a tuple representing raw data of idle activity.

    Returns:
        tuple[int, str, int, int, str, str]: Idle raw data or empty tuple.
    """
    cfg = load_config()
    now = int(time.time())

    # Access all input times concurrently
    executor = ThreadPoolExecutor(max_workers=4)
    mouse_time = executor.submit(load_input_time, 'mouse')
    keyboard_time = executor.submit(load_input_time, 'keyboard')
    audio_time = executor.submit(load_input_time, 'audio')
    fullscreen_time = executor.submit(load_input_time, 'fullscreen')

    wait([mouse_time, keyboard_time, audio_time, fullscreen_time])

    idle_time = min(
        now - mouse_time.result(),
        now - keyboard_time.result(),
        now - audio_time.result(),
        now - fullscreen_time.result())

    if idle_time > cfg['IDLE_TIME']:
        return (now, "Time not counted", -1, -1, "IDLE TIME", "", "")
    return ()


def parse_data(data: tuple[int, str, int, int, str, str, str]) -> pd.DataFrame:
    """
    Transforms the raw data into an appropriate form for processing.

    Args:
        tuple[int, str, str, int]: time of detection, \
            active window title, window handle, pid, \
                process name, url and domain in case of browser.

    Returns:
        pd.DataFrame: Dataframe with parsed data.
    """
    parsed = {
        'start_time': [data[0]],
        'end_time': [data[0]],
        'app': [data[1].split(" - ")[-1]],
        'info': [data[1]],
        'handle': data[2],
        'pid': data[3],
        'process_name': data[4],
        'url': data[5],
        'domain': data[6]
    }
    return pd.DataFrame(parsed)


def join(dataframe: pd.DataFrame) -> None:
    """
    Tries to join current activity to previous activity,
    adds activity otherwise.

    Args:
        pd.DataFrame: Dataframe with parsed data.
    """
    cfg = load_config()
    activity = load_lastest_row('activity')
    # Check if merge should be done
    same_event = all(activity.iloc[0, 2:9] == dataframe.iloc[0, 2:9])
    not_idle = (
        int(time.time()) - activity.loc[0, 'end_time']) < cfg['IDLE_TIME']
    if not_idle:
        if same_event:  # Join to last event
            activity.loc[0, 'end_time'] = dataframe.loc[0, 'end_time']
            modify_latest_row('activity', activity, ['end_time'])
        else:  # Append and connect to last event
            new_time = activity.loc[0, 'end_time']
            dataframe.loc[0, 'start_time'] = new_time
            append_to_database('activity', dataframe)
    else:  # Raw append
        dataframe.loc[0, 'start_time'] -= 1
        append_to_database('activity', dataframe)


def organize_by_date() -> pd.DataFrame:
    """
    Filters activity database to get events between timestamps in date.db.

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    date_range = load_dataframe('date')
    start, end = date_range.iloc[0, 0:2]
    filtered_df = load_activity_between(start, end)
    return filtered_df


def categories_sum(
        dataframe: pd.DataFrame, cfg2: dict[str, any]) -> pd.DataFrame:
    """
    Generates the sum of time of equivalent rows in the input dataframe.

    Args:
        dataframe (pd.DataFrame): Activity dataframe.
        cfg2 (dict[str, any]): Categories dictionary.

    Returns:
        pd.DataFrame: Aggregated categorized dataframe.
    """
    dataframe.loc[
        :, 'duration'] = dataframe['end_time'] - dataframe['start_time']

    # Choose event category and method of choosing
    conditions = [
        dataframe['process_name'].str.contains(
            '|'.join(cfg2['WORK_APPS']), case=False, regex=True),
        dataframe['process_name'].str.contains(
            '|'.join(cfg2['PERSONAL_APPS']), case=False, regex=True),
        dataframe['domain'].str.contains(
            '|'.join(cfg2['WORK_DOMAINS']), case=False, regex=True),
        dataframe['domain'].str.contains(
            '|'.join(cfg2['PERSONAL_DOMAINS']), case=False, regex=True),
        dataframe['domain'] != "",
        dataframe['info'].str.contains(
            '|'.join(cfg2['WORK_KEYWORDS']), case=False, regex=True),
        dataframe['info'].str.contains(
            '|'.join(cfg2['PERSONAL_KEYWORDS']), case=False, regex=True)
    ]
    choices = [
        "Work(A)", "Personal(A)",
        "Work(D)", "Personal(D)", "Neutral(D)",
        "Work(K)", "Personal(K)"
    ]
    dataframe['category'] = np.select(
        conditions, choices, default="Neutral(E)")

    dataframe.loc[:, 'method'] = dataframe['category'].str[-3:]
    dataframe.loc[:, 'category'] = dataframe['category'].str[:-3]

    # Choose appropriate subtitle
    conditions = [
        dataframe['domain'] != "",
        dataframe['method'] != "(A)"
    ]
    choices = [
        dataframe['domain'],
        dataframe['info']
    ]
    dataframe['subtitle'] = np.select(conditions, choices, default="")

    # Aggregate events to simply visualization
    df_sum = dataframe.groupby(
        ['process_name', 'subtitle', 'category', 'method']
    ).agg({'duration': 'sum'}).reset_index()
    df_sum.loc[:, 'total'] = df_sum['duration'] / 3600
    df_sum = df_sum.sort_values(by='duration', ascending=False)
    df_sum.loc[:, 'duration'] = df_sum['duration'].apply(format_long_duration)
    return df_sum


def total_by_category(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Determines how much time each category has in total.

    Args:
        dataframe (pd.DataFrame): Given dataframe.

    Returns:
        pd.DataFrame: Dataframe with the category and it's total time.
    """
    filtered_df = dataframe[dataframe['process_name'] != "IDLE TIME"]
    grouped_df = filtered_df.groupby('category').agg(
        {'total': 'sum'}).reset_index()
    return grouped_df


def parser(save_files: bool = True) -> tuple[pd.DataFrame]:
    """
    Parses raw activity and creates appropriate files.

    Args:
        save_files (bool, optional): If files should be saved. Default True.

    Returns:
        tuple[pd.DataFrame]: Dataframes created.
    """
    # Update backend update time
    arg = (pd.DataFrame({'time': [int(time.time())]}), 'backend')
    input_thread = Thread(target=save_dataframe, args=arg)
    input_thread.daemon = True
    input_thread.start()

    # Get raw data
    raw_data = detect_activity()
    idle_data = detect_idle()
    if idle_data:
        raw_data = idle_data

    # Parse and add to activity file
    parsed_data = parse_data(raw_data)
    join(parsed_data)

    # Make secondary file containing aggregated entries
    dated_dataframe = organize_by_date()
    cfg2 = load_categories()
    categorized_dataframe = categories_sum(dated_dataframe, cfg2)
    if save_files:
        arg = (categorized_dataframe, 'categories')
        categories_thread = Thread(target=save_dataframe, args=arg)
        categories_thread.daemon = True
        categories_thread.start()

    # Make third file containing total by category
    grouped_dataframe = total_by_category(categorized_dataframe)
    save_dataframe(grouped_dataframe, "totals")

    # Wait for thread finish
    if save_files:
        categories_thread.join()
    input_thread.join()
    return categorized_dataframe, grouped_dataframe
