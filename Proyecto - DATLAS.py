# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 11:24:32 2022

@author: datar
"""
# Bibliotecas que posiblemente requieran instalacion
# pip install folium
# pip install dash
# pip install plotly
# pip install dash_bootstrap_components

import dash
import folium
import numpy as np
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#------------Funciones para generar el mapa con la ubicacion de los lugares
def generador_mapa_ab(nombre):
    df_ab = airbnb[['Nombre', 'Latitud', 'Longitud']]
    ab_a_mapear = df_ab[df_ab['Nombre'] == nombre]
    punto = (ab_a_mapear.Latitud.values[0], ab_a_mapear.Longitud.values[0])
    mapa_ab = folium.Map(location = punto, zoom_start = 12)
    folium.Marker(location = punto, popup = nombre, icon = folium.Icon(color="red", icon="info-sign")).add_to(mapa_ab)
    doc_nom = 'assets/' + nombre + '.html'
    mapa_ab.save(doc_nom)
    
def generador_mapa_hot(nombre):
    df_hot = hoteles[['Nombre', 'Latitud', 'Longitud']]
    hot_a_mapear = df_hot[df_hot['Nombre'] == nombre]
    punto = (hot_a_mapear.Latitud.values[0], hot_a_mapear.Longitud.values[0])
    mapa_hot = folium.Map(location = punto, zoom_start = 12)
    folium.Marker(location = punto, popup = nombre, icon = folium.Icon(color = "green", icon = "info-sign")).add_to(mapa_hot)
    doc_nom = 'assets/' + nombre + '.html'
    mapa_hot.save(doc_nom)

#-----------Lectura de los documentos y preparacion de algunas contadores
airbnb = pd.read_excel('BD_AIRBNB.xlsx')
total_airbnb = airbnb.shape[0]
lista_municipios = airbnb.Municipio.unique()
lista_municipios.sort()

hoteles = pd.read_excel('DB_HOTELES.xlsx')
total_hoteles = hoteles.shape[0]

#-----------Histograma fijo para los hoteles
fig2 = px.histogram(hoteles, x = 'Precio (MXN)')

#-----------Inicializacion y aplicacion de tema a Dash
app = dash.Dash(external_stylesheets = [dbc.themes.LUX])

#-----------Barra de navegacion
navbar = dbc.Navbar(id = ' navbar', children = [
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Img(src = app.get_asset_url('datlas.png'), height = '50px')
                )
            ], align = 'center')
        ], style = {'margin' : '0px 10px'})
    ], color = '#345696', style = {'padding' : '10px'})

#------------Dropdown principal con el listado de municipios del area metropolitana
dropdown = dbc.Container([
        html.Br(),

        dbc.Row([
            dbc.Col([
                html.H6('Municipios', ),
                dcc.Dropdown(id = 'dropdown',
                             options = [{'label' : i, 'value' : i} for i in np.append('Todos', lista_municipios)], 
                             value = 'Todos'
                             )
                ])
            ]),
    ], style = {'backgroundColor' : '#E6EFF5'})

#--------------Cuerpo del dashboard
body_app = dbc.Container([
    #Llamado al dropdown
    dropdown,
    html.Br(),
    
    #Fila donde iran las graficas
    dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Card(id = 'frecuencia_precio_airbnb')
                ]),
            dbc.Col([
                dbc.Card(id = 'frecuencia_precio_hoteles')
                ])
            ]),
        ]),
    
    html.Br(),
        
    #Fila donde se despliega informacion estadistica sobre un rango de precios determinado
    dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Card(id = 'estadistica_ab',
                         style = {'height' : '150px'})
                ]),
            dbc.Col([
                dbc.Card(id = 'estadistica_hot',
                         style = {'height' : '150px'})
                ])
            ]),
        ]),
    
    html.Br(),
        
    #Fila para filtro de Airbnb
    dbc.Row([
        dbc.Col([
            dbc.Card(id = 'filtro_airbnb')
            ], width = 12)
        ]),

    html.Br(),
    
    #Fila para Dropdown con lista filtrada
    dbc.Row([
        dbc.Col(
            dbc.Card(id = 'selector_ab'), width = 6
            ),
        dbc.Col(
            dbc.Card(id = 'selector_hot'), width = 6
            ),
        ]),
    
    html.Br(),
    
    #Fila para tabla de resultado
    dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Card(id = 'info_ab')
                ], width=6),
            dbc.Col([
                dbc.Card(id = 'info_hot')
                ], width=6)
            ]),
        ]),
    
    html.Br(),
    
    #Fila para mapas
    dbc.Row([
        dbc.Col([
            html.H1('AIRBNB', style = {'textAlign' : 'center'}),
            html.H1('en el area', style = {'textAlign' : 'center'}),
            html.Iframe(id = 'map_airbnb', srcDoc = open('assets\Todos_mapa.html', 'r').read(), width = '100%', height = '500')
            ]),
        dbc.Col([
            html.H1('Hoteles', style = {'textAlign' : 'center'}),
            html.H1('en el Area Metropolitana', style = {'textAlign' : 'center'}),
            html.Iframe(id = 'map_hoteles', srcDoc = open('assets\mapa_hoteles.html', 'r').read(), width = '100%', height = '500')
            ])
        ])
    
    ], style = {'backgroundColor' : '#E6EFF5'}, 
    fluid = True)

#Union del navbar y cuerpo del dashboard
app.layout = html.Div(id = 'parent', children = [navbar, body_app])

#Modificacion de las graficas a partir del municipio seleccionado (dropdowm)
@app.callback([Output('frecuencia_precio_airbnb', 'children'),
               Output('frecuencia_precio_hoteles', 'children')], 
              [Input('dropdown', 'value')])

def graficas(mun):
    if mun == 'Todos':
        df_aux = airbnb
        fig = px.histogram(df_aux, x = 'Precio (MXN)', range_x = [0, 5000])
        fig.update_layout(yaxis_title = 'Frecuencia')
    elif mun == 'Monterrey':
        df_aux = airbnb[airbnb['Municipio'] == mun]
        fig = px.histogram(df_aux, x = 'Precio (MXN)', range_x = [0, 5000])
        fig.update_layout(yaxis_title = 'Frecuencia')
    else:
        df_aux = airbnb[airbnb['Municipio'] == mun]
        fig = px.histogram(df_aux, x = 'Precio (MXN)')
        fig.update_layout(yaxis_title = 'Frecuencia')
    
    precio_mini = df_aux['Precio (MXN)'].min()
    precio_maxi = df_aux['Precio (MXN)'].max()
        
    
    
    precios_ab = df_aux['Precio (MXN)'].unique()
    precios_ab.sort()
    
    card_content1 = [
        dbc.CardBody([
            html.H6('Frecuencia de precios en AirBnb', 
                    style = {'fontWeight' : 'bold', 
                             'textAlign' : 'center'}),
            html.H6('{}'.format(mun), 
                    style = {'fontWeight' : 'bold', 
                             'textAlign' : 'center'}),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id = 'grafica_airbnb', figure = fig)
                    ])
                ]),
            dbc.Row([
                dbc.Col([
                    html.H4('Rango de precios'),
                    dcc.RangeSlider(id = 'slider_airbnb', min = precio_mini, max = precio_maxi, value = [500, 5000], step = 2500),
                        ])
                ])
            ])
        ]
    
    card_content2 = [
        dbc.CardBody([
            html.H6('Frecuencia de precios en hoteles', 
                    style = {'fontWeight' : 'bold', 
                             'textAlign' : 'center'}),
            html.H6('Area Metropolitana', 
                    style = {'fontWeight' : 'bold', 
                             'textAlign' : 'center'}),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id = 'grafica_hoteles', figure = fig2)
                    ])
                ]),
            dbc.Row([
                dbc.Col([
                    html.H4('Rango de precios'),
                    dcc.RangeSlider(id = 'slider_hoteles', min = hoteles['Precio (MXN)'].min(), max = hoteles['Precio (MXN)'].max(), value = [500, 5000], step = 1000),
                    ])
                ])
            ])
        ]
    
    return card_content1, card_content2

#Modificacion de las graficas, estadisticos y filtro a partir del municipio y rango de precios seleccionados (dropdown y slider)
@app.callback([Output('grafica_airbnb', 'figure'),
               Output('grafica_hoteles', 'figure'),
               Output('estadistica_ab', 'children'), 
               Output('estadistica_hot', 'children'),
               Output('filtro_airbnb', 'children')], 
              [Input('dropdown', 'value'), 
              Input('slider_airbnb', 'value'),
              Input('slider_hoteles', 'value')])

def elementos(mun, rango_ab, rango_hot):
    if mun == 'Todos':
        df_aux = airbnb
        if (rango_ab[0] in range(0,5001)) & (rango_ab[1] in range(0,5001)):
            fig = px.histogram(df_aux, x = 'Precio (MXN)', range_x = [0, 5000])
            fig.add_vline(x = rango_ab[0], line_dash = 'dash', line_color = 'firebrick')
            fig.add_vline(x = rango_ab[1], line_dash = 'dash', line_color = 'firebrick')
            fig.update_layout(yaxis_title = 'Frecuencia')
        else:
            fig = px.histogram(df_aux, x = 'Precio (MXN)')
            fig.add_vline(x = rango_ab[0], line_dash = 'dash', line_color = 'firebrick')
            fig.add_vline(x = rango_ab[1], line_dash = 'dash', line_color = 'firebrick')
            fig.update_layout(yaxis_title = 'Frecuencia')
    elif mun == 'Monterrey':
        df_aux = airbnb[airbnb['Municipio'] == mun]
        if (rango_ab[0] in range(0,5001)) & (rango_ab[1] in range(0,5001)):
            fig = px.histogram(df_aux, x = 'Precio (MXN)', range_x = [0, 5000])
            fig.add_vline(x = rango_ab[0], line_dash = 'dash', line_color = 'firebrick')
            fig.add_vline(x = rango_ab[1], line_dash = 'dash', line_color = 'firebrick')
            fig.update_layout(yaxis_title = 'Frecuencia')
        else:
            fig = px.histogram(df_aux, x = 'Precio (MXN)')
            fig.add_vline(x = rango_ab[0], line_dash = 'dash', line_color = 'firebrick')
            fig.add_vline(x = rango_ab[1], line_dash = 'dash', line_color = 'firebrick')
            fig.update_layout(yaxis_title = 'Frecuencia')
    else:
        df_aux = airbnb[airbnb['Municipio'] == mun]
        fig = px.histogram(df_aux, x = 'Precio (MXN)')
        fig.add_vline(x = rango_ab[0], line_dash = 'dash', line_color = 'firebrick')
        fig.add_vline(x = rango_ab[1], line_dash = 'dash', line_color = 'firebrick')
        fig.update_layout(yaxis_title = 'Frecuencia')
    
    fig2 = px.histogram(hoteles, x = 'Precio (MXN)')
    fig2.add_vline(x = rango_hot[0], line_dash = 'dash', line_color = 'firebrick')
    fig2.add_vline(x = rango_hot[1], line_dash = 'dash', line_color = 'firebrick')
    fig2.update_layout(yaxis_title = 'Frecuencia')
    
    df_filtro_precio = df_aux[(df_aux['Precio (MXN)'] >= rango_ab[0]) & (df_aux['Precio (MXN)'] <= rango_ab[1])]
    
    tipo_hab = df_filtro_precio['Tipo Habitacion'].unique()
    tipo_hab.sort()
    
    tipo_renta = df_filtro_precio['Tipo renta'].unique()
    tipo_renta.sort()
    
    hab_comun = df_filtro_precio['Tipo Habitacion'].value_counts().idxmax()
    rent_comun = df_filtro_precio['Tipo renta'].value_counts().idxmax()
    
    df_hotel = hoteles[(hoteles['Precio (MXN)'] >= rango_hot[0]) & (hoteles['Precio (MXN)'] <= rango_hot[1])]
    
    municipio_comun = df_hotel['Municipio'].value_counts().idxmax()
    
    contenido_est_ab = [
        dbc.CardBody([
            html.H4('Estadisticas AIRBNB'),
            html.H6('Precio promedio: $ {} (MXN)'.format(round(df_filtro_precio['Precio (MXN)'].mean(), 2))),
            html.H6('Numero de huespedes promedio: {}'.format(int(round(df_filtro_precio['# Huespedes'].mean(), 0)))),
            html.H6('Tipo de habitacion más común: {}'.format(hab_comun)),
            html.H6('Tipo de renta más común: {}'.format(rent_comun))
            ])
        ]
    
    contenido_est_hot = [
        dbc.CardBody([
            html.H4('Estadisticas Hoteles'),
            html.H6('Precio promedio: $ {} (MXN)'.format(round(df_hotel['Precio (MXN)'].mean(), 2))),
            html.H6('Municipio con más hoteles: {}'.format(municipio_comun))
            #html.H6('Tipo de renta más común: {}'.format(rent_comun))
            ])
        ]
    
    contenido_check_ab = [
        dbc.CardBody([
            html.H3('Filtros para airbnb', style = {'textAlign' : 'center'}),
            dbc.Row([
                dbc.Col([
                    html.H4('Tipo de habitacion', style = {'textAlign' : 'center'}),
                    dcc.RadioItems(id = 'list_airbnb_habitacion',
                                  options = [{'label' : i, 'value' : i} for i in tipo_hab],
                                  inline = False,
                                  labelStyle = {'display': 'block'})
                    ]),
                dbc.Col([
                    html.H4('Tipo de renta', style = {'textAlign' : 'center'}),
                    dcc.RadioItems(id = 'list_airbnb_renta',
                                  options = [{'label' : i, 'value' : i} for i in tipo_renta],
                                  inline = False,
                                  labelStyle = {'display': 'block'})
                    ])
                ])
            ])
        ]
    

    return fig, fig2, contenido_est_ab, contenido_est_hot, contenido_check_ab

#Modificacion de los selectores, resultado de los filtros ingresados (dropdown, slider, radioitems)
@app.callback([Output('selector_ab', 'children'), 
               Output('selector_hot', 'children')], 
              [Input('dropdown', 'value'), 
                Input('slider_airbnb', 'value'), 
                Input('slider_hoteles', 'value'),
                Input('list_airbnb_habitacion', 'value'), 
                Input('list_airbnb_renta', 'value')])
def selectores(mun, rango_ab, rango_hot, hab, rent):
    if mun == 'Todos':
        df_aux = airbnb
    else:
        df_aux = airbnb[airbnb['Municipio'] == mun]
    
    df_filtro_precio = df_aux[(df_aux['Precio (MXN)'] >= rango_ab[0]) & (df_aux['Precio (MXN)'] <= rango_ab[1])]
    df_resultado = df_filtro_precio[(df_filtro_precio['Tipo Habitacion'] == hab) & (df_filtro_precio['Tipo renta'] == rent)]
    lista_filtrada = df_resultado['Nombre']
    
    df_hotel = hoteles[(hoteles['Precio (MXN)'] >= rango_hot[0]) & (hoteles['Precio (MXN)'] <= rango_hot[1])]
    nombre_hotel = df_hotel['Nombre'].unique()
    nombre_hotel.sort()
    
    selector_ab = [
        dbc.CardBody([
            html.H4('Lista de airbnb'),
            dcc.Dropdown(id = 'dropdown_airbnb_habitacion',
                          options = [{'label' : i, 'value' : i} for i in lista_filtrada],
                          placeholder = 'Airbnb')
            ])
        ]
    
    selector_hot = [
        dbc.CardBody([
            html.H4('Lista de hoteles'),
            dcc.Dropdown(id = 'dropdown_hotel_nombre',
                          options = [{'label' : i, 'value' : i} for i in nombre_hotel],
                          placeholder = 'Hoteles')
            ])
        ]
    
    return selector_ab, selector_hot

#Regreso de informacion y mapa de la eleccion final
@app.callback([Output('info_ab', 'children'), 
               Output('info_hot', 'children'),
               Output('map_airbnb', 'srcDoc'),
               Output('map_hoteles', 'srcDoc')], 
              [Input('dropdown_airbnb_habitacion', 'value'), 
               Input('dropdown_hotel_nombre', 'value')])

def resultado(elemento_ab, elemento_hot):
    df_resultados_ab = airbnb.drop(['Tipo Habitacion', 'Tipo renta', 'Municipio', 'Latitud', 'Longitud', 'Precio p/per (MXN)', 'Precio p/per (USD)'], axis = 1)
    x = df_resultados_ab.loc[df_resultados_ab['Nombre'] == elemento_ab]
    
    df_resultados_hot = hoteles.drop(['Municipio', 'Latitud', 'Longitud'], axis = 1)
    y = df_resultados_hot.loc[df_resultados_hot['Nombre'] == elemento_hot]
    
    card_ab = [
        dbc.CardBody([
            dbc.Table.from_dataframe(x, striped=True, bordered=True, hover=True, size = 'md')
            ])
        ]
    
    card_hot = [
        dbc.CardBody([
            dbc.Table.from_dataframe(y, striped=True, bordered=True, hover=True, size = 'md')
            ])
        ]
    
    try:
        generador_mapa_ab(elemento_ab)
        generador_mapa_hot(elemento_hot)
    except:
        pass
    
    ruta_mapa_ab = 'assets/'
    ruta_mapa_ab += elemento_ab 
    ruta_mapa_ab += '.html'
    
    ruta_mapa_hot = 'assets/'
    ruta_mapa_hot += elemento_hot
    ruta_mapa_hot += '.html'
    
    return card_ab, card_hot, open(ruta_mapa_ab, 'r').read(), open(ruta_mapa_hot, 'r').read()
    
#Ejecucion del dashboard
if __name__ == '__main__':
    app.run_server()