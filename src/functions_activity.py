"""
Updates DataFrame with current activity.
"""
# pylint: disable=protected-access, broad-exception-caught, unused-argument
# pylint: disable=c-extension-no-member, import-error, no-name-in-module
import time
import re
from threading import Thread
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, wait
import pandas as pd
import numpy as np
import pywinctl as pwc
from helper_server import format_long_duration
from helper_io import (
    load_dataframe,
    load_input_time,
    append_to_database,
    save_dataframe,
    load_url,
    load_config,
    load_lastest_row,
    modify_latest_row,
    load_categories,
    timestamp_to_day,
)


def detect_activity() -> tuple[int, str, str, str, str]:
    """
    Detects user activity and returns tracking variables.

    Returns:
        tuple[int, str, str, str, str]: time of detection, \
            active window title, process name, url and domain.
    """
    cfg = load_config()
    cfg2 = load_categories()
    retries = cfg["RETRY_ATTEMPS"]
    start_time = int(time.time())
    title, process_name, url, domain = None, None, None, None

    for _ in range(retries):
        try:
            window = pwc.getActiveWindow()
            title = window.title
            process_name = window.getAppName()
            if not (isinstance(title, str) and isinstance(process_name, str)):
                time.sleep(0.25)
                continue

            if process_name not in ["brave.exe", "brave"]:
                url, domain = "", ""
            else:
                url, domain = match_to_url(title)
            if url is None:
                time.sleep(0.25)
                continue
        except (AssertionError, AttributeError):
            time.sleep(0.25)
        else:
            break

    results = [
        isinstance(title, str),
        isinstance(process_name, str),
        url is not None,
    ]

    # Set to idle in case of failure
    if not all(results):
        print(
            f"\033[93m{time.strftime('%X')} Activity failed to detect,",
            f"setting idle... {results}\033[00m ",
        )
        return (start_time, "Time not counted", "IDLE TIME", "", "")

    # Hide information from apps in HIDDEN_APPS list
    name = process_name.lower()
    if any(re.search(pattern, name) for pattern in cfg2["HIDDEN_APPS"]):
        title = "HIDDEN APPLICATION INFO"
    return (start_time, title, process_name, url, domain)


def match_to_url(title: str) -> tuple[str, str]:
    """
    Matches a window title to a browser tab's URL.

    Args:
        title (str): Title of the active window.

    Returns:
        str: URL of the tab.
        str: Domain of the tab.
    """
    # Correct for special characters
    title = title.encode("utf-8").decode("unicode_escape")
    url = load_url(title.removesuffix(" - Brave"))
    if url.empty:
        return None, None
    url = url.loc[0, "url"]
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        domain = parsed.scheme + "://"
    else:
        domain = parsed.netloc
    return url, domain


def detect_idle() -> tuple[int, str, str, str, str]:
    """
    if idle, return a tuple representing raw data of idle activity.

    Returns:
        tuple[int, str, str, str, str]: Idle raw data or empty tuple.
    """
    cfg = load_config()
    now = int(time.time())

    # Access all input times concurrently
    executor = ThreadPoolExecutor(max_workers=3)
    mouse_time = executor.submit(load_input_time, "mouse")
    keyboard_time = executor.submit(load_input_time, "keyboard")
    audio_time = executor.submit(load_input_time, "audio")

    wait([mouse_time, keyboard_time, audio_time])

    idle_time = min(
        now - mouse_time.result(),
        now - keyboard_time.result(),
        now - audio_time.result(),
    )

    if idle_time > cfg["IDLE_TIME"]:
        return (now, "Time not counted", "IDLE TIME", "", "")
    return ()


def parse_data(data: tuple[int, str, str, str, str]) -> pd.DataFrame:
    """
    Transforms the raw data into an appropriate form for processing.

    Args:
        tuple[int, str, str, str, str]: time of detection, \
            active window title, process name, url and domain.

    Returns:
        pd.DataFrame: Dataframe with parsed data.
    """
    parsed = {
        "start_time": [data[0]],
        "end_time": [data[0]],
        "app": [data[1].split(" - ")[-1]],
        "info": [data[1]],
        "process_name": data[2],
        "url": data[3],
        "domain": data[4],
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
    act = load_lastest_row("activity")

    # Check if merge should be done
    same_event = all(act.iloc[0, 2:7] == dataframe.iloc[0, 2:7])
    same_event &= all(  # Check if events are on the same day
        timestamp_to_day(act["start_time"])
        == timestamp_to_day(dataframe["start_time"])
    )

    not_idle = (int(time.time()) - act.loc[0, "end_time"]) < cfg["IDLE_TIME"]

    if not_idle:
        if same_event:  # Join to last event
            act.loc[0, "end_time"] = dataframe.loc[0, "end_time"]
            modify_latest_row("activity", act, ["end_time"])
        else:  # Append and connect to last event
            new_time = act.loc[0, "end_time"]
            dataframe.loc[0, "start_time"] = new_time
            append_to_database("activity", dataframe)
    else:  # Raw append
        dataframe.loc[0, "start_time"] -= 1
        append_to_database("activity", dataframe)


def categories_sum(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the sum of time of equivalent rows in the input dataframe.

    Args:
        dataframe (pd.DataFrame): Activity dataframe.

    Returns:
        pd.DataFrame: Aggregated categorized dataframe.
    """
    cfg2 = load_categories()

    # Choose event category and method of choosing
    conds = [
        dataframe["process_name"].str.contains(
            "|".join(cfg2["WORK_APPS"]), case=False, regex=True),
        dataframe["process_name"].str.contains(
            "|".join(cfg2["PERSONAL_APPS"]), case=False, regex=True),
        dataframe["domain"].str.contains(
            "|".join(cfg2["WORK_DOMAINS"]), case=False, regex=True),
        dataframe["domain"].str.contains(
            "|".join(cfg2["PERSONAL_DOMAINS"]), case=False, regex=True),
        dataframe["domain"] != "",
        dataframe["info"].str.contains(
            "|".join(cfg2["WORK_KEYWORDS"]), case=False, regex=True),
        dataframe["info"].str.contains(
            "|".join(cfg2["PERSONAL_KEYWORDS"]), case=False, regex=True),
    ]
    choices = [
        "Work(A)", "Personal(A)",
        "Work(D)", "Personal(D)", "Neutral(D)",
        "Work(K)", "Personal(K)",
    ]

    dataframe["category"] = np.select(conds, choices, default="Neutral(E)")

    dataframe.loc[:, "method"] = dataframe["category"].str[-3:]
    dataframe.loc[:, "category"] = dataframe["category"].str[:-3]

    # Choose appropriate subtitle
    conds = [dataframe["domain"] != "", dataframe["method"] != "(A)"]
    choices = [dataframe["domain"], dataframe["info"]]
    dataframe["subtitle"] = np.select(conds, choices, default="")

    # Aggregate events to simply visualization
    df_sum = (
        dataframe.groupby(
            ["process_name", "day", "subtitle", "category", "method"])
        .agg({"total": "sum", "duration": "sum"})
        .reset_index()
    )
    df_sum = df_sum.sort_values(by=["day", "duration"], ascending=False)
    df_sum.loc[:, "duration"] = df_sum["duration"].apply(format_long_duration)
    return df_sum


def parser(save_files: bool = True) -> pd.DataFrame:
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
    act = load_dataframe("activity", False, 'activity_view', False)
    categorized_dataframe = categories_sum(act)
    if save_files:
        arg = (categorized_dataframe, "activity", "categories")
        categories_thread = Thread(target=save_dataframe, args=arg)
        categories_thread.daemon = True
        categories_thread.start()

    # Update backend update time
    arg = (pd.DataFrame({"time": [int(time.time())]}), "backend")
    input_thread = Thread(target=save_dataframe, args=arg)
    input_thread.daemon = True
    input_thread.start()

    # Wait for thread finish
    if save_files:
        categories_thread.join()
    input_thread.join()
    return categorized_dataframe
