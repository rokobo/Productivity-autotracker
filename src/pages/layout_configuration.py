"""Page that shows the raw category database."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
import os
import sys
from ruamel.yaml import YAML
from dash import html, callback, Output, Input, State, dcc, callback_context
import dash_bootstrap_components as dbc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_io import load_config
from helper_server import make_colorpicker, make_valuepicker, \
    rgb_to_hex, hex_to_rgb

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("Configuration page"), width='auto'),
        dbc.Col([
            dbc.Col(
                dbc.Button(
                    "Refresh values",
                    id="refresh-button",
                    color="info", outline=True
                ), width='auto'
            ),
            dbc.Tooltip(
                "Refresh the 'saved value is' row with the contents of \
                    the current config file.",
                target="refresh-button", placement="bottom"),
            dbc.Col(
                dbc.Button(
                    "Set values",
                    id="set-button",
                    color="info", outline=True
                ), width='auto'
            ),
            dbc.Tooltip(
                "Set the values of the input cells with the contents of \
                    the current config file. DESCTRUCTIVE!",
                target="set-button", placement="bottom"),
            dbc.Col(
                dbc.Button(
                    "Save config",
                    id="save-button",
                    color="danger", outline=True
                ), width='auto'
            ),
            dbc.Tooltip(
                "Save the values in this page to the current \
                    config file. DESCTRUCTIVE!",
                target="save-button", placement="bottom"),
            dcc.Interval(
                id='check_interval',
                interval=1 * 1000,
                n_intervals=-1
            )
        ], className="d-grid gap-2 d-md-flex justify-content-md-end")
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row(html.H2('Goal variables (hours)')),
    dbc.Row([
        dbc.Row([
            make_valuepicker("WORK_DAILY_GOAL", 0, 24, 0.1),
            make_valuepicker("SMALL_WORK_DAILY_GOAL", 0, 24, 0.1),
            make_valuepicker("PERSONAL_DAILY_GOAL", 0, 24, 0.1)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("WORK_TO_PERSONAL_MULTIPLIER", 0, 48, 0.1),
            make_valuepicker("BRONZE_STREAK_VALUE", 1, 100, 0.1),
            make_valuepicker("SILVER_STREAK_VALUE", 1, 100, 0.1)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("RED_STREAK_VALUE", 1, 100, 0.1),
            make_valuepicker("GOLD_STREAK_VALUE", 1, 100, 0.1),
            make_valuepicker("ENCHANTED_GOLD_STREAK_VALUE", 1, 100, 0.1)
        ], className="g-0"),
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row(html.H2('Time variables (seconds)')),
    dbc.Row([
        dbc.Row([
            make_valuepicker("IDLE_TIME", 15, 3600),
            make_valuepicker("IDLE_CHECK_INTERVAL", 1, 60),
            make_valuepicker("ACTIVITY_CHECK_INTERVAL", 1, 10)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("MINIMUM_ACTIVITY_TIME", 1, 1800),
            make_valuepicker("UNRESPONSIVE_THRESHOLD", 3, 30),
            make_valuepicker("RETRY_ATTEMPS", 1, 25)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("GMT_OFFSET", -12, 12),
            make_valuepicker("ADVISOR_CHECK_INTERVAL", 1, 60),
            make_valuepicker("BACKUP_INTERVAL", 1, 3600),
        ], className="g-0"),
        dbc.Tooltip(
            "This interval is in minutes.",
            target="BACKUP_INTERVAL", placement="bottom"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("NUMBER_OF_BACKUPS", 1, 100),
            make_valuepicker("PARTIAL_CATEGORIES_INTERVAL", 1, 60),
            dbc.Col()
        ], className="g-0"),
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row(html.H2('Size variables (pixels)')),
    dbc.Row([
        dbc.Row([
            make_valuepicker("CATEGORY_HEIGHT", 100, 500),
            make_valuepicker("CATEGORY_FONT_SIZE", 1, 50),
            make_valuepicker("TROUBLESHOOTING_HEIGHT", 100, 2000)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("DIVISION_PADDING", 1, 50),
            make_valuepicker("SIDE_PADDING", 1, 50),
            make_valuepicker("CARD_PADDING", 1, 10)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("GOALS_HEATMAP_HEIGHT", 50, 250),
            make_valuepicker("GOALS_HEATMAP_GAP", 1, 15),
            make_valuepicker("GOALS_HEATMAP_DIVISION", 5, 100)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker("CATEGORY_CARD_MARGIN", 1, 20),
            make_valuepicker("CATEGORY_COLUMN_SPACE", 1, 100),
            dbc.Col()
        ], className="g-0")
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row(html.H2('Color variables')),
    dbc.Row([
        dbc.Row([
            make_colorpicker('WORK_COLOR'),
            make_colorpicker('PERSONAL_COLOR'),
            make_colorpicker('NEUTRAL_COLOR'),
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_colorpicker('TEXT_COLOR'),
            make_colorpicker('CARD_COLOR'),
            make_colorpicker('BACKGROUND'),
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_colorpicker('HEATMAP_GOOD_COLOR'),
            make_colorpicker('HEATMAP_OKAY_COLOR'),
            make_colorpicker('HEATMAP_BAD_COLOR'),
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_colorpicker('HEATMAP_BASE_COLOR'),
            make_colorpicker('CATEGORY_CARD_PERCENTAGE_COLOR'),
            make_colorpicker('CARD_OUTLINE_COLOR'),
        ], className="g-0")
    ], style=CFG["SECTION_STYLE"]),
])


vars1 = [
    "WORK_DAILY_GOAL", "SMALL_WORK_DAILY_GOAL", "PERSONAL_DAILY_GOAL",
    "WORK_TO_PERSONAL_MULTIPLIER", "BRONZE_STREAK_VALUE", "SILVER_STREAK_VALUE",
    "RED_STREAK_VALUE", "GOLD_STREAK_VALUE", "ENCHANTED_GOLD_STREAK_VALUE",
    "IDLE_TIME", "IDLE_CHECK_INTERVAL", "ACTIVITY_CHECK_INTERVAL",
    "MINIMUM_ACTIVITY_TIME", "UNRESPONSIVE_THRESHOLD", "RETRY_ATTEMPS",
    "GMT_OFFSET", "ADVISOR_CHECK_INTERVAL", "BACKUP_INTERVAL",
    "NUMBER_OF_BACKUPS", "PARTIAL_CATEGORIES_INTERVAL",
    "CATEGORY_HEIGHT", "CATEGORY_FONT_SIZE", "TROUBLESHOOTING_HEIGHT",
    "DIVISION_PADDING", "SIDE_PADDING", "CARD_PADDING",
    "GOALS_HEATMAP_HEIGHT", "GOALS_HEATMAP_GAP", "GOALS_HEATMAP_DIVISION",
    "CATEGORY_CARD_MARGIN", "CATEGORY_COLUMN_SPACE"
]
vars2 = [
    "WORK_COLOR", "PERSONAL_COLOR", "NEUTRAL_COLOR",
    "TEXT_COLOR", "CARD_COLOR", "BACKGROUND",
    "HEATMAP_OKAY_COLOR", "HEATMAP_GOOD_COLOR", "HEATMAP_BAD_COLOR",
    "HEATMAP_BASE_COLOR", "CATEGORY_CARD_PERCENTAGE_COLOR", "CARD_OUTLINE_COLOR"
]

@callback(
    [Output(f'saved-{name}', 'children') for name in vars1 + vars2],
    Input('refresh-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
)
def update_saved_values(_1, _2):
    """Updates the saved values using the config file."""
    global CFG
    CFG = load_config()
    return [CFG[var] for var in vars1 + vars2]


@callback(
    [Output(name, 'value') for name in vars1 + vars2],
    Input('set-button', 'n_clicks'),
)
def update_display_values(_1):
    """Updates the display values using the config file."""
    global CFG
    CFG = load_config()
    return_value = [CFG[var] for var in vars1]
    return_value += [rgb_to_hex(CFG[var]) for var in vars2]
    return return_value


@callback(
    [Output(name, 'invalid') for name in vars1 + vars2],
    Output('save-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
    Input('check_interval', 'n_intervals'),
    [State(name, 'value') for name in vars1 + vars2],
    prevent_initial_call=True
)
def change_config(n_clicks, _2, *args):
    """Update invalid status or change config file."""
    global CFG
    CFG = load_config()
    invalid = [value is None for value in args]
    ctx = callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx == 'check_interval':
        return invalid + [n_clicks]

    if any(invalid):
        print("\033[93mInvalid data in configuration page\033[00m")
        sys.exit()

    yaml = YAML()
    yaml.indent(mapping=4, sequence=2, offset=2)
    yaml.preserve_quotes = True
    yaml.explicit_end = True

    path = os.path.join(CFG["WORKSPACE"], 'config/config.yml')
    with open(path, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    index = len(vars1)
    for arg, name in zip(args[:index], vars1):
        if arg is None:
            print("\033[93mInvalid data in configuration page\033[00m")
            sys.exit()
        data[name] = arg

    for arg, name in zip(args[index:], vars2):
        if arg is None:
            print("\033[93mInvalid data in configuration page\033[00m")
            sys.exit()
        data[name] = hex_to_rgb(arg)

    with open(path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)
    return invalid + [n_clicks]
