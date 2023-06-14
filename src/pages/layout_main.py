"""Dashboard page."""
# pylint: disable=wrong-import-position, import-error
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
    format_short_duration, set_date_range
from helper_io import save_dataframe, load_dataframe, \
    load_input_time, load_config

cfg = load_config()


layout = html.Div([
    dbc.Row([
        layout_menu.layout,
        dbc.Col(html.H3("Productivity Dashboard"), width='auto'),
        dcc.Interval(
            id='date_reset_interval',
            interval=30 * 1000,
            n_intervals=-1
        )
    ], style={
        'margin-left': f"{cfg['SIDE_PADDING']}px",
        'margin-right': f"{cfg['SIDE_PADDING']}px",
        'margin-bottom': f"{cfg['DIVISION_PADDING']}px",
        'margin-top': f"{cfg['DIVISION_PADDING']}px"
    }),
    dbc.Row([dbc.Card([dbc.CardBody([
        html.Div(id="info_row")
    ])])], style={
        'margin-left': f"{cfg['SIDE_PADDING']}px",
        'margin-right': f"{cfg['SIDE_PADDING']}px",
        'margin-bottom': f"{cfg['DIVISION_PADDING']}px",
        'margin-top': f"{cfg['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dbc.Card([dbc.CardBody([
            dcc.Graph(
                id="category_graph"
            ),
            dcc.Interval(
                id='category_interval',
                interval=10 * 1000,
                n_intervals=-1
            )
        ])])
    ], style={
        'margin-left': f"{cfg['SIDE_PADDING']}px",
        'margin-right': f"{cfg['SIDE_PADDING']}px",
        'margin-bottom': f"{cfg['DIVISION_PADDING']}px",
        'margin-top': f"{cfg['DIVISION_PADDING']}px"
    }),
    dbc.Row([
        dcc.Interval(
            id='categorized_interval',
            interval=cfg["ACTIVITY_CHECK_INTERVAL"] * 1000,
            n_intervals=-1
        ),
        dbc.Col([
            html.Div(
                id='categorized_list',
                style={
                    'margin-left': f"{cfg['SIDE_PADDING']}px",
                    'margin-right': f"{cfg['SIDE_PADDING']}px"
                }
            )
        ])

    ])
])


@callback(
    Output('category_graph', 'figure'),
    Input('category_interval', 'n_intervals'))
def update_category(_1):
    """Makes total time by category graph."""
    _, data = load_dataframe('totals')
    fig = px.bar(
        data, x='category', y='total',
        category_orders={'category': ['Work', 'Personal', 'Neutral']}
    )
    fig.update_traces(marker_color=cfg['CATEGORY_COLORS'])
    fig.update_layout(
        plot_bgcolor='rgb(43, 43, 43)',
        paper_bgcolor='rgb(43, 43, 43)',
        font_color=cfg['TEXT_COLOR'],
        height=cfg['CATEGORY_HEIGHT'],
        legend_title_text="",
        title="",
        title_font_color=cfg['TEXT_COLOR'],
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
            'y': yi + (data['total'].max() / 8),
            'text': f"{yi:.2f} hour" + ("s" if yi >= 2 else ""),
            'xanchor': 'center',
            'yanchor': 'top',
            'showarrow': False,
            'font': {
                'color': cfg['TEXT_COLOR'],
                'size': cfg['CATEGORY_FONT_SIZE']
            }
        } for xi, yi in zip(data['category'], data['total'])
    ]
    fig.update_layout(annotations=sum_annotations)
    return fig


@callback(
    Output('categorized_list', 'children'),
    Input('categorized_interval', 'n_intervals'))
def update_element_list(_1):
    """Generates the event cards."""
    _, dataframe = load_dataframe('categories')
    save_dataframe(pd.DataFrame({'time': [int(time.time())]}), 'frontend')
    return generate_cards(dataframe)


@callback(
    Output('info_row', 'children'),
    Input('categorized_interval', 'n_intervals')
)
def update_info_row(_1):
    """Makes time since last update row."""
    now = int(time.time())
    backend = format_short_duration(now - load_input_time('backend'))
    frontend = format_short_duration(now - load_input_time('frontend'))
    mouse = format_short_duration(now - load_input_time('mouse'))
    keyboard = format_short_duration(now - load_input_time('keyboard'))
    audio = format_short_duration(now - load_input_time('audio'))
    fullscreen = format_short_duration(now - load_input_time('fullscreen'))
    style = {'margin': '0px'}
    row = dbc.Row([
        dbc.Col([html.H4("Backend"), html.H5(backend)], style=style),
        dbc.Col([html.H4("Fronent"), html.H5(frontend)], style=style),
        dbc.Col([html.H4("Mouse"), html.H5(mouse)], style=style),
        dbc.Col([html.H4("Keyboard"), html.H5(keyboard)], style=style),
        dbc.Col([html.H4("Audio"), html.H5(audio)], style=style),
        dbc.Col([html.H4("Fullscreen"), html.H5(fullscreen)], style=style)
    ])
    return row


@callback(
    Output('date_reset_interval', 'n_intervals'),
    Input('date_reset_interval', 'n_intervals')
)
def save_date(intevals):
    """Sets the desired date range to file."""
    set_date_range()
    return intevals
