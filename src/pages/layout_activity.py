"""Page that shows the raw activity database."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
import os
import sys
from datetime import datetime
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import layout_menu

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_io import load_dataframe, load_config

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(id='activity_update_time'),
        dbc.Col(id='activity_data'),
        dbc.Col(
            html.Button(
                "Update table", id='activity_refresh_button',
                style={
                    'width': '100%', 'border-radius': '4px',
                    'background-color': CFG['CARD_COLOR'],
                    'margin-top': '5px', 'color': CFG['TEXT_COLOR']
                }
            ), width=2
        )
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dcc.Graph(id='activity_table', style={'width': '100%'})
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    })
])


@callback(
    Output('activity_table', 'figure'),
    Output('activity_update_time', 'children'),
    Output('activity_data', 'children'),
    Input('activity_refresh_button', 'n_clicks'))
def update_activity(_1):
    """Makes activity graph."""
    global CFG
    CFG = load_config()
    dataframe = load_dataframe('activity')
    dataframe = dataframe.iloc[::-1]

    table = go.Table(
        header={
            'values': dataframe.columns
        },
        cells={
            'values': [dataframe[col] for col in dataframe.columns],
        }
    )

    fig = go.Figure(data=table)
    fig.update_layout(
        height=CFG['TROUBLESHOOTING_HEIGHT'],
        margin={'b': 0, 't': 0, 'l': 0, 'r': 0}
    )
    title = f'Last update: {datetime.now().strftime("%H:%M:%S")}'
    info = f'Rows: {dataframe.shape[0]}, '
    info += f'Columns: {dataframe.shape[1]}, '
    info += f'Process_names: {dataframe["process_name"].nunique()}'
    return fig, html.H3(title), html.H4(info)
