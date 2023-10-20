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
import plotly.express as px
from helper_io import load_config, load_categories, load_day_total, \
    load_dataframe, get_break_days


def generate_cards(dataframe: pd.DataFrame, totals=None) -> dbc.Row:
    """
    Generates categorized list of activities in a given timeframe.

    Args:
        dataframe (pd.DataFrame): Dataframe with categories.
        totals (pd.DataFrame): Total time of three categories for comparison.

    Returns:
        dbc.Row: Dash Row with categorized activities.
    """
    if totals is None:
        totals = load_day_total(364)
    cfg = load_config()
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
        percentage2 = 0 if total == 0 \
            else f' {round(row["total"] / total * 100, 1)}% total'
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
        id_name: str, min_val: int, max_val: int, step=1.0) -> dbc.Col:
    """
    Makes the input component with a label, id, minimium and maximum value.
    Used to pick a value and display text.

    Args:
        id_name (str): Component id.
        min_val (int): Maximum value of the given input.
        max_val (int): Minimum value of the given input.
        step (float, optional): Step in value. Defaults to 1.0

    Returns:
        dbc.Col: Input component.
    """
    colorpicker = dbc.Col([
        html.H5(id_name, style={"textAlign": "left"}),
        dbc.Input(
            type="number", id=id_name,
            min=min_val, max=max_val, step=step,
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
    assert match is not None, "RGB to HEX error"

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
    assert match is not None, "HEX to RGB error"

    rgb_code = "rgb({}, {}, {})".format(
        int(hex_string[1:3], 16),
        int(hex_string[3:5], 16),
        int(hex_string[5:7], 16)
    )
    return rgb_code


def make_heatmap(
        dataframe: pd.DataFrame, dataframe_accessor: str,
        title: str, goal: str, color: str) -> tuple[go.Figure, str]:
    """
    Makes a yealy heatmap using the provided arguments.
    The arguments are lists for multiple graphs support.

    Args:
        data (pd.DataFrame): Data used for the heatmap.
        dataframe_accessor (str): Column name.
        title (str): Name of the graph.
        goal (str): Goal variable from config file.
        color (str): Color for the heatmap

    Returns:
        go.Figure: Heatmap graph.
        str: Full title.
    """
    cfg = load_config()
    data = dataframe[dataframe_accessor].values
    base = [cfg["HEATMAP_BASE_COLOR"], cfg["HEATMAP_BASE_COLOR"]]
    assert len(data) == 364, "Heatmap data not in correct format error"

    if dataframe_accessor != "Personal":
        values = [[
            1 if data[day_index] >= cfg[goal]
            else 0
            for day_index in range(week * 7, (1 + week) * 7)
        ] for week in range(52)]
    else:
        work_data = dataframe["Work"].values
        values = [[
            1 if data[day_index] >= max(
                cfg[goal],
                work_data[day_index] * cfg["WORK_TO_PERSONAL_MULTIPLIER"]
            )
            else 0
            for day_index in range(week * 7, (1 + week) * 7)
        ] for week in range(52)]
    values = list(map(list, zip(*values)))

    fig = go.Figure(data=go.Heatmap(
        z=values, x=list(range(1, 53)), y=list(range(1, 7)),
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
    full_title = f"{title} {cfg[goal]}h"
    return fig, full_title


def make_crown() -> dbc.Row:
    """
    Makes a row of three crowns representing objective completion trends.

    Returns:
        dbc.Row: Crown row.
    """
    cfg = load_config()
    streaks = [0, 0, 0]
    breaks = get_break_days()
    goals = [
        cfg["WORK_TO_PERSONAL_MULTIPLIER"],
        cfg["PERSONAL_DAILY_GOAL"],
        cfg["SMALL_WORK_DAILY_GOAL"],
        cfg["WORK_DAILY_GOAL"]
    ]

    # Get goals met for today
    today = load_day_total(364)
    streaks[2] += 1 if today.loc[0, "Work"] >= goals[3] else 0
    streaks[1] += 1 if today.loc[0, "Work"] >= goals[2] else 0
    streaks[0] += 1 if today.loc[0, "Personal"] <= max(
        goals[1], today.loc[0, "Work"] * goals[0]
    ) else 0

    # Get goals streak for previous days
    is_not_done = [True, True, True]
    for day in range(363, 0, -1):
        day_break = breaks.loc[breaks["difference"] == 364 - day]
        day_break = 0 if day_break.empty else day_break.iloc[0, 1]
        values = load_day_total(day)
        work = values.loc[0, "Work"]
        work_with_break = work - day_break
        personal = values.loc[0, "Personal"]

        # Full work goal
        if is_not_done[2] and work >= goals[3]:
            if work_with_break >= goals[3]:
                streaks[2] += 1
        else:
            is_not_done[2] = False

        # Small work goal
        if is_not_done[1] and work >= goals[2]:
            if work_with_break >= goals[2]:
                streaks[1] += 1
        else:
            is_not_done[1] = False

        # Personal goal
        if is_not_done[0] and personal <= max(goals[1], work * goals[0]):
            if personal <= max(goals[1], work_with_break * goals[0]):
                streaks[0] += 1
        else:
            is_not_done[0] = False

        if set(is_not_done) == {False}:
            break

    # Determine which crown to give
    crowns = [
        "crown_enchanted_gold.gif",
        "crown_gold.png",
        "crown_red.png",
        "crown_silver.png",
        "crown_bronze.png",
        "crown_black.png"
    ]
    thresholds = [
        cfg["ENCHANTED_GOLD_STREAK_VALUE"],
        cfg["GOLD_STREAK_VALUE"],
        cfg["RED_STREAK_VALUE"],
        cfg["SILVER_STREAK_VALUE"],
        cfg["BRONZE_STREAK_VALUE"],
        0
    ]
    assets = [next(
        result for threshold, result
        in zip(thresholds, crowns)
        if value >= threshold
    ) for value in streaks]

    # Return row
    return dbc.Row([
        dbc.Col([
            html.Img(
                src=f"/assets/{assets[0]}",
                height="30px",
                width="30px",
                title="Personal daily goal streak"
            ),
            html.H5(streaks[0])
        ], class_name="g-0", style={
            'margin-right': '15px', 'margin-bottom': '0px'}),
        dbc.Col([
            html.Img(
                src=f"/assets/{assets[1]}",
                height="30px",
                width="30px",
                title="Small work daily goal streak"
            ),
            html.H5(streaks[1])
        ], class_name="g-0", style={
            'margin-right': '15px', 'margin-bottom': '0px'}),
        dbc.Col([
            html.Img(
                src=f"/assets/{assets[2]}",
                height="30px",
                width="30px",
                title="Work daily goal streak"
            ),
            html.H5(streaks[2])
        ], class_name="g-0", style={'margin-bottom': '0px'})
    ], class_name="g-0")


def make_totals_graph(graph_data: pd.DataFrame):
    """
    Makes the totals graph for the main page.

    Args:
        data (pd.DataFrame): Daily totals dataframe.

    Returns:
        _type_: Graph.
    """
    cfg = load_config()

    # Scale personal bar by work to personal multiplier
    data = graph_data.copy()
    personal = "Personal, scaled down by " + \
        f"{cfg['WORK_TO_PERSONAL_MULTIPLIER']}x"
    data.loc[1, "category"] = personal
    data.loc[1, "total"] /= 2

    fig = px.bar(
        data, x='category', y='total',
        category_orders={'category': ['Work', personal, 'Neutral']}
    )

    fig.update_traces(marker_color=[
        cfg["NEUTRAL_COLOR"], cfg["PERSONAL_COLOR"], cfg["WORK_COLOR"]])
    fig.update_layout(
        plot_bgcolor=cfg['CARD_COLOR'],
        paper_bgcolor=cfg['CARD_COLOR'],
        font_color=cfg['TEXT_COLOR'],
        height=cfg['CATEGORY_HEIGHT'],
        legend_title_text="",
        title="",
        title_font_color=cfg['TEXT_COLOR'],
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
    )
    fig.update_xaxes(
        title=None,
        showgrid=False
    )
    fig.update_yaxes(
        title=None,
        showgrid=False,
        showticklabels=False
    )

    # Anotate bars
    data.loc[1, "total"] *= 2
    sum_annotations = [{
        'x': xi,
        'y': (0.5 if xi == personal else 1) * yi + (data['total'].max() / 9),
        'text': f"{yi:.2f} hour" + (
            "s" if yi >= 1 else "") + f" / {round(yi/16*100, 1)}% of the day",
        'xanchor': 'center',
        'yanchor': 'top',
        'showarrow': False,
        'font': {
            'color': cfg['TEXT_COLOR'],
            'size': cfg['CATEGORY_FONT_SIZE']
        }
    } for xi, yi in zip(data['category'], data['total'])]
    fig.update_layout(annotations=sum_annotations)
    return fig


def make_info_row(data: pd.DataFrame) -> dbc.Col:
    """
    Makes the top info row of the main page.

    Args:
        data (pd.DataFrame): Daily progress data.

    Returns:
        dbc.Col: Info row column.
    """
    cfg = load_config()
    work = data.loc[data['category'] == 'Work', 'total'].values[0]
    work_goal = cfg['WORK_DAILY_GOAL']

    # Make first row
    first_row = "Work: "
    if work >= work_goal:
        first_row += "Done!"
    else:
        first_row += f"{int((work_goal - work) * 60)} min left"

    personal = data.loc[data['category'] == 'Personal', 'total'].values[0]
    first_row += ", Personal: "
    personal_goal = cfg['PERSONAL_DAILY_GOAL']
    work_multiplied = cfg['WORK_TO_PERSONAL_MULTIPLIER'] * work
    if work_multiplied > personal_goal:
        personal_goal = work_multiplied
    if personal >= personal_goal:
        first_row += "Over limit!"
    else:
        first_row += f"{int((personal_goal - personal) * 60)} min left"

    # Make second row
    second_row = datetime.datetime.now().strftime('%B %d, %A, %H:%M')
    thresholds = [
        work_goal * 0.25, work_goal * 0.50,
        work_goal * 0.75, work_goal]
    if work >= work_goal:
        second_row += ", 💯: Done!"
    else:
        objetive = next(
            (result, threshold) for threshold, result
            in zip(thresholds, ["¼", "½", "¾", "💯"])
            if work <= threshold)
        second_row += f", {objetive[0]}: {round(objetive[1], 2)}h"

    column = dbc.Col([
        dbc.Row(html.H4(first_row)),
        dbc.Row(html.H4(second_row))
    ], style={'padding': '0px'})
    return column


def make_trend_graph() -> dbc.Col:
    """
    Makes trend graphs for trends page.

    Returns:
        dbc.Col: Column of graphs.
    """
    cfg = load_config()
    row = []
    totals = load_dataframe("totals")
    colors = [cfg["WORK_COLOR"], cfg["PERSONAL_COLOR"]]
    types = ["Work", "Personal"]
    intervals = [30, 90, 364]
    style = {
        'margin-left': f"{cfg['SIDE_PADDING']}px",
        'margin-right': f"{cfg['SIDE_PADDING']}px",
        'margin-bottom': f"{cfg['DIVISION_PADDING']}px"
    }
    for selected, color in zip(types, colors):
        for interval in intervals:
            fig = px.bar(
                totals.iloc[-interval:, :],
                x="rowid",
                y=selected,
                labels={"rowid": "day"},
                color_discrete_sequence=[color]
            )
            fig.update_layout(
                plot_bgcolor=cfg['CARD_COLOR'],
                paper_bgcolor=cfg['CARD_COLOR'],
                font_color=cfg['TEXT_COLOR'],
                height=cfg['CATEGORY_HEIGHT'],
                title="",
                margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
            )
            row.append(dbc.Row([
                html.H3(f"{selected} {interval}-day trend"),
                dcc.Graph(figure=fig)
            ], style=style))
        row.append(html.Br())
    return dbc.Col(row)
