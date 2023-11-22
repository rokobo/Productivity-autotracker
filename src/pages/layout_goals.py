"""Page that shows your goals."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
from os.path import dirname, abspath
import sys
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

sys.path.append(dirname(dirname(abspath(__file__))))
sys.path.append(dirname(abspath(__file__)))

import layout_menu
from helper_io import load_config, load_dataframe
from helper_server import make_heatmap

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("Goals tracking"), width='auto'),
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

    totals = load_dataframe('activity', False, 'totals')

    fig1, title1 = make_heatmap(
        totals, "Work",
        "Work",
        "WORK_DAILY_GOAL",
        CFG["HEATMAP_GOOD_COLOR"])
    fig2, title2 = make_heatmap(
        totals, "Personal",
        "Personal",
        "PERSONAL_DAILY_GOAL",
        CFG["HEATMAP_BAD_COLOR"])
    fig3, title3 = make_heatmap(
        totals, "Work",
        "Consistency",
        "SMALL_WORK_DAILY_GOAL",
        CFG["HEATMAP_GOOD_COLOR"])

    style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    }
    c = {'displayModeBar': False}
    cards = dbc.Row([
        dbc.Row([
            html.H2(title1),
            dcc.Graph(figure=fig1, config=c)
        ], style=style),
        dbc.Row([
            html.H2(title2),
            html.H5(f"or work to personal override \
                    ({CFG['WORK_TO_PERSONAL_MULTIPLIER']}x multiplier)"),
            dcc.Graph(figure=fig2, config=c)
        ], style=style),
        dbc.Row([
            html.H2(title3),
            dcc.Graph(figure=fig3, config=c)
        ], style=style),
    ])
    return cards, {'padding': '0px'}
