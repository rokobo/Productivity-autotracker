"""
Updates DataFrame with current activity.
"""
# pylint: disable=protected-access, broad-exception-caught
# pylint: disable=c-extension-no-member, import-error, no-name-in-module
import time
from ctypes import windll
from urllib.parse import urlparse
from win32gui import GetWindowText, GetWindowRect
from win32process import GetWindowThreadProcessId
import pandas as pd
import numpy as np
import yaml
from helper_server import format_long_duration
from helper_retry import try_to_run
from helper_io import load_dataframe, load_input_time, append_to_database, \
    save_dataframe, load_urls, clean_and_select_newest_url, load_config, \
    load_lastest_row, modify_latest_row

cfg = load_config()


def detect_activity() -> tuple[int, str, int, int, str, str, str]:
    """
    Detects user activity and returns tracking variables.

    Returns:
        tuple[int, str, str, int]: time of detection, \
            active window title, window handle, pid, \
                process name, url and domain in case of browser.
    """
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
            \nprocesses = process_iter()\
            \nfor process in processes:\
            \n    if process.pid == pid:\
            \n        process_name = process.name()',
        error_check='processes == ""',
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
        clean_and_select_newest_url()

    # Hide information from apps in HIDDEN_APPS list
    if process_name.lower() in cfg["HIDDEN_APPS"]:
        title = "HIDDEN APPLICATION INFO"

    # Detect fullscreen mode from apps in FULLSCREEN_APPS list
    if process_name.lower() in cfg['FULLSCREEN_APPS']:
        if detect_fullscreen(handle):
            save_dataframe(
                pd.DataFrame({'time': [int(time.time())]}), 'fullscreen')
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
    access_error, urls = load_urls()
    if access_error:
        return "", ""

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
    now = int(time.time())
    mouse_time = now - load_input_time('mouse')
    keyboard_time = now - load_input_time('keyboard')
    audio_time = now - load_input_time('audio')
    fullscreen_time = now - load_input_time('fullscreen')
    idle_time = min(mouse_time, keyboard_time, audio_time, fullscreen_time)

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
    sections = data[1].split(" - ")
    parsed = {
        'start_time': [data[0]],
        'end_time': [data[0]],
        'app': [sections[-1]],
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
    accessible, activity = load_lastest_row('activity')
    if accessible:
        # Check if merge should be done
        same_event = all(activity.iloc[0, 2:9] == dataframe.iloc[0, 2:9])
        not_idle = (
            time.time() - activity.loc[0, 'end_time']) < cfg['IDLE_TIME']
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


def organize_by_date(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Filters dataframe to get events between two dates stored in date.db.

    Args:
        dataframe (pd.DataFrame): Given dataframe.

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    _, date_range = load_dataframe('date')
    start, end = date_range.iloc[0, 0:2]
    filtered_df = dataframe[
        (dataframe['start_time'] >= start) &
        (dataframe['end_time'] <= end)]
    return filtered_df


def categories_sum(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the sum of time of equivalent rows in the input dataframe.

    Args:
        input_dataframe (pd.DataFrame): Activity dataframe.

    Returns:
        pd.DataFrame: Aggregated categorized dataframe.
    """
    dataframe = input_dataframe.copy()
    config_path = '../config/categories.yml'
    with open(config_path, 'r', encoding='utf-8') as file:
        cfg2 = yaml.safe_load(file)

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
    # Get raw data
    raw_data = detect_activity()
    idle_data = detect_idle()
    if idle_data:
        raw_data = idle_data

    # Parse and add to activity file
    parsed_data = parse_data(raw_data)
    join(parsed_data)

    # Make secondary file containing aggregated entries
    _, activity = load_dataframe('activity')
    dated_dataframe = organize_by_date(activity)
    categorized_dataframe = categories_sum(dated_dataframe)

    # Make third file containing total by category
    grouped_dataframe = total_by_category(categorized_dataframe)

    # Save dataframes
    if save_files:
        save_dataframe(categorized_dataframe, 'categories')
        save_dataframe(grouped_dataframe, 'totals')

    # Update last time since backend update
    save_dataframe(pd.DataFrame({'time': [time.time()]}), 'backend')
    return categorized_dataframe, grouped_dataframe
