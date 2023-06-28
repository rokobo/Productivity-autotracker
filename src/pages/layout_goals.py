"""Page that shows your goals."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
import os
import sys
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_io import load_config, load_dataframe
from helper_server import make_heatmap

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H3("Goals tracking"), width='auto'),
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row(id='goals_heatmap'),
    dcc.Interval(
        id='idle_interval',
        interval=30 * 1000,
        n_intervals=-1
    ),
])


@callback(
    Output('goals_heatmap', 'children'),
    Output('goals_heatmap', 'style'),
    Input('idle_interval', 'n_intervals')
)
def update_category(_1):
    """Makes total time by category graph."""
    global CFG
    CFG = load_config()

    totals = load_dataframe("totals")

    row = []
    row.append(make_heatmap(
        totals["Work"].values,
        "Daily study goal tracker",
        "WORK_DAILY_GOAL",
        CFG["HEATMAP_GOOD_COLOR"]))
    row.append(make_heatmap(
        totals["Personal"].values,
        "Daily personal goal tracker",
        "PERSONAL_DAILY_GOAL",
        CFG["HEATMAP_BAD_COLOR"]))
    row.append(make_heatmap(
        totals["Work"].values,
        "Daily study consistency tracker",
        "SMALL_WORK_DAILY_GOAL",
        CFG["HEATMAP_GOOD_COLOR"]))

    style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    }
    return row, style
