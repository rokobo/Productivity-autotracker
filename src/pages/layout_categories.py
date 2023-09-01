"""Page that shows the raw category database."""
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
        dbc.Col(id='categories_update_time'),
        dbc.Col(id='categories_data'),
        dbc.Col(
            html.Button(
                "Update table", id='categories_refresh_button',
                style={
                    'width': '65%', 'border-radius': '4px',
                    'background-color': CFG['BACKGROUND'],
                    'margin-top': '5px', 'color': CFG['TEXT_COLOR']
                }
            ),
        )
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dcc.Graph(id='categories_table', style={'width': '100%'})
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    })
])


@callback(
    Output('categories_table', 'figure'),
    Output('categories_update_time', 'children'),
    Output('categories_data', 'children'),
    Input('categories_refresh_button', 'n_clicks'))
def update_categories(_1):
    """Makes categories graph."""
    global CFG
    CFG = load_config()
    dataframe = load_dataframe('categories')

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
    info += f'Columns: {dataframe.shape[1]}'
    return fig, html.H3(title), html.H4(info)
