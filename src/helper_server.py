"""
Collection of helper functions for website routines.
"""
from typing import Optional
import datetime
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from helper_io import save_dataframe, load_config, load_dataframe

cfg = load_config()


def generate_cards(dataframe: pd.DataFrame) -> dbc.Row:
    """
    Generates categorized list of activities in a given timeframe.

    Args:
        dataframe2 (pd.DataFrame): _description_

    Returns:
        dbc.Row: Dash Row with categorized activities.
    """
    totals = load_dataframe('totals')[1]
    work_list = []
    personal_list = []
    neutral_list = []
    for _, row in dataframe.iterrows():
        if row['total'] < cfg['MINIMUM_ACTIVITY_TIME'] / 3600:
            continue
        category = row['category']
        total = totals.loc[totals["category"] == category, "total"].values[0]
        percentage1 = f'{round(row["total"] / 16 * 100, 1)}% day '
        percentage2 = f' {round(row["total"] / total * 100, 1)}% total'
        percentage2 = percentage2 if row["process_name"] != "IDLE TIME" else ""
        item = dbc.Card([dbc.CardBody([
            dbc.Row([
                html.H4(f'{row["process_name"]} {row["method"]}'),
                html.H5(row['subtitle']) if row['subtitle'] else None
            ], className="g-0", align='center'),
            dbc.Row([
                dbc.Col(
                    html.H6(percentage1),
                    style={"color": cfg["CATEGORY_CARD_PERCENTAGE_COLOR"]},
                    width="auto"
                ),
                dbc.Col(
                    html.H6(row['duration']),
                    width="auto"
                ),
                dbc.Col(
                    html.H6(percentage2),
                    style={"color": cfg["CATEGORY_CARD_PERCENTAGE_COLOR"]},
                    width="auto"
                )
            ], className="justify-content-center g-0")
        ])], className='category-card')
        if category == "Work":
            work_list.append(item)
        elif category == "Personal":
            personal_list.append(item)
        else:
            neutral_list.append(item)
    row = dbc.Row([
        dbc.Col(work_list, width=4),
        dbc.Col(personal_list, width=4),
        dbc.Col(neutral_list, width=4)
    ])
    return row


def get_day_timestamps(date: str):
    """
    Generates the timestamps of the start and end of the given day.

    Args:
        date (str): Given date.

    Returns:
        tuple(int, int): Timestamps.
    """
    current_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    # Start of the day
    start_of_day = datetime.datetime.combine(current_date, datetime.time.min)
    start_timestamp = int(start_of_day.timestamp())

    # End of the day
    end_of_day = datetime.datetime.combine(current_date, datetime.time.max)
    end_timestamp = int(end_of_day.timestamp())
    return start_timestamp, end_timestamp


def set_date_range(start: Optional[int] = None, end: Optional[int] = None):
    """
    Sets the date range file to the passed values or today in case of None.

    Args:
        start (int): Start date timestamp.
        end (int): End date timestamp.

    Returns:
        start (int): Start date timestamp.
        end (int): End date timestamp.
    """
    start_today, end_today = get_day_timestamps(
        str(datetime.datetime.now().date()))
    if start is None:
        start = start_today
    if end is None:
        end = end_today
    save_dataframe(
        pd.DataFrame({'start_time': [start], 'end_time': [end]}), 'date')
    return start, end


def format_duration(seconds: int, long: bool) -> str:
    """
    Formats seconds into a readable string.

    Args:
        seconds (int): Seconds to be converted.
        long (bool): If string should contain non-abbreviated units

    Returns:
        str: Readable string.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    duration_parts = []
    units = [" hour", " minute", " second"] if long else ["h", "m", "s"]
    join_string = ", " if long else " "
    if hours > 0:
        duration_parts.append(
            f"{int(hours)}{units[0]}{'s' if hours > 1 and long else ''}")
    if minutes > 0:
        duration_parts.append(
            f"{int(minutes)}{units[1]}{'s' if minutes > 1 and long else ''}")
    if seconds > 0 or not duration_parts:
        duration_parts.append(
            f"{int(seconds)}{units[2]}{'s' if seconds > 1 and long else ''}")
    return join_string.join(duration_parts)


def format_long_duration(seconds: int) -> str:
    """
    Wrapper function that formats seconds into a long readable string.

    Args:
        seconds (int): Seconds to be converted.

    Returns:
        str: Readable string.
    """
    return format_duration(seconds, True)


def format_short_duration(seconds: int) -> str:
    """
    Wrapper function that formats seconds into a short readable string.

    Args:
        seconds (int): Seconds to be converted.

    Returns:
        str: Readable string.
    """
    return format_duration(seconds, False)
