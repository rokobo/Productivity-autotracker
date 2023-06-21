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
        dbc.Col(html.H3("Configuration page"), width='auto'),
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
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row(html.H3('Time variables')),
    dbc.Row([
        dbc.Row([
            make_valuepicker('idle-time', "IDLE_TIME", 15, 3600),
            make_valuepicker('idle-check-interval', "IDLE_CHECK_INTERVAL", 1, 60),
            make_valuepicker('activity-check-interval', "ACTIVITY_CHECK_INTERVAL", 1, 10)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker('minimum-activity-time', "MINIMUM_ACTIVITY_TIME", 1, 1800),
            make_valuepicker('unresponsive-threshold', "UNRESPONSIVE_THRESHOLD", 3, 30),
            make_valuepicker('retry-attemps', "RETRY_ATTEMPS", 1, 25)
        ], className="g-0")
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row(html.H3('Size variables')),
    dbc.Row([
        dbc.Row([
            make_valuepicker('category-height', "CATEGORY_HEIGHT", 100, 500),
            make_valuepicker('category-font-size', "CATEGORY_FONT_SIZE", 1, 50),
            make_valuepicker('troubleshooting-height', "TROUBLESHOOTING_HEIGHT", 100, 2000)
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_valuepicker('division-padding', "DIVISION_PADDING", 1, 50),
            make_valuepicker('side-padding', "SIDE_PADDING", 1, 50),
            dbc.Col()
        ], className="g-0")
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row(html.H3('Color variables')),
    dbc.Row([
        dbc.Row([
            make_colorpicker('work-color', 'WORK_COLOR'),
            make_colorpicker('personal-color', 'PERSONAL_COLOR'),
            make_colorpicker('neutral-color', 'NEUTRAL_COLOR'),
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_colorpicker('text-color', 'TEXT_COLOR'),
            make_colorpicker('card-color', 'CARD_COLOR'),
            make_colorpicker('background', 'BACKGROUND'),
        ], className="g-0"),
        html.Hr(),
        dbc.Row([
            make_colorpicker('card-percentage-color', 'CATEGORY_CARD_PERCENTAGE_COLOR'),
        ], className="g-0")
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
])


input_names = [
    'idle-time', 'idle-check-interval', 'activity-check-interval',
    'minimum-activity-time', 'unresponsive-threshold', 'retry-attemps',
    'category-height', 'category-font-size', 'troubleshooting-height',
    'division-padding', 'side-padding',
    'work-color', 'personal-color', 'neutral-color',
    'text-color', 'card-color', 'background',
    'card-percentage-color'
]
variable_names = [
    "IDLE_TIME", "IDLE_CHECK_INTERVAL", "ACTIVITY_CHECK_INTERVAL",
    "MINIMUM_ACTIVITY_TIME", "UNRESPONSIVE_THRESHOLD", "RETRY_ATTEMPS",
    "CATEGORY_HEIGHT", "CATEGORY_FONT_SIZE", "TROUBLESHOOTING_HEIGHT",
    "DIVISION_PADDING", "SIDE_PADDING",
    "WORK_COLOR", "PERSONAL_COLOR", "NEUTRAL_COLOR",
    "TEXT_COLOR", "CARD_COLOR", "BACKGROUND",
    "CATEGORY_CARD_PERCENTAGE_COLOR"
]

@callback(
    [Output(f'saved-{name}', 'children') for name in input_names],
    Input('refresh-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
)
def update_saved_values(_1, _2):
    """Updates the saved values using the config file."""
    global CFG
    CFG = load_config()
    return [CFG[var] for var in variable_names]


@callback(
    [Output(name, 'value') for name in input_names],
    Input('set-button', 'n_clicks'),
)
def update_display_values(_1):
    """Updates the display values using the config file."""
    global CFG
    CFG = load_config()
    return_value = [CFG[var] for var in variable_names[:11]]
    return_value += [rgb_to_hex(CFG[var]) for var in variable_names[11:]]
    return return_value


@callback(
    [Output(name, 'invalid') for name in input_names],
    Output('save-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
    Input('check_interval', 'n_intervals'),
    [State(name, 'value') for name in input_names],
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

    assert not any(invalid)

    yaml = YAML()
    yaml.indent(mapping=4, sequence=2, offset=2)
    yaml.preserve_quotes = True
    yaml.explicit_end = True

    path = os.path.join(CFG["WORKSPACE"], 'config/config.yml')
    with open(path, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    for arg, name in zip(args[0:11], variable_names[0:11]):
        assert arg is not None
        data[name] = arg

    for arg, name in zip(args[11:], variable_names[11:]):
        assert arg is not None
        data[name] = hex_to_rgb(arg)

    with open(path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)
    return invalid + [n_clicks]
