"""
deck of helper functions for flashcards functionality.
"""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: F401
from os.path import dirname, abspath
import sys
import time
from dash import html, callback, Output, Input, State, callback_context, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

sys.path.append(dirname(dirname(abspath(__file__))))
sys.path.append(dirname(abspath(__file__)))

import layout_menu
from helper_io import load_config, update_flashcard, update_flashcards_database
from helper_server import format_long_duration

CFG = load_config()
FLASHCARDS = None


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H2("Flashcards page"))
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Col(dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(html.H3(id="card-album", style={
                    "textAlign": "left", 'text-decoration': 'underline'
                })),
                dbc.Col(
                    dbc.Button(
                        dbc.Spinner(html.Div(id="load-flashcards-spinner")),
                        id="load-flashcards"
                    ), style={"textAlign": "right"}
                )
            ]),
            html.Br(),
            dbc.Row(
                html.Small(id="card-info", style={'whiteSpace': 'pre'}),
                style={"textAlign": "center"}
            )
        ]),
        dbc.CardBody([
            html.P("Question:", className="card-text"),
            dbc.Card(dcc.Markdown(id="card-question"), className="mx-4 my-4 p-2"),
            html.P("Answer:", className="card-text"),
            dbc.Fade([
                dbc.Card(dcc.Markdown(id="card-answer"), className="mx-4 my-4 p-2")
            ], id="flashcard-fade", exit=False),
        ], style={"height": "70vh", "overflow": "scroll"}),
        dbc.CardFooter([dbc.Row([
            dbc.Col(dbc.ButtonGroup([
                dbc.Button("RIGHT", id="button-1", color="success"),
                dbc.Button("Right", id="button-2", color="info"),
                dbc.Button("Guess", id="button-3", color="secondary"),
                dbc.Button("Guess -", id="button-4", color="secondary"),
                dbc.Button("Wrong", id="button-5", color="warning"),
                dbc.Button("WRONG", id="button-6", color="danger"),
            ])),
            dbc.Col(dbc.Button(
                "Reveal answer", id="reveal-flashcard",
                color="light", className="float-end"
            ))
        ])]),
    ], style={
        'background-color': CFG['CARD_COLOR'],
        'border': f'1px solid {CFG["CARD_OUTLINE_COLOR"]}',
        'margin-bottom': f'{CFG["CATEGORY_CARD_MARGIN"]}px',
        'color': CFG['TEXT_COLOR']
    }), style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px",
        'align-items': "center"
    })
])


@callback(
    Output('card-album', 'children'),
    Output('card-question', 'children'),
    Output('card-answer', 'children'),
    Output('card-info', 'children'),
    Output("flashcard-fade", "is_in"),
    Output("load-flashcards-spinner", "children"),

    Input('button-1', 'n_clicks'),
    Input('button-2', 'n_clicks'),
    Input('button-3', 'n_clicks'),
    Input('button-4', 'n_clicks'),
    Input('button-5', 'n_clicks'),
    Input('button-6', 'n_clicks'),
    Input("load-flashcards", "n_clicks"),
    Input("reveal-flashcard", "n_clicks"),

    State("flashcard-fade", "is_in"),
    State('card-album', 'children'),
    State('card-question', 'children'),
    State('card-answer', 'children'),
    State('card-info', 'children')
)
def update_card(_1, _2, _3, _4, _5, _6, _7, _8, is_in, *card):
    """Update card."""
    ctx = callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx == "reveal-flashcard":
        return *card, not is_in, "Reload flashcard"

    global FLASHCARDS
    if FLASHCARDS is None:
        FLASHCARDS = update_flashcards_database()

    if FLASHCARDS is None:
        raise PreventUpdate

    if ctx.startswith('button-'):
        result = update_flashcard(FLASHCARDS, int(ctx[-1]), card)
        if result is not None:
            FLASHCARDS = result

    if ctx.startswith("load"):
        FLASHCARDS = update_flashcards_database()
        return *card, is_in, "Reload flashcard"
    card = FLASHCARDS.loc[0, :]
    info = (
        f"Ease factor {round(card.ease_factor, 2)}    Last access: "
        f"{format_long_duration(int(time.time()) - card.last_access)} ago    "
        f"Access interval: {format_long_duration(card.access_interval)}"
    )
    return card.deck_name, card.question, card.answer, info, False, "Reload flashcard"
