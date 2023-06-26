"""
Collection of helper functions for website routines.
"""
# pylint: disable=consider-using-f-string, import-error
import re
import datetime
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from helper_io import load_config,\
    load_categories, load_day_total, load_dataframe


def generate_cards(dataframe: pd.DataFrame) -> dbc.Row:
    """
    Generates categorized list of activities in a given timeframe.

    Args:
        dataframe2 (pd.DataFrame): _description_

    Returns:
        dbc.Row: Dash Row with categorized activities.
    """
    cfg = load_config()
    totals = load_day_total(364)
    work_list = []
    personal_list = []
    neutral_list = []

    card_style = {
        'background-color': cfg['CARD_COLOR'],
        'border': f'1px solid {cfg["CARD_OUTLINE_COLOR"]}',
        'margin-bottom': f'{cfg["CATEGORY_CARD_MARGIN"]}px'
    }
    cardbody_style = {'padding': f'{cfg["CARD_PADDING"]}px'}

    for _, row in dataframe.iterrows():
        if row['total'] < cfg['MINIMUM_ACTIVITY_TIME'] / 3600:
            continue
        category = row['category']
        total = totals.loc[0, category]
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
        ], style=cardbody_style)], style=card_style)
        if category == "Work":
            work_list.append(item)
        elif category == "Personal":
            personal_list.append(item)
        else:
            neutral_list.append(item)

    cols = [
        dbc.Col(work_list, class_name='g-0'),
        dbc.Col(personal_list, class_name='g-0', style={
            'margin-left': f'{cfg["CATEGORY_COLUMN_SPACE"]}px',
            'margin-right': f'{cfg["CATEGORY_COLUMN_SPACE"]}px'
        }),
        dbc.Col(neutral_list, class_name='g-0'),
    ]
    return cols


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


def make_listpicker(name: str) -> dbc.Tab:
    """
    Makes the listpicker component with config based on name variable.
    Used to modify a list and display state.

    Args:
        name (str): String used to make labels and ids, such as:
            input-{name}, button-{name}, checklist-{name}.

    Returns:
        dbc.Tab: Listpicker component.
    """
    cfg2 = load_categories()
    names = cfg2[name]
    listpicker = dbc.Tab([
        html.Br(),
        html.H3(name),
        dbc.Row([
            dbc.Col(
                dbc.Input(
                    type="text",
                    placeholder="Enter new item",
                    id=f'input-{name}', autocomplete='off'
                ), className="me-3",
            ),
            dbc.Tooltip(
                "This list uses regex patterns to match events into their \
                    respective categories. Remember to escape special \
                        characters if you want their literals.",
                target=f'input-{name}', placement="bottom"),
            dbc.Col(
                dbc.Button("Submit", color="primary", id=f'button-{name}'),
                width="auto"
            ),
        ], class_name='g-0'),
        html.Hr(),
        dbc.Checklist(
            options=names, value=names, id=f'checklist-{name}',
            style={'font-size': '20px', 'columns': '3'},
            switch=True
        )
    ], label=name)
    return listpicker


def make_colorpicker(id_name: str) -> dbc.Col:
    """
    Makes the colorpicker component with a label and id.
    Used to pick a color, and display text.

    Args:
        id_name (str): Component id.

    Returns:
        dbc.Col: Colorpicker component.
    """
    colorpicker = dbc.Col([
        html.H5(id_name, style={"textAlign": "left"}),
        dbc.Input(
            type="color",
            id=id_name,
            value="#000000",
            style={"width": 200, "height": 50},
        ),
        html.H5(
            ["Saved color is ", html.Span("", id=f'saved-{id_name}')],
            style={"textAlign": "left"}
        ),
    ], className="g-0")
    return colorpicker


def make_valuepicker(
        id_name: str, min_val: int, max_val: int) -> dbc.Col:
    """
    Makes the input component with a label, id, minimium and maximum value.
    Used to pick a value and display text.

    Args:
        id_name (str): Component id.
        min_val (int): Maximum value of the given input.
        max_val (int): Minimum value of the given input.

    Returns:
        dbc.Col: Input component.
    """
    colorpicker = dbc.Col([
        html.H5(id_name, style={"textAlign": "left"}),
        dbc.Input(
            type="number", id=id_name,
            min=min_val, max=max_val, step=1,
            style={"width": 200, "height": 50},
        ),
        html.H5(
            ["Saved value is ", html.Span("", id=f'saved-{id_name}')],
            style={"textAlign": "left"}
        ),
    ], className="g-0")
    return colorpicker


def rgb_to_hex(rgb_string: str) -> str:
    """
    Transforms an rgb string to a hex string.

    Args:
        rgb_string (str): rgb string.

    Returns:
        str: hex string.
    """
    match = re.match(r'^rgb\(\d+,\s*\d+,\s*\d+\)$', rgb_string)
    assert match is not None

    values = re.findall(r'(\d+)', rgb_string)
    hex_code = "#{:02x}{:02x}{:02x}".format(
        int(values[0]), int(values[1]), int(values[2]))
    return hex_code


def hex_to_rgb(hex_string: str) -> str:
    """
    Transforms a rgb string to a hex string.

    Args:
        hex_string (str): hex string.

    Returns:
        str: rgb string.
    """
    match = re.match(r'^#[A-Fa-f0-9]{6}$', hex_string)
    assert match is not None

    rgb_code = "rgb({}, {}, {})".format(
        int(hex_string[1:3], 16),
        int(hex_string[3:5], 16),
        int(hex_string[5:7], 16)
    )
    return rgb_code


def make_heatmap(
        categories: list[str], titles: list[str],
        colors: list[list[str]]) -> list:
    """
    Makes a yealy heatmap using the provided arguments.
    The arguments are lists for multiple graphs support.

    Args:
        categories (list[str]): List of categories from totals database.
        titles (list[str]): List of titles of the heatmaps.
        colors (list[list[str]]): List of colors of the heatmaps.

    Returns:
        list: _description_
    """
    cfg = load_config()
    row = []
    base = [cfg["HEATMAP_BASE_COLOR"], cfg["HEATMAP_BASE_COLOR"]]

    for category, title, color in zip(categories, titles, colors):
        totals = load_dataframe("totals")[category].values
        data = [[
            1 if totals[day_index] >= cfg[f"{category.upper()}_DAILY_GOAL"]
            else 0
            for day_index in range(week * 7, (1 + week) * 7)
        ] for week in range(52)]
        data = list(map(list, zip(*data)))

        fig = go.Figure(data=go.Heatmap(
            z=data, x=list(range(1, 53)), y=list(range(1, 7)),
            xgap=cfg["GOALS_HEATMAP_GAP"], ygap=cfg["GOALS_HEATMAP_GAP"],
            colorscale=base + [color],
            showlegend=False, showscale=False
        ))
        fig.update_layout(
            plot_bgcolor=cfg["BACKGROUND"],
            paper_bgcolor=cfg["BACKGROUND"],
            font_color=cfg['TEXT_COLOR'],
            height=cfg['GOALS_HEATMAP_HEIGHT'],
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
        )
        fig.update_xaxes(
            side="top", title=None, showgrid=False,
            color=cfg['TEXT_COLOR'], tickmode='array',
            tickvals=[1, 10, 20, 30, 40, 50],
            ticktext=[1, 10, 20, 30, 40, 50]
        )
        fig.update_yaxes(
            side="right", title=None, showgrid=False,
            color=cfg['TEXT_COLOR'], tickmode='array',
            tickvals=[7], ticktext=["←"]
        )
        row.append(dbc.Row([
            html.H4(
                title +
                f' ({cfg[f"{category.upper()}_DAILY_GOAL"]} hours)'
            ),
            dcc.Graph(figure=fig, style={'width': '100%'})
        ], style={'margin-bottom': f'{cfg["GOALS_HEATMAP_DIVISION"]}px'}))
    return row
