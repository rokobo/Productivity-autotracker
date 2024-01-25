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
from helper_server import make_credit

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("Credits and attributions"), width='auto'),
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        make_credit("favicon.ico", "Application favicon", (
            "Grow icons created by Freepik at "
            "https://www.flaticon.com/free-icons/grow")),
        make_credit("sprout.png", "Notification icon", (
            "Sprout icons created by Freepik at "
            "https://www.flaticon.com/free-icons/sprout"))
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px"
    }),
    dbc.Row([
        make_credit("crown_gold.png", "Goal streak icon", (
            "Crown icon by Icons8 at "
            "https://icons8.com/icon/13728/crown")),
        make_credit(None, "Application font", (
            "JetBrains font at "
            "https://github.com/JetBrains/JetBrainsMono")),
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px"
    })
])
