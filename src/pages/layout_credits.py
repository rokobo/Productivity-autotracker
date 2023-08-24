"""Page that shows credits."""
# pylint: disable=import-error, wrong-import-position
# flake8: noqa: F401
import os
import sys
from dash import html
import dash_bootstrap_components as dbc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_io import load_config

CFG = load_config()
card_style = {
    'background-color': CFG['CARD_COLOR'],
    'border': '0px',
    'margin-bottom': f'{CFG["CATEGORY_CARD_MARGIN"]}px'
}


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H3("Credits and attributions"), width='auto'),
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.Row([
            dbc.Col(
                dbc.CardImg(
                    src="/assets/favicon.ico",
                    className="img-fluid rounded-start",
                ), className="col-md-4",
            ),
            dbc.Col(
                dbc.CardBody([
                    html.H4("Application favicon", className="card-title"),
                    html.P(
                        "Grow icons created by Freepik at\
                            https://www.flaticon.com/free-icons/grow",
                        className="card-text",
                    ),
                ]),
            ),], className="d-flex align-items-center",)
        ], style=card_style, className="mb-3")),

        dbc.Col(dbc.Card([dbc.Row([
            dbc.Col(
                dbc.CardImg(
                    src="/assets/sprout.png",
                    className="img-fluid rounded-start",
                ), className="col-md-4",
            ),
            dbc.Col(
                dbc.CardBody([
                    html.H4("Desktop notification icon", className="card-title"),
                    html.P(
                        "Sprout icons created by Freepik at\
                            https://www.flaticon.com/free-icons/sprout",
                        className="card-text",
                    ),
                ]),
            ),], className="d-flex align-items-center",)
        ], style=card_style, className="mb-3")),
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px"
    }),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.Row([
            dbc.Col(
                dbc.CardImg(
                    src="/assets/crown_gold.png",
                    className="img-fluid rounded-start",
                ), className="col-md-4",
            ),
            dbc.Col(
                dbc.CardBody([
                    html.H4("Dashboard goal streak icon", className="card-title"),
                    html.P(
                        "Crown icon by Icons8 at\
                            https://icons8.com/icon/13728/crown",
                        className="card-text",
                    ),
                ]),
            ),], className="d-flex align-items-center",)
        ], style=card_style, className="mb-3")),
        dbc.Col()
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px"
    })
])
