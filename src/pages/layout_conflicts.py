"""Page that shows the category matching conflicts."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
import os
import sys
from datetime import datetime
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import layout_menu

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_io import load_dataframe, load_config, load_categories

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(id='conflicts_update_time'),
        dbc.Col(id='conflicts_data'),
        dbc.Col(
            html.Button(
                "Update table", id='conflicts_refresh_button',
                style={
                    'width': '65%', 'border-radius': '4px',
                    'background-color': CFG['BACKGROUND'],
                    'margin-top': '5px', 'color': CFG['TEXT_COLOR']
                }
            ),
        )
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row([
        dcc.Graph(
            id='conflicts_table',
            style={'width': '100%'},
            config={'displayModeBar': False}
        )
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    })
])


@callback(
    Output('conflicts_table', 'figure'),
    Output('conflicts_update_time', 'children'),
    Output('conflicts_data', 'children'),
    Input('conflicts_refresh_button', 'n_clicks'))
def update_conflicts(_1):
    """Makes conflicts graph."""
    global CFG
    CFG = load_config()
    cfg2 = load_categories()
    activity = load_dataframe("activity")
    assert (activity is not None) and (not activity.empty)
    activity = activity.loc[:, ["process_name", "domain"]]
    activity['work_matches'] = activity['process_name'].str.extract(
        f'(?i)({"|".join(cfg2["WORK_APPS"])})', expand=False).combine(
            activity['domain'].str.extract(
        f'(?i)({"|".join(cfg2["WORK_DOMAINS"])})', expand=False),
            lambda x, y: f'{x}<br>{y}' if pd.notnull(y) or pd.notnull(x) else x
        )
    activity['personal_matches'] = activity['process_name'].str.extract(
        f'(?i)({"|".join(cfg2["PERSONAL_APPS"])})', expand=False).combine(
            activity['domain'].str.extract(
        f'(?i)({"|".join(cfg2["PERSONAL_DOMAINS"])})', expand=False),
            lambda x, y: f'{x}<br>{y}' if pd.notnull(y) or pd.notnull(x) else x
        )
    activity.dropna(inplace=True)

    table = go.Table(
        header={'values': activity.columns},
        cells={'values': [activity[col] for col in activity.columns]}
    )

    fig = go.Figure(data=table)
    fig.update_layout(
        height=CFG['TROUBLESHOOTING_HEIGHT'],
        margin={'b': 0, 't': 0, 'l': 0, 'r': 0}
    )
    title = f'Last update: {datetime.now().strftime("%H:%M:%S")}'
    info = f'{activity.shape[0]} conflict{"" if activity.shape[0] == 1 else "s"}'
    return fig, html.H2(title), html.H3(info)
