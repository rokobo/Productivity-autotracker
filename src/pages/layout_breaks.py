"""Page that shows break days configuration."""
# pylint: disable=wrong-import-position, import-error
# flake8: noqa: F402
import os
import sys
from datetime import datetime, timedelta
from dash import html, callback, Output, Input, State, dcc, callback_context
import dash_bootstrap_components as dbc
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_io import load_config, append_to_database, load_dataframe, \
    check_dataframe, save_dataframe, delete_from_dataframe


CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H3("Breaks page"), width='auto')
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dbc.Col(html.H2("Define and modify break days"), width=6),
        dbc.Col(dcc.DatePickerSingle(
            id="break-picker",
            min_date_allowed=datetime.now() - timedelta(days=363),
            initial_visible_month=datetime.now(),
            display_format='YYYY/MM/DD',
        ), width=2),
        dbc.Col(dbc.Button(
            "Add break day",
            id="break-button",
            color="info", outline=True,
            style={'width': '100%'}
        ), width=2),
        dbc.Col(dbc.Button(
            "Save config",
            id="save-button",
            color="danger", outline=True,
            style={'width': '100%'}
        ), width=2)
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        html.H5("The breaks will remain stored until the break day passes, \
                at which point the break event will be added.")
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        html.Hr(),
        dbc.Checklist(
            id='checklist-breaks',
            style={'font-size': '20px', 'columns': '4'},
            switch=True
        )
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Tooltip(
        "Adds new break day to configuration.",
        target='break-button', placement="bottom"
    ),
    dbc.Tooltip(
        "Saves current configuration (You can delete days in the checklist).",
        target='save-button', placement="bottom"
    )
])


@callback(
    Output('checklist-breaks', 'options'),
    Output('checklist-breaks', 'value'),
    Output("break-picker", "date"),
    Input('break-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
    State("break-picker", "date"),
    State("checklist-breaks", "value"),
    State("checklist-breaks", "options"))
def define_breaks(_1, _2, date, values, options):
    """Updates checklist and breaks database."""
    if not check_dataframe("breaks"):
        save_dataframe(pd.DataFrame({"day": []}), "breaks")
    ctx = callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx != "save-button":
        if date is not None:
            if date not in load_dataframe("breaks", True)["day"].to_list():
                append_to_database("breaks", pd.DataFrame({"day": [date]}))
        break_days = load_dataframe("breaks", True)["day"].to_list()
        return break_days, break_days, None

    # Save button
    to_delete = list(set(options) - set(values))
    delete_from_dataframe("breaks", "day", to_delete)
    break_days = load_dataframe("breaks", True)["day"].to_list()
    return break_days, break_days, date
