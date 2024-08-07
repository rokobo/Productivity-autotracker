"""Dashboard page."""
# pylint: disable=wrong-import-position, import-error, global-statement
# pylint: disable=ungrouped-imports
# flake8: noqa: E402
import os
import sys
import time
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_server import generate_cards, make_crown, \
    make_totals_graph, make_info_row, make_heatmap
from helper_io import save_dataframe, load_dataframe, \
    load_config, set_idle, load_latest_row, load_day_total

CFG = load_config()


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Dashboard"),
            layout_menu.layout,
        ], width='auto'),
        dbc.Col(id="goals_title", width='auto'),
        dcc.Interval(id='title_interval', interval=1000, n_intervals=-1),
        dbc.Col(id="streak_crowns", width='auto'),
        dbc.Col(
            dbc.Button([
                    dbc.Spinner(html.Div(id="idle_loading"), size="sm"),
                    "Set idle"
                ],
                id="set_idle_button",
                color="warning", outline=True
            ), class_name="d-md-flex justify-content-md-end"
        ),
        dbc.Tooltip(
                "Sets your state to idle. \
                    Just press the button and stop moving your mouse.",
                target='set_idle_button', placement="bottom"
        ),
    ], style=CFG["SECTION_STYLE"]),
    dcc.Interval(id='heatmap_interval', interval=30000, n_intervals=-1),
    dbc.Row(id='heatmap_row'),
    dcc.Interval(id='category_interval', interval=15000, n_intervals=-1),
    dbc.Row(id='category_row'),
    dcc.Interval(
        id='activity_check_interval',
        interval=CFG["ACTIVITY_CHECK_INTERVAL"] * 1000,
        n_intervals=-1
    ),
    dbc.Row(id='categorized_list'),
    html.Div(
        html.H1("User is currently idle", id='idle_warning_style', style={}),
        id='idle_warning', className=''
    )
])


@callback(
    Output('goals_title', 'children'),
    Input('title_interval', 'n_intervals')
)
def update_title(_1):
    """Updates title."""
    global CFG
    CFG = load_config()
    data = load_day_total(0).transpose()
    data.reset_index(inplace=True)
    data.rename(columns={
        'index': 'category', data.columns[1]: 'total'
    }, inplace=True)
    return make_info_row()

@callback(
    Output('category_row', 'children'),
    Output('category_row', 'style'),
    Output('streak_crowns', 'children'),
    Input('category_interval', 'n_intervals')
)
def update_category(_1):
    """Makes total time by category graph."""
    global CFG
    CFG = load_config()

    # Main categories graph
    data = load_day_total(0).transpose()
    data.reset_index(inplace=True)
    data.rename(columns={
        'index': 'category', data.columns[1]: 'total'
    }, inplace=True)

    fig = make_totals_graph(data)
    if fig is None:
        raise PreventUpdate

    crowns = make_crown()
    if crowns is None:
        raise PreventUpdate

    card_style = {
        'background-color': CFG['CARD_COLOR'],
        'border': f'1px solid {CFG["CARD_OUTLINE_COLOR"]}'
    }
    cardbody_style = {'padding': f'{CFG["CARD_PADDING"]}px'}

    card = dbc.Card([dbc.CardBody([
        dcc.Graph(figure=fig, config={'displayModeBar': False}),
    ], style=cardbody_style)], style=card_style)
    return card, CFG["SECTION_STYLE"], crowns


@callback(
    Output('heatmap_row', 'children'),
    Output('heatmap_row', 'style'),
    Input('heatmap_interval', 'n_intervals')
)
def update_heatmap_graph(_1):
    """Makes heatmap graph."""
    global CFG
    CFG = load_config()

    fig = make_heatmap()
    if fig is None:
        raise PreventUpdate

    card_style = {
        'margin-left': "0px",
        'margin-right': "0px",
    }
    style = {
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }
    return dbc.Row(
        dcc.Graph(figure=fig, config={'displayModeBar': False}),
        style=card_style
    ), style


@callback(
    Output('categorized_list', 'children'),
    Output('categorized_list', 'style'),
    Input('activity_check_interval', 'n_intervals'),
    prevent_initial_call=True
)
def update_element_list(_1):
    """Generates the event cards."""
    dataframe = load_dataframe('activity', False, 'categories_partial')
    dataframe = dataframe[
        dataframe['day'] == str(pd.to_datetime('today').date())]
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'frontend')
    cards = generate_cards(dataframe)
    return cards, CFG["SECTION_STYLE"]


@callback(
    Output('idle_warning', 'className'),
    Output('idle_warning_style', 'style'),
    Input('activity_check_interval', 'n_intervals')
)
def update_info_row(_1):
    """Updates idle modal."""
    last_row = load_latest_row('activity')
    idle = last_row.loc[0, "process_name"] == "IDLE TIME"
    if idle:
        return 'blinking-warning', {'opacity': 0.5}
    return '', {'opacity': 0, 'pointer-events': 'none'}


@callback(
    Output('idle_loading', 'children'),
    Input('set_idle_button', 'n_clicks'),
    prevent_initial_call=True
)
def set_idle_button(_1):
    """Sets all input databases to idle state."""
    # Ensure idle is set (late mouse thread can revert this sometimes)
    time.sleep(3)
    set_idle()
    time.sleep(0.5)
    set_idle()
    time.sleep(0.5)
    set_idle()
    # Loading animation has a delay
    time.sleep(0.5)
    return ""
