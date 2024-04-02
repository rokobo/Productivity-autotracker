"""
Updates DataFrame with current activity.
"""
# pylint: disable=protected-access, broad-exception-caught, unused-argument
# pylint: disable=c-extension-no-member, import-error, no-name-in-module
import time
import re
from typing import Optional
from threading import Thread
from urllib.parse import urlparse
from datetime import datetime
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
    load_latest_row,
    modify_latest_row,
    load_categories,
    timestamp_to_day,
    retry,
)


@retry(wait=0.25, log_result=True)
def detect_activity() -> Optional[tuple[int, str, str, str, str]]:
    """
    Detects user activity and returns tracking variables.

    Returns:
        tuple[int, str, str, str, str]: time of detection, \
            active window title, process name, url and domain.
    """
    cfg2 = load_categories()
    start_time = int(time.time())

    window = pwc.getActiveWindow()
    assert window, "Could not get active window"
    process_name = window.getAppName()
    title = window.title

    assert isinstance(title, str), "Could not find title of window"
    assert isinstance(process_name, str), "Could not find pname of window"

    url, domain = None, None
    if process_name in ["brave.exe", "brave"]:
        result = match_to_url(title)
        if result is not None:
            url, domain = result
    else:
        url, domain = "", ""

    assert url is not None, f"Could not find URL for {title}"
    assert domain is not None, f"Could not find domain for {title}"

    # Hide information from apps in HIDDEN_APPS list
    name = process_name.lower()
    if any(re.search(pattern, name) for pattern in cfg2["HIDDEN_APPS"]):
        title = "HIDDEN APPLICATION INFO"
    return (start_time, title, process_name, url, domain)


def match_to_url(title: str) -> Optional[tuple[str, str]]:
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
    assert url is not None, "URL is None"
    url = url.loc[0, "url"]
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        domain = parsed.scheme + "://"
    else:
        domain = parsed.netloc
    return url, domain


def detect_idle() -> Optional[bool]:
    """
    if idle, return a tuple representing raw data of idle activity.

    Returns:
        tuple[int, bool]: Time now and if idle is detected.
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
        return True
    return False


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


def join(current_act: pd.DataFrame) -> None:
    """
    Tries to join current activity to previous activity,
    adds activity otherwise.

    Args:
        pd.DataFrame: Dataframe with parsed data from latest activity.
    """
    cfg = load_config()
    previous_act = load_latest_row("activity")
    if previous_act is None:
        return
    start1, start2 = previous_act["start_time"], current_act["start_time"]
    assert isinstance(start1, pd.Series) and isinstance(start2, pd.Series)

    # Check if merge should be done and if events are on the same day
    same_event = all(previous_act.iloc[0, 2:7] == current_act.iloc[0, 2:7])
    same_event &= all(timestamp_to_day(start1) == timestamp_to_day(start2))

    not_idle = (
        int(time.time()) - previous_act.loc[0, "end_time"]
    ) < cfg["IDLE_TIME"]

    if not_idle:
        if same_event:  # Join to last event
            previous_act.loc[0, "end_time"] = current_act.loc[0, "end_time"]
            modify_latest_row("activity", previous_act, ["end_time"])
        else:  # Append and connect to last event
            new_time = previous_act.loc[0, "end_time"]
            current_act.loc[0, "start_time"] = new_time
            append_to_database("activity", current_act)
    else:  # Raw append
        current_act.loc[0, "start_time"] -= 1
        append_to_database("activity", current_act)


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
    durations = df_sum["duration"].apply(format_long_duration)
    df_sum = df_sum.astype({"duration": "str"})
    df_sum.loc[:, "duration"] = durations
    return df_sum


def create_categories_database(partial: bool = False) -> None:
    """
    Wrapper function for creating categories DB.

    Args:
        partial (bool, optional): Create partial categories DB?
            Defaults to False.
    """
    if partial:
        act = load_dataframe(
            "activity", False, 'activity_view',
            False, ('day', '=', datetime.now().date()))
    else:
        act = load_dataframe("activity", False, 'activity_view', False)

    if act is None:
        return
    cat_df = categories_sum(act)
    arg = (cat_df, "activity", f"categories{'_partial' if partial else ''}")
    categories_thread = Thread(target=save_dataframe, args=arg)
    categories_thread.daemon = True
    categories_thread.start()


def parser() -> None:
    """Parses raw activity and creates appropriate partial categories DBs."""
    # Get raw data
    raw_data = detect_activity()
    idle_data = detect_idle()

    if raw_data is not None:
        arg = (pd.DataFrame({"time": [int(time.time())]}), "backend")
        save_thread = Thread(target=save_dataframe, args=arg)
        save_thread.daemon = True
        save_thread.start()

    if idle_data or (raw_data is None) or (idle_data is None):
        raw_data = (int(time.time()), "Time not counted", "IDLE TIME", "", "")

    # Parse and add to activity file
    parsed_data = parse_data(raw_data)
    join(parsed_data)

    create_categories_database(True)


def secondary_parser() -> None:
    """Parses activity DB and creates complete categories DB."""
    create_categories_database(False)
