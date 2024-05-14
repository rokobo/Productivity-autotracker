"""Page that shows line graph of user data trends."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
import sys
from os.path import dirname, abspath
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

sys.path.append(dirname(dirname(abspath(__file__))))
sys.path.append(dirname(abspath(__file__)))

import layout_menu
from helper_io import load_config
from helper_server import make_trend_graphs

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("User trends"), width='auto'),
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row(id='trend_graphs'),
    dcc.Interval(
        id='idle_interval',
        interval=30 * 1000,
        n_intervals=-1
    ),
])


@callback(
    Output('trend_graphs', 'children'),
    Output('trend_graphs', 'style'),
    Input('idle_interval', 'n_intervals')
)
def update_category(_1):
    """Makes total time by category graph."""
    return make_trend_graphs(), {'padding': '0px'}
