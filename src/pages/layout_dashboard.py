"""Dashboard page."""
# pylint: disable=wrong-import-position, import-error, global-statement
# flake8: noqa: E402
import os
import sys
import time
import pandas as pd
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import layout_menu
from helper_server import generate_cards, \
    format_short_duration
from helper_io import save_dataframe, load_dataframe, \
    load_input_time, load_config, set_idle, load_lastest_row, load_day_total

CFG = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H3("Productivity Dashboard"), width='auto'),
        dbc.Col(
            dbc.Button([
                    dbc.Spinner(html.Div(id="idle_loading"), size="sm"),
                    "Set state to idle"
                ],
                id="set_idle_button",
                color="warning", outline=True
            ), class_name="d-md-flex justify-content-md-end"
        )
    ], style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }),
    dbc.Row(id="info_row"),
    dcc.Interval(id='category_interval', interval=15 * 1000, n_intervals=-1),
    dbc.Row(id='category_row'),
    dcc.Interval(
        id='categorized_interval',
        interval=CFG["ACTIVITY_CHECK_INTERVAL"] * 1000,
        n_intervals=-1
    ),
    dbc.Row(id='categorized_list'),
    dbc.Modal([
            dbc.ModalBody([
                html.Br(),
                html.H2("Attention, you are currently idle!"),
                html.Br(),
                html.Img(
                    src='/assets/warning.gif',
                    alt="warning",
                    style={"display": "block", "margin": "0 auto"}
                ),
                html.Br(),
                html.H2("Attention, you are currently idle!"),
                html.Br(),
            ])],
        id="idle_modal", centered=True, is_open=False
    )
])


@callback(
    Output('category_row', 'children'),
    Output('category_row', 'style'),
    Input('category_interval', 'n_intervals')
)
def update_category(_1):
    """Makes total time by category graph."""
    global CFG
    CFG = load_config()

    data = load_day_total(364).transpose()
    data.reset_index(inplace=True)
    data.rename(columns={
        'index': 'category', data.columns[1]: 'total'
    }, inplace=True)
    fig = px.bar(
        data, x='category', y='total',
        category_orders={'category': ['Work', 'Personal', 'Neutral']}
    )

    fig.update_traces(marker_color=[
        CFG["NEUTRAL_COLOR"], CFG["PERSONAL_COLOR"], CFG["WORK_COLOR"]])
    fig.update_layout(
        plot_bgcolor=CFG['CARD_COLOR'],
        paper_bgcolor=CFG['CARD_COLOR'],
        font_color=CFG['TEXT_COLOR'],
        height=CFG['CATEGORY_HEIGHT'],
        legend_title_text="",
        title="",
        title_font_color=CFG['TEXT_COLOR'],
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
    )
    fig.update_xaxes(
        title=None,
        showgrid=False
    )
    fig.update_yaxes(
        title=None,
        showgrid=False,
        showticklabels=False
    )
    sum_annotations = [
        {
            'x': xi,
            'y': yi + (data['total'].max() / 9),
            'text': f"{yi:.2f} hour" + (
                "s" if yi >= 1 else "") + f" / {round(yi / 16 * 100, 1)}% of the day",
            'xanchor': 'center',
            'yanchor': 'top',
            'showarrow': False,
            'font': {
                'color': CFG['TEXT_COLOR'],
                'size': CFG['CATEGORY_FONT_SIZE']
            }
        } for xi, yi in zip(data['category'], data['total'])
    ]
    fig.update_layout(annotations=sum_annotations)

    card_style = {
        'background-color': CFG['CARD_COLOR'],
        'border': f'1px solid {CFG["CARD_OUTLINE_COLOR"]}'
    }
    cardbody_style = {'padding': f'{CFG["CARD_PADDING"]}px'}

    card = dbc.Card([dbc.CardBody([
        dcc.Graph(figure=fig),
    ], style=cardbody_style)], style=card_style)

    style = {
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }
    return card, style


@callback(
    Output('categorized_list', 'children'),
    Output('categorized_list', 'style'),
    Input('categorized_interval', 'n_intervals'),
    prevent_initial_call=True
)
def update_element_list(_1):
    """Generates the event cards."""
    dataframe = load_dataframe('categories')
    dataframe = dataframe[
        dataframe['day'] == str(pd.to_datetime('today').date())]
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'frontend')
    cards = generate_cards(dataframe)
    style = {
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px"
    }
    return cards, style


@callback(
    Output('info_row', 'children'),
    Output('info_row', 'style'),
    Output('idle_modal', 'is_open'),
    Input('categorized_interval', 'n_intervals')
)
def update_info_row(_1):
    """Makes time since last update row and updates idle modal."""
    now = int(time.time())
    backend = format_short_duration(now - load_input_time('backend'))
    frontend = format_short_duration(now - load_input_time('frontend'))
    mouse = format_short_duration(now - load_input_time('mouse'))
    keyboard = format_short_duration(now - load_input_time('keyboard'))
    audio = format_short_duration(now - load_input_time('audio'))
    fullscreen = format_short_duration(now - load_input_time('fullscreen'))

    style = {'margin': '0px'}
    card_style = {
        'background-color': CFG['CARD_COLOR'],
        'border': f'1px solid {CFG["CARD_OUTLINE_COLOR"]}'
    }
    cardbody_style = {'padding': f'{CFG["CARD_PADDING"]}px'}

    row = dbc.Card([dbc.CardBody([dbc.Row([
        dbc.Col([html.H4("Backend"), html.H5(backend)], style=style),
        dbc.Col([html.H4("Fronent"), html.H5(frontend)], style=style),
        dbc.Col([html.H4("Mouse"), html.H5(mouse)], style=style),
        dbc.Col([html.H4("Keyboard"), html.H5(keyboard)], style=style),
        dbc.Col([html.H4("Audio"), html.H5(audio)], style=style),
        dbc.Col([html.H4("Fullscreen"), html.H5(fullscreen)], style=style)
    ])], style=cardbody_style)], style=card_style)

    style={
        'margin-left': f"{CFG['SIDE_PADDING']}px",
        'margin-right': f"{CFG['SIDE_PADDING']}px",
        'margin-bottom': f"{CFG['DIVISION_PADDING']}px",
        'margin-top': f"{CFG['DIVISION_PADDING']}px",
    }

    # Modal
    last_row = load_lastest_row('activity')
    idle = last_row.loc[0, "process_name"] == "IDLE TIME"
    return row, style, idle


@callback(
    Output('idle_loading', 'children'),
    Input('set_idle_button', 'n_clicks'),
    prevent_initial_call=True
)
def set_idle_button(_1):
    """Sets all input databases to idle state."""
    # Ensure idle is set (late mouse thread can revert this sometimes)
    time.sleep(3)
    set_idle()
    time.sleep(0.5)
    set_idle()
    time.sleep(0.5)
    set_idle()
    # Loading animation has a delay
    time.sleep(0.5)
    return ""
