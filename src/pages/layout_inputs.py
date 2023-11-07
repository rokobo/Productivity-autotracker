"""Page that shows the raw input databases."""
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
        dbc.Col(id='inputs_update_time'),
        dbc.Col(
            html.Button(
                "Update table", id='inputs_refresh_button',
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
        html.Div(id='input_tables')
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px"
    })
])


def create_table(name: str) -> go.Table:
    """
    Creates table for inputs.

    Args:
        name (str): Name of database.

    Returns:
        go.Table: Input table from transposed database.
    """
    dataframe = load_dataframe(name)
    dataframe = dataframe.T

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
        height=50,
        margin={'b': 0, 't': 0, 'l': 0, 'r': 0}
    )
    return fig


@callback(
    Output('input_tables', 'children'),
    Output('inputs_update_time', 'children'),
    Input('inputs_refresh_button', 'n_clicks'))
def update_inputs(_1):
    """Makes input graph."""
    global CFG
    CFG = load_config()
    inputs = ['backend', 'frontend', 'mouse', 'keyboard', 'audio']
    rows = []
    for database1, database2 in zip(inputs[::2], inputs[1::2]):
        table1 = create_table(database1)
        table2 = create_table(database2)
        rows.append(dbc.Row([
            dbc.Col([html.H3(database1), dcc.Graph(figure=table1)]),
            dbc.Col([html.H3(database2), dcc.Graph(figure=table2)])
        ]))

    if len(inputs) % 2 ==1:
        database3 = inputs[-1]
        table3 = create_table(database3)
        rows.append(dbc.Row([
            dbc.Col([html.H3(database3), dcc.Graph(figure=table3)]),
            dbc.Col([])
        ]))

    title = f'Last update: {datetime.now().strftime("%H:%M:%S")}'
    return dbc.Row(rows), html.H2(title)
