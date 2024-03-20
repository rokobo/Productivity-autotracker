"""
Collection of helper functions for website routines.
"""
# pylint: disable=consider-using-f-string, import-error
import sys
import re
import time
import datetime
from typing import Optional
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from helper_io import load_config, load_categories, load_day_total, \
    load_dataframe, load_input_time  # , retry


def generate_cards(df: pd.DataFrame, totals=None) -> Optional[list[dbc.Col]]:
    """
    Generates categorized list of activities in a given timeframe.

    Args:
        df (pd.DataFrame): Dataframe with categories.
        totals (pd.DataFrame): Total time of three categories for comparison.

    Returns:
        dbc.Row: Dash Row with categorized activities.
    """
    if totals is None:
        totals = load_day_total(0)
    if (totals is None) or totals.empty:
        return None
    cfg = load_config()
    card_list = [[], [], []]

    card_style = {
        'background-color': cfg['CARD_COLOR'],
        'border': f'1px solid {cfg["CARD_OUTLINE_COLOR"]}',
        'margin-bottom': f'{cfg["CATEGORY_CARD_MARGIN"]}px'
    }
    cardbody_style = {'padding': f'{cfg["CARD_PADDING"]}px'}

    for _, row in df.iterrows():
        if row['total'] < cfg['MINIMUM_ACTIVITY_TIME'] / 3600:
            continue
        category = row['category']
        cat_total = totals.loc[0, category]
        act_total = row["total"]
        assert isinstance(act_total, float)

        percentage1 = f'{round(act_total / 16 * 100, 1)}% day '
        percentage2 = 0 if cat_total == 0 \
            else f' {round(row["total"] / cat_total * 100, 1)}% total'
        percentage2 = percentage2 if row["process_name"] != "IDLE TIME" else ""

        item = dbc.Card([dbc.CardBody([
            dbc.Row([
                html.H4(f'{row["process_name"]} {row["method"]}'),
                html.H5(row['subtitle']) if row['subtitle'] != "" else None],
                className="g-0",
                align='center',
                style={"color": cfg["TEXT_COLOR"]}
            ),
            dbc.Row([
                dbc.Col(
                    html.H6(percentage1),
                    style={"color": cfg["CATEGORY_CARD_PERCENTAGE_COLOR"]},
                    width="auto"
                ),
                dbc.Col(
                    html.H6(row['duration']),
                    style={"color": cfg["TEXT_COLOR"]},
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
            card_list[0].append(item)
        elif category == "Personal":
            card_list[1].append(item)
        else:
            card_list[2].append(item)

    spacing = f'g-{cfg["CATEGORY_COLUMN_SPACE"]}'
    return [
        dbc.Col(card_list[0], class_name=spacing, width=4),
        dbc.Col(card_list[1], class_name=spacing, width=4),
        dbc.Col(card_list[2], class_name=spacing, width=4)
    ]


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
    t_parts = [seconds // 3600, (seconds % 3600) // 60, seconds % 60]
    t_units = [" hour", " min", " sec"] if long else ["h", "m", "s"]
    separator = ", " if long else " "
    string_parts = []

    for t_part, t_unit in zip(t_parts, t_units):
        if t_part == 0:
            continue
        string_parts.append(
            f"{int(t_part)}{t_unit}{'s' if t_part > 1 and long else ''}"
        )
    return separator.join(string_parts)


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
        html.H2(name),
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
    if match is None:
        print("\033[93mRGB to HEX error\033[00m")
        sys.exit()

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
    if match is None:
        print("\033[93mHEX to RGB error\033[00m")
        sys.exit()

    rgb_code = "rgb({}, {}, {})".format(
        int(hex_string[1:3], 16),
        int(hex_string[3:5], 16),
        int(hex_string[5:7], 16)
    )
    return rgb_code


def join_rgb(rgb1: str, rgb2: str) -> str:
    """
    Joins two rgb strings and returns the average color.

    Args:
        rgb1 (str): RGB string 1.
        rgb2 (str): RGB string 2.

    Returns:
        str: Average RGB string.
    """
    match1 = re.match(r'^rgb\(\d+,\s*\d+,\s*\d+\)$', rgb1)
    match2 = re.match(r'^rgb\(\d+,\s*\d+,\s*\d+\)$', rgb2)
    if match1 is None or match2 is None:
        print("\033[93mRGB join error\033[00m")
        sys.exit()

    values1 = re.findall(r'(\d+)', rgb1)
    values2 = re.findall(r'(\d+)', rgb2)
    rgb_code = "rgb({}, {}, {})".format(
        *[int((int(v1) + int(v2)) / 2) for v1, v2 in zip(values1, values2)]
    )
    return rgb_code


def make_heatmap() -> Optional[go.Figure]:
    """
    Makes a yealy heatmap with goals.

    Returns:
        go.Figure: Heatmap graph.
    """
    cfg = load_config()
    totals = load_dataframe("activity", False, "totals", False)
    if (totals is None) or totals.empty:
        return None
    fig = go.Figure()
    values = []
    hovertext = []

    for week in range(52):
        temp_values = []
        temp_hovertext = []
        for day in range(week * 7, (1 + week) * 7):
            work = totals.loc[day, "Work"]
            pers = totals.loc[day, "Personal"]

            if work > cfg["WORK_DAILY_GOAL"]:
                temp_values.append(4)
            elif (pers > cfg["PERSONAL_DAILY_GOAL"]) and (
                work * cfg["WORK_TO_PERSONAL_MULTIPLIER"]
                < max(cfg["PERSONAL_DAILY_GOAL"], pers)
            ):
                if work > cfg["SMALL_WORK_DAILY_GOAL"]:
                    temp_values.append(2)
                else:
                    temp_values.append(1)
            elif work > cfg["SMALL_WORK_DAILY_GOAL"]:
                temp_values.append(3)
            else:
                temp_values.append(0)

            temp_hovertext.append((
                f"{round(work, 2)} hours of work<br>"
                + f"{round(pers, 2)} hours of personal<br>"
                + f"Week {week + 1}, Day {day + 1}<br>"
                + ('Current week'
                    if week == 51
                    else (f'Happened {51-week}w ago'))
                + "<br>"
                + ('Current day'
                    if day == 363
                    else (f'Happened {363-day}d ago'))
            ))
        values.append(temp_values)
        hovertext.append(temp_hovertext)

    values = list(map(list, zip(*values)))
    hovertext = list(map(list, zip(*hovertext)))

    fig.add_trace(go.Heatmap(
        z=values, x=list(range(1, 52)), y=list(range(1, 7)),
        hoverinfo="text", text=hovertext,
        xgap=cfg["GOALS_HEATMAP_GAP"], ygap=cfg["GOALS_HEATMAP_GAP"],
        colorscale=[
            cfg["HEATMAP_BASE_COLOR"],
            cfg["HEATMAP_BAD_COLOR"],
            join_rgb(cfg["HEATMAP_BAD_COLOR"], cfg["HEATMAP_OKAY_COLOR"]),
            cfg["HEATMAP_OKAY_COLOR"],
            cfg["HEATMAP_GOOD_COLOR"]],
        showlegend=False, showscale=False
    ))

    for week in [1, 4, 12, 26, 52]:
        fig.add_vline(
            x=52.5-week, line_width=1, line_dash="dash", line_color="cyan")

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=cfg['TEXT_COLOR'],
        height=cfg['GOALS_HEATMAP_HEIGHT'],
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
    )
    fig.update_xaxes(
        side="top", title=None, showgrid=False,
        color=cfg['TEXT_COLOR'], tickmode='array',
        tickvals=[
            0.5, 5, 10, 15, 20, 26.5, 30, 35, 40.5, 45, 48.5, 51.5
        ],
        ticktext=[
            "1y", 5, 10, 15, 20, "6m", 30, 35, "3m", 45, "1m", "1w"
        ]
    )

    offset = int(totals.query('days_since == 0')["weekday_num"].iloc[0]) + 1
    row_ticks = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    row_ticks = row_ticks[offset:] + row_ticks[:offset]
    row_ticks[6] = "(" + row_ticks[6] + ")"
    fig.update_yaxes(
        side="right", title=None, showgrid=False,
        color=cfg['TEXT_COLOR'], tickmode='array',
        tickvals=list(range(1, 8)), ticktext=row_ticks
    )
    return fig


def make_crown() -> Optional[dbc.Row]:
    """
    Makes a row of three crowns representing work completion trends.

    Returns:
        dbc.Row: Crown row.
    """
    cfg = load_config()
    data = load_dataframe('activity', False, 'totals', False)
    if (data is None) or data.empty:
        return None
    weeks = [1, 4, 12, 26, 52]
    goal = cfg["WORK_DAILY_GOAL"]
    streaks0 = [
        round(data.loc[364 - (interval * 7):, "Work"].apply(
            lambda x: min(x, goal)).sum() / (interval * 7 * goal) * 100, 2)
        for interval in weeks
    ]
    streaks1 = [
        round((data.loc[364 - (interval * 7):, "Work"] >= goal).sum() /
              (interval * 7) * 100, 1)
        for interval in weeks
    ]
    streaks2 = [
        round((data.loc[364 - (interval * 7):, "Work"] >= cfg[
            "SMALL_WORK_DAILY_GOAL"]).sum() / (interval * 7) * 100, 1)
        for interval in weeks
    ]
    sums = [
        format_short_duration(
            3600 * data.loc[364 - (interval*7):, "Work"].sum() / (interval*7))
        for interval in weeks
    ]

    # Determine which crown to give
    crowns = [
        "crown_enchanted_gold.gif", "crown_gold.png",
        "crown_red.png", "crown_silver.png",
        "crown_bronze.png", "crown_black.png"
    ]
    thresholds = [
        cfg["ENCHANTED_GOLD_STREAK_VALUE"], cfg["GOLD_STREAK_VALUE"],
        cfg["RED_STREAK_VALUE"], cfg["SILVER_STREAK_VALUE"],
        cfg["BRONZE_STREAK_VALUE"], 0
    ]
    assets = [next(
        result for threshold, result
        in zip(thresholds, crowns)
        if value >= threshold
    ) for value in streaks0]

    row = dbc.Row([
        dbc.Col([
            html.Img(
                src=f"/assets/{asset}",
                height="35px",
                width="35px",
                title=(
                    f"{weeks[i]}-week work goal: "
                    f"{round(streaks1[i]*7*weeks[i]/100)} / {7*weeks[i]}"
                    f"\n{weeks[i]}-week small work goal: "
                    f"{round(streaks2[i]*7*weeks[i]/100)} / {7*weeks[i]}"
                    f"\n{weeks[i]}-week work average: {sums[i]}"
                )
            ),
            html.H5([f"{streaks0[i]}%"]),
        ], class_name="g-0 justify-content-md-end", style={
            'margin-right': '15px', 'margin-bottom': '0px'})
        for i, asset in enumerate(assets)
    ], class_name="g-0")
    return row


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
    max_val = data['total'].max()
    data.loc[1, "total"] *= 2
    sum_annotations = [{
        'x': xi,
        'y': (0.5 if xi == personal else 1) * yi + (max_val / 9),
        'text': f"{yi:.2f} hours / {round(yi/16*100, 1)}% of the day",
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


def make_info_row() -> Optional[dbc.Col]:
    """
    Makes the top info row of the main page.

    Returns:
        dbc.Col: Info row column.
    """
    cfg = load_config()
    data = load_day_total(0)
    if (data is None) or data.empty:
        return None
    work = data.loc[0, "Work"]
    work_goal = cfg['WORK_DAILY_GOAL']

    # Make first row
    first_row = "Work: "
    if work >= work_goal:
        first_row += "Done!"
    else:
        first_row += f"{int((work_goal - work) * 60)} min left"

    personal = data.loc[0, "Personal"]
    first_row += ", Personal: "
    person_goal = cfg['PERSONAL_DAILY_GOAL']
    person_goal = max(cfg['WORK_TO_PERSONAL_MULTIPLIER'] * work, person_goal)

    if personal >= person_goal:
        first_row += "Over limit!"
    else:
        first_row += f"{int((person_goal - personal) * 60)} min left"

    # Make second row
    second_row = datetime.datetime.now().strftime('%B %d, %A, %H:%M:%S')
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

    # Make third row
    now = int(time.time())
    last_input = now - max(
        load_input_time('mouse'),
        load_input_time('audio'),
        load_input_time('keyboard')
    )
    last_backend = now - load_input_time('backend')
    third_row = f"Last input: {last_input}s, Last backend: {last_backend}s"

    return dbc.Col([
        dbc.Row(html.H5(first_row)),
        dbc.Row(html.H5(second_row)),
        dbc.Row(html.H5(third_row))
    ], style={'padding': '0px'})


def make_trend_graphs() -> Optional[dbc.Col]:
    """
    Makes trend graphs for trends page.

    Returns:
        dbc.Col: Column of graphs.
    """
    cfg = load_config()
    row = []
    totals = load_dataframe('activity', False, 'totals', False)
    if (totals is None) or totals.empty:
        return None
    intervals = [364, 90, 30]

    figs = [go.Figure() for _ in range(4)]
    for title, ind1, acc in zip(
        ["total trends", "weekday trends"],
        range(0, 3, 2),
        ["day", "weekday"]
    ):
        for selected, color, ind2 in zip(
            ["Work", "Personal"],
            [cfg["WORK_COLOR"], cfg["PERSONAL_COLOR"]],
            range(2)
        ):
            fig = figs[ind1 + ind2]
            for interval in intervals[::-1]:
                _totals = totals.iloc[-interval:, :]
                if acc == "weekday":
                    _totals = _totals.groupby(['weekday', 'weekday_num']).agg(
                        {"Neutral": "sum", "Personal": "sum", "Work": "sum"}
                    ).reset_index().sort_values('weekday_num')
                    _totals["Work"] /= interval
                    _totals["Personal"] /= interval
                fig.add_trace(go.Bar(
                    x=_totals[acc], y=_totals[selected],
                    showlegend=False, marker_color=color
                ))

            row.append(dbc.Row([
                html.H2(f"{selected} {title}"),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ], style={
                'margin-left': f"{cfg['SIDE_PADDING']}px",
                'margin-right': f"{cfg['SIDE_PADDING']}px",
                'margin-bottom': f"{cfg['DIVISION_PADDING']}px"
            }))

    for fig in figs:
        fig.update_layout(
            plot_bgcolor=cfg['CARD_COLOR'],
            paper_bgcolor=cfg['CARD_COLOR'],
            font_color='rgb(180, 180, 180)',
            height=cfg['CATEGORY_HEIGHT'],
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            updatemenus=[{
                "type": "buttons", "direction": "down",
                "buttons": [{
                    "args": [{"visible": [j == i for j in range(2, -1, -1)]}],
                    "label": label,
                    "method": "update"
                } for i, label in zip(range(3), intervals)],
                "showactive": True, "xanchor": "right",
                "active": 0
            }]
        )
    return dbc.Col(row)


def make_credit(img_src: str, title: str, subtitle: str) -> dbc.Col:
    """
    Makes credit and attribution card.

    Args:
        img_src (str): Image source.
        title (str): Title of the card.
        subtitle (str): Subtitle of the card.

    Returns:
        dbc.Col: Card column.
    """
    cfg = load_config()
    card_style = {
        'background-color': cfg['CARD_COLOR'],
        'border': '0px',
        'margin-bottom': f'{cfg["CATEGORY_CARD_MARGIN"]}px',
        'color': cfg['TEXT_COLOR']
    }
    col = []
    if img_src is not None:
        col.append(dbc.Col(dbc.CardImg(
            src=f"assets/{img_src}",
            className="img-fluid rounded-start",
        ), className="col-md-4"))
    col.append(dbc.Col(dbc.CardBody([
        html.H4(title),
        html.H5(subtitle),
    ])))
    return dbc.Col(dbc.Card([dbc.Row(
        col, className="d-flex align-items-center"
    )], style=card_style, className="mb-3"))
