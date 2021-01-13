import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import numpy as np

import pandas as pd

from fileIO import getData , getColumnNames

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


colors = {
    'background': '#e9f5eb',
    'text': '##5a5a5a'
}

server = app.server

app.layout = html.Div(style={'backgroundColor': colors['background']} ,children= [
     html.H1(
        children='TwistyPlot',
        style={
            'textAlign': 'center',
        }
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drop or ',
            html.A('Browse')
        ]),
        style={
            'width': '50%',
            'height': '100px',
            'lineHeight': '100px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '5% 25% 0% 25%',
            'padding': '50px',
            'backgroundColor': '#f8f8f0',
            'fontSize': 50
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Count', 'Date']],
                value='Count',
                labelStyle={
                'display': 'inline-block',
                'margin': '10px',
                },

                style={

                    'margin': '1% 40% 0% 50%',
                }

    ),
    dcc.RadioItems(
                id='file-source',
                options=[{'label': i, 'value': i} for i in ['CSTimer', 'Twisty Timer']],
                value='CSTimer',
                labelStyle={
                'display': 'inline-block',
                'margin': '10px',
                },

                style={

                    'margin': '1% 40% 0% 50%',
                }

    ),
    dcc.Dropdown(
                id="my-dynamic-dropdown",
                style={

                    'margin': '0% 45% 0% 45%',
                }

                ),

    html.Div(id='output-data-upload',
        style={

            'backgroundColor': '#f8f8f0'
        }

    ),
    html.Div(id='output-data-hist'),
])












def make_graphic(contents, filename, isCount , sessionID , fileSource):
    try:
        df = getData(contents , fileSource , sessionID)
        grouped = df.groupby("YearMonth").mean()

        if(isCount):
            fig = dict({
                "data": [{"type": "line",
                        "y": df["TotTime"]/1000}],
                "layout": {"title": {"text": "3x3 solve times"},
                           "xaxis": {"title" : "Solve Number"},
                           "yaxis": {"title" : "Seconds"}}
            })
        else:
            fig = dict({
                "data": [{"type": "line",
                        "x" : grouped.index,
                        "y": grouped["TotTime"]/1000}],
                "layout": {"title": {"text": "3x3 solve times"},
                           "xaxis": {"title" : "Month"},
                           "yaxis": {"title" : "Seconds"}}
            })


    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
    dcc.Graph(figure = fig)])



def make_hist(contents, filename , sessionID , fileSource):
    try:
        df = getData(contents , fileSource , sessionID)
        grouped = df.groupby("YearMonth").mean()

        recent = df["TotTime"][-100:]/1000
        print(max(recent))

       # fig = px.histogram(df, x="TotTime")
        fig = dict({
            "data": [{"type": "histogram",
                    "x": df["TotTime"][-100:]/1000}],
            "layout": {"title": {"text": "3x3 solve times histogram"},
                       "xaxis": {"title" : "Seconds"},
                       "yaxis": {"title" : "Count"}}
        })
          

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
    dcc.Graph(figure = fig)])



@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
              Input('yaxis-type' , 'value'),
              Input("my-dynamic-dropdown", "value")],
              [State('upload-data', 'filename'),
              State('file-source', 'value')])
def update_output(list_of_contents, yLabel, sessionID, list_of_names , fileSource):
    print("Hello")
    if list_of_contents is not None:
        return make_graphic(list_of_contents[0] , list_of_names[0] , yLabel=="Count" ,  sessionID , fileSource)

@app.callback(Output('output-data-hist', 'children'),
              [Input('upload-data', 'contents'),
              Input('yaxis-type' , 'value'),
              Input("my-dynamic-dropdown", "value")],
              [State('upload-data', 'filename'),
              State('file-source', 'value')])
def update_hist(list_of_contents, yLabel, sessionID , list_of_names , fileSource):
    print(sessionID)
    if list_of_contents is not None:
        return make_hist(list_of_contents[0] , list_of_names[0] , sessionID , fileSource)


defaultOptions = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montreal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
]


@app.callback(Output("my-dynamic-dropdown", "options"),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename') , 
              State('file-source', 'value')])
def update_options(list_of_contents, list_of_names , fileSource):
    if list_of_contents is not None and fileSource == "CSTimer":
        names = getColumnNames(list_of_contents[0])
        options = []
        for name in names[:-1]:
            options.append({"label":name , "value" : name})
        return [o for o in options]
    return [o for o in defaultOptions]



if __name__ == '__main__':
    app.run_server(debug=True)