
import os
import pathlib
import re
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd
from itertools import islice
import csv
from collections import OrderedDict
import time
from time import strftime
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

path = "data_fuel.csv"
path_sae = "data_sae.csv"

df = pd.read_csv(path)

df_sae = pd.read_csv(path_sae)

app = dash.Dash(
    __name__,
    external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Painel de Controle - Tche Baja"
server = app.server
app.config["suppress_callback_exceptions"] = True

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Telemetria",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Dados Baja SAE",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Painel de Controle"),
                    html.H6("Dados do carro informados a partir de medidores e graficos"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("logo_branco.png"), style={'width': '60px', 'height':'60px'}),
                    ),
                ],
            ),
        ],
    )

# Web Scraping do Baja SAE

PATH = 'C:\Program Files (x86)\chromedriver.exe'

# Coleta os dados do Enduro
def GetDataFromSAE():

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_argument('disable-dev-shm-usage')

    driver = webdriver.Chrome(PATH, options=options)

    driver.get("https://resultados.bajasaebrasil.online/22SU/prova.php?id=22SU_END")

    time.sleep(4)

    page = bs(driver.page_source,"html.parser")

    table = page.find(id='myTable')

    headers = ['Posicao', 'ID', 'Equipe', 'Voltas','Pontos']

    matrix = []
    for rows in table.select('tr')[1:]:
        values = []
        for columns in rows.select('td'):
            values.append(columns.text)
        matrix.append(values)

    df = pd.DataFrame(data=matrix, columns=headers)

    driver.quit()

    return df[df.eq("12").any(1)]

# Armazena os dados para passar para o arquivo.
df_typing_formatting = pd.DataFrame(OrderedDict([
    ('Voltas', [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
    ('Tempo', ['00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00','00:00',
               '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00',
               '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00', '00:00','00:00','00:00','00:00','00:00','00:00']),
]))

# Secao 1 do Painel
def tab_content():
    return (html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Dados provindos do Baja SAE"),
            html.Div(
                id="control-chart-live",
                children=[
                    dcc.Interval(id='interval_dt', interval=10000*2, n_intervals=0),
                    html.Div(
                        id="card-1",
                        children=[
                            daq.LEDDisplay(
                                id="operator-led3",
                                label={
                                    'label': 'Pontos',
                                    'style': {
                                        'color': 'white',
                                        'fontSize': 16,
                                    }
                                },
                                value='0',
                                labelPosition="bottom",
                                backgroundColor='transparent',
                                color="white",
                                size=15
                            ),
                            daq.LEDDisplay(
                                id="operator-led2",
                                label={
                                    'label': 'Voltas',
                                    'style': {
                                        'fontSize': 16,
                                    }
                                },
                                value='0',
                                labelPosition="bottom",
                                backgroundColor='transparent',
                                color="white",
                                size=15
                            ),
                            daq.LEDDisplay(
                                id="operator-led4",
                                label={
                                    'label': 'Enduro',
                                    'style': {
                                        'fontSize': 16,
                                    }
                                },
                                value='0',
                                labelPosition="bottom",
                                backgroundColor='transparent',
                                color="white",
                                size=15
                            ),
                            daq.LEDDisplay(
                                id="operator-led5",
                                label={
                                    'label': 'Tempo de Corrida',
                                    'style': {
                                        'fontSize': 16,
                                    }
                                },
                                value='0',
                                labelPosition="bottom",
                                backgroundColor='transparent',
                                color="white",
                                size=15
                            ),
                            dbc.Button(
                                'Stop',
                                color="dark",
                                id='btn-5',
                                className="btn5",
                                n_clicks=0,
                            )
                        ])])]))

# Contadores para o start()
sc = -20
mn = 0
hr = 0
stp = 0

# Contadores para o start_2()
sec = -20
mins = 0
hour = 0
stp_2 = 0
voltas = 0

# Auxiliares
i = 0
j = 0
m = 0
n = 0

def start():

    global sc, mn, hr, stp

    sc = sc + 20

    if(sc==60):
        mn = mn + 1
        sc = 0

    if(mn==60):
        hr= hr + 1
        mn = 0

    if(stp == 0):
        return '%i:%i:%i'%(hr, mn, sc)


def start_2():

    global sec, mins, hour, stoop

    sec = sec + 20

    if(sec==60):
        mins = mins + 1
        sec = 0

    if(mins==60):
        hour= hour + 1
        mins = 0

    if(stp_2==0):
        return '%i:%i:%i'%(hour, mins, sec)

# Remove os elementos que nao sao ASCII da coluna Posicao
def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i) < 128)


# Secao 2 do Painel
def tab_content_2():

    return (html.Div(
            id="control-chart-container2",
            className="twelve columns",
            children=[
                generate_section_banner("Ultimo Abastecimento"),
                html.Div(
                    id="control-chart-live2",
                    children=[
                        dcc.Interval(id='interval_db', interval=10000*2, n_intervals=0),
                        html.Div(
                            id="card-2",
                            children=[
                                dbc.Button(
                                    [
                                        html.I(className="bi bi-fuel-pump-fill"),
                                    ],
                                    color="#1E2130",
                                    id='btn-1',
                                    className="btn",
                                    n_clicks=0,
                                ),
                                daq.LEDDisplay(
                                    id="operator-tempo2",
                                    className="tempo2",
                                    label={
                                        'label': 'Tempo de Corrida',
                                        'color':'white',
                                        'style': {
                                            'fontSize': 16,
                                        }
                                    },
                                    value='0',
                                    labelPosition="bottom",
                                    color="white",
                                    backgroundColor="#1E2130",
                                    size=15,
                                ),
                                daq.LEDDisplay(
                                    id="operator-volta2",
                                    label={
                                        'label': 'Voltas',
                                        'style': {
                                            'fontSize': 16,
                                        }
                                    },
                                    value='0',
                                    labelPosition="bottom",
                                    color="white",
                                    backgroundColor="#1E2130",
                                    size=15,
                                ),
                            ])])]))

# Secao 3 do Painel
def tab_content_3():

    return (html.Div(
            id="control-chart-container3",
            className="twelve columns",
            children=[
                generate_section_banner("Analise do Tempo em cada Volta"),
                html.Div(
                    id="control-chart-live3",
                    children=[
                        html.Div(
                            id="card-3",
                            children=[
                                daq.LEDDisplay(
                                    id="operator-tempo5",
                                    className="tempo5",
                                    label={
                                        'label': 'Ultima',
                                        'color': 'white',
                                        'style': {
                                            'fontSize': 16,
                                        }
                                    },
                                    value='0',
                                    labelPosition="bottom",
                                    color="white",
                                    backgroundColor="transparent",
                                    size=15,
                                ),
                                daq.LEDDisplay(
                                    id="operator-tempo3",
                                    className="tempo3",
                                    label={
                                        'label': 'Melhor',
                                        'style': {
                                            'fontSize': 16,
                                        }
                                    },
                                    value='0',
                                    labelPosition="bottom",
                                    color="white",
                                    backgroundColor="transparent",
                                    size=15,
                                ),
                                html.Div([
                                dash_table.DataTable(id="input-data",
                                                     columns=[{"name": i, "id": i} for i in df_sae.columns],
                                                     data=df_sae.to_dict('records'),
                                                     editable=True,
                                                     row_deletable=True,
                                                     style_table={},
                                                     style_cell={'textAlign': 'center',
                                                                 'font_size': '20px',
                                                                 'height': '50px',
                                                                 'width':'180px',
                                                                 'border': '3px solid white'
                                                                 },
                                                     style_data={
                                                         'color': 'white',
                                                         'backgroundColor': 'transparent',
                                                     },
                                                     style_header={
                                                         'color': 'white',
                                                         'backgroundColor': 'transparent',
                                                         'font_size': '20px',
                                                         'border': '3px solid white'
                                                     },
                                                     sort_action='native',
                                                     page_action="native",
                                                     page_current=0,
                                                     page_size=4,
                                                     export_format='csv',
                                                     export_headers='names',
                                                     ),
                                        dcc.Interval(id='interval_data', interval=10000*2, n_intervals=0)])
                                      ]
                        )])]))

# Secao 4 do Painel
def tab_content_4():

    return (html.Div(
            id="control-chart-container4",
            className="twelve columns",
            children=[
                generate_section_banner("Analise desde o Ultimo Abastecimento"),
                html.Div(
                    id="control-chart-live4",
                    children=[
                        html.Div(
                            id="card-4",
                            children=[
                                html.Div(
                                children=[dash_table.DataTable(id="input-data2",
                                                               columns=[{"name": i, "id": i} for i in df.columns],
                                                               data=df.to_dict('records'),
                                                               editable=True,
                                                               row_deletable=True,
                                                               style_table={},
                                                               style_cell={'textAlign': 'center',
                                                                           'font_size': '20px',
                                                                           'height': '50px',
                                                                           'width': '180px',
                                                                           'border': '3px solid white'
                                                                           },
                                                               style_data={
                                                                   'color': 'white',
                                                                   'backgroundColor': 'transparent',
                                                               },
                                                               style_header={
                                                                   'color': 'white',
                                                                   'backgroundColor': 'transparent',
                                                                   'font_size': '20px',
                                                                   'border': '3px solid white'
                                                               },
                                                               style_data_conditional=[{
                                                                   'if': {
                                                                       'filter_query': '{tempo} gt 50'
                                                                   },
                                                                   'backgroundColor': 'lightgrey'
                                                               }],
                                                               sort_action='native',
                                                               page_action="native",
                                                               page_current=0,
                                                               page_size=4,
                                                               export_format='csv',
                                                               export_headers='names',
                                                               ),
                                          dcc.Interval(id='interval_data2', interval=10000*2, n_intervals=0)])
                            ])])]))


def render_tab_content():
    return html.Div([
            generate_section_banner("Dados da Telemetria")
        ])

# Layout do Painel
app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                dcc.Tabs(
                    id="app-tabs",
                    value="tab2",
                    className="custom-tabs",
                    children=[
                        dcc.Tab(
                            id="Specs-tab",
                            label="Telemetria",
                            value="tab1",
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                            children=[render_tab_content()]
                        ),
                        dcc.Tab(
                            id="Control-chart-tab",
                            label="Dados Baja SAE",
                            value="tab2",
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                            children=[tab_content(), tab_content_2(), tab_content_3(), tab_content_4()]
                        ),
                    ],
                ),
                html.Div(id="app-content")
            ],
        )
    ]
)


# Chama as funcoes para compor o Painel
# @app.callback(
#     [Output("app-content", "children")],
#     [Input("app-tabs", "value")]
# )
#
# def calling_tab(tab):
#     if tab == 'tab1':
#         return render_tab_content()
#
#     elif tab == 'tab2':
#         return render_tab_content_2()

@app.callback(
    Output("operator-led3", "value"),
    Output("operator-led2", "value"),
    Output("operator-led4", "value"),
    Output("operator-led5", "value"),
    Input("interval_dt", "n_intervals"),
    Input("btn-5", "n_clicks")
)

# Adiciona os dados na secao 1 do painel
def secao_1(n_intervals, btn5):

    global i, j, df_typing_formatting

    # Dados do Baja SAE
    dr = GetDataFromSAE()

    # Cronometro
    ct = start()

    dr['Posicao'] = dr['Posicao'].apply(remove_non_ascii)

    if 'btn-5' == ctx.triggered_id:
        ct = 0

    voltas = int(dr.iloc[0, 3])

    df_typing_formatting.iloc[i, j] = voltas

    if df_typing_formatting.iloc[i, j] > df_typing_formatting.iloc[i - 1, j]:

        df_typing_formatting.iloc[i, j + 1] = ct

        i = i + 1

        with open('data_sae.csv', 'a+') as f:
            for line in islice(f, 1, None):
                pass

            data = [voltas, ct]

            writing = csv.writer(f)

            writing.writerow(data)

            f.close()

    else:
        df_typing_formatting.iloc[i, j] = 0

    return dr.iloc[0,4], dr.iloc[0,3], dr.iloc[0,0], ct

@app.callback(
    Output("operator-tempo2", "value"),
    Output("operator-volta2", "value"),
    Input('btn-1', 'n_clicks'),
    Input("interval_db", "n_intervals")
)

# Adiciona os dados na secao 2 do painel
def secao_2(n_intervals, btn1):

    # Cronometro
    ct = start_2()

    # Dados do Baja SAE
    dr = GetDataFromSAE()

    voltas = dr.iloc[0,3]

    if "btn-1" == ctx.triggered_id:

        data = [voltas, ct]

        with open('data_fuel.csv', 'a+') as f:
            for line in islice(f, 1, None):
                pass

            writing = csv.writer(f)

            writing.writerow(data)

            f.close()

    return ct, voltas


@app.callback([Output('operator-tempo5', 'value'),
              Output('operator-tempo3', 'value'),
              Output('input-data', 'data')],
              [Input('interval_data', 'n_intervals')])

# Adiciona os dados na secao 3 do painel
def adiciona_linhas_secao3(n_intervals):

    data = pd.read_csv(path_sae)

    tempo5 = data['Tempo'].iat[-2]

    tempo3 = data['Tempo'].min()

    dict = data.to_dict('records')

    return tempo5, tempo3, dict

@app.callback(Output('input-data', 'columns'),
              [Input('interval_data', 'n_intervals')
              ])

def adiciona_linhas_secao3(n_intervals):

    data = pd.read_csv(path_sae)

    columns = [{'id': i, 'name': i} for i in data.columns]

    return columns


@app.callback(Output('input-data2', 'data'),
              [Input('interval_data2', 'n_intervals')])

# Adiciona os dados na secao 4 do painel
def adiciona_linhas_secao4(n_intervals):

    data = pd.read_csv(path)

    dict = data.to_dict('records')

    return dict

@app.callback(Output('input-data2', 'columns'),
              [Input('interval_data2', 'n_intervals')
              ])

def adiciona_colunas_secao4(n_intervals):

    data = pd.read_csv(path)

    columns = [{'id': i, 'name': i} for i in data.columns]

    return columns

# Roda o servidor
if __name__ == "__main__":
    app.run_server(debug=True, port=8000)