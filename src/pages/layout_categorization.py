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
from helper_io import load_config, load_categories
from helper_server import make_listpicker

CFG = load_config()
CFG2 = load_categories()
NAMES = list(CFG2.keys())

layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("Categorization page"), width='auto'),
        dbc.Col([
            dbc.Col(
                dbc.Button(
                    "Reset values",
                    id="reset-button",
                    color="info", outline=True
                ), width='auto'
            ),
            dbc.Tooltip(
                "Reset the values and options of the checklist with the \
                    contents of the current categories file. DESCTRUCTIVE!",
                target="reset-button", placement="bottom"),
            dbc.Col(
                dbc.Button(
                    "Save config",
                    id="save-button",
                    color="danger", outline=True
                ), width='auto'
            ),
            dbc.Tooltip(
                "Save the values of all tabs to the current \
                    categories file. DESCTRUCTIVE!",
                target="save-button", placement="bottom"),
            dcc.Interval(
                id='check_interval',
                interval=1 * 1000,
                n_intervals=-1
            )
        ], className="d-grid gap-2 d-md-flex justify-content-md-end")
    ], style=CFG["SECTION_STYLE"]),
    dbc.Row([dbc.Tabs([
        make_listpicker(name) for name in NAMES
    ])], style=CFG["SECTION_STYLE"])
])


@callback(
    [Output(f'button-{name}', 'n_clicks') for name in NAMES],
    [Output(f'checklist-{name}', 'value') for name in NAMES],
    [Output(f'input-{name}', 'value') for name in NAMES],
    [Output(f'checklist-{name}', 'options') for name in NAMES],
    Input('reset-button', 'n_clicks'),
    Input('save-button', 'n_clicks'),
    [Input(f'button-{name}', 'n_clicks') for name in NAMES],
    [State(f'input-{name}', 'value') for name in NAMES],
    [State(f'checklist-{name}', 'value') for name in NAMES],
    prevent_initial_call=True
)
def input_value(_, _2, *args):
    """Updates the saved values using the config file."""
    global CFG2
    CFG2 = load_categories()

    raw_ctx = callback_context.triggered[0]['prop_id'].split('.')[0]
    ctx = raw_ctx[7:]
    size = len(NAMES)
    buttons = args[0:size]
    inputs = list(args[size:2*size])
    values = list(args[2*size:3*size])

    # Save configuration
    if raw_ctx == 'save-button':
        yaml = YAML()
        yaml.indent(mapping=4, sequence=2, offset=2)
        yaml.preserve_quotes = True
        yaml.explicit_end = True

        path = os.path.join(CFG["WORKSPACE"], 'config/categories.yml')
        for name, items in zip(NAMES, values):
            CFG2[name] = items

        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(CFG2, file)
        return buttons + tuple(values) + tuple(inputs) + tuple(values)

    # Reset values
    if raw_ctx == 'reset-button':
        return buttons + tuple(CFG2.values()) + tuple(inputs) + tuple(CFG2.values())

    index = NAMES.index(ctx)
    new_value = inputs[index]

    if not new_value or new_value in CFG2[ctx]:
        return buttons + tuple(values) + tuple(inputs) + tuple(values)

    # Update checklist values, otherwise new option will not be checked
    values[index].append(new_value)

    # Clear text from input field
    inputs[index] = ""
    return buttons + tuple(values) + tuple(inputs) + tuple(values)
