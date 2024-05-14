"""Page that shows all events all."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: E402
from os.path import dirname, abspath
import sys
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
sys.path.append(dirname(abspath(__file__)))

import layout_menu
from helper_io import load_config, load_dataframe
from helper_server import generate_cards, format_long_duration

CFG = load_config()

layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("All events categorized"), width='auto'),
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row([
        dbc.Col(html.H3("Work")),
        dbc.Col(html.H3("Personal")),
        dbc.Col(html.H3("Neutral"))
    ]),
    dbc.Row(id='all_list', style=CFG["SECTION_STYLE"]),
    dcc.Interval(
        id='all_interval',
        interval=60 * 1000,
        n_intervals=-1
    ),
])


@callback(
    Output('all_list', 'children'),
    Input('all_interval', 'n_intervals'),
    # prevent_initial_call=True
)
def update_element_list(_1):
    """Generates the event cards."""
    dataframe = load_dataframe('activity', False, 'categories')
    dataframe = dataframe.groupby(
        ['process_name', 'subtitle', 'category', 'method']
    ).agg({'total': 'sum'}).reset_index()
    dataframe = dataframe.sort_values(by=['total'], ascending=False)
    dataframe.loc[:, 'duration'] = dataframe['total'] * 3600
    dataframe.loc[:, 'duration'] = dataframe['duration'].apply(
        format_long_duration)
    totals = pd.DataFrame(
        load_dataframe('activity', False, 'totals', False).sum(axis=0)
    ).transpose()
    cards = generate_cards(dataframe, totals)
    return cards
