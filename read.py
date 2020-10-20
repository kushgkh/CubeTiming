import base64
import datetime
import io

import dash
#import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import numpy as np

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
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
            'padding': '50px'
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
                'margin': '15px',
                },

                style={

                    'margin': '1% 40% 0% 50%',


                }

    ),


    html.Div(id='output-data-upload'),
     html.Div(id='output-data-hist'),
])



def timeToMilis(num):
    time = num.split(":")
    if(len(time) == 1):
        return int(float(time[0]) * 1000)
    return int((float(time[0]) * 60 + float(time[1])) * 1000)

def formatDigit(num ):
    if(num < 10 ):
        return "0" + str(num)
    return str(num)

def make_graphic(contents, filename, isCount):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:


        if 'txt' in filename:
            times = io.StringIO(decoded.decode('utf-8'))
            if 'cstimer' in filename:            
                for time in times:
                   output = json.loads(time)


                #Extract lists for penalty, time, scramble and date
                results = list(zip(*output["session2"]))


                #seperate penalty and time
                out2 = list(zip(*results[0]))


                #put them in dataframe
                df = pd.DataFrame({"Penalty": out2[0] , "Time": out2[1]})


                #Get total time using function
                def totalTime(row):
                    if(row["Penalty"] >= 0):
                        return row["Penalty"] + row["Time"]
                    else:
                        return -1
                df["TotTime"] = df.apply(totalTime , axis=1)


                #Complete df
                df["Scramble"] = results[1]
                df["Date"] = results[3]

                def toDatetime(time):
                    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                df["Date"] = pd.to_datetime(df["Date"].apply(toDatetime))



            else:
                arr = {"TotTime": [] , "Scramble": [] , "Date" :  []}
                with open("times.txt") as times:
                    for time in times:
                        parts = time.split(";")
                        arr["TotTime"].append(timeToMilis(parts[0].strip('\"')))
                        arr["Scramble"].append(parts[1].strip('\"'))
                        arr["Date"].append(parts[2].strip("\n").strip('\"'))
                

                df  = pd.DataFrame(arr)
                df["Date"] = pd.to_datetime(df["Date"])



            df['YearMonth'] = df['Date'].map(lambda x: str(x.year) + "-" + formatDigit(x.month))
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



def make_hist(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:


        if 'txt' in filename:
            times = io.StringIO(decoded.decode('utf-8'))
            if 'cstimer' in filename:            
                for time in times:
                   output = json.loads(time)


                #Extract lists for penalty, time, scramble and date
                results = list(zip(*output["session2"]))


                #seperate penalty and time
                out2 = list(zip(*results[0]))


                #put them in dataframe
                df = pd.DataFrame({"Penalty": out2[0] , "Time": out2[1]})


                #Get total time using function
                def totalTime(row):
                    if(row["Penalty"] >= 0):
                        return row["Penalty"] + row["Time"]
                    else:
                        return -1
                df["TotTime"] = df.apply(totalTime , axis=1)


                #Complete df
                df["Scramble"] = results[1]
                df["Date"] = results[3]

                def toDatetime(time):
                    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                df["Date"] = pd.to_datetime(df["Date"].apply(toDatetime))



            else:
                arr = {"TotTime": [] , "Scramble": [] , "Date" :  []}
                with open("times.txt") as times:
                    for time in times:
                        parts = time.split(";")
                        arr["TotTime"].append(timeToMilis(parts[0].strip('\"')))
                        arr["Scramble"].append(parts[1].strip('\"'))
                        arr["Date"].append(parts[2].strip("\n").strip('\"'))
                

                df  = pd.DataFrame(arr)
                df["Date"] = pd.to_datetime(df["Date"])



            df['YearMonth'] = df['Date'].map(lambda x: str(x.year) + "-" + formatDigit(x.month))
            grouped = df.groupby("YearMonth").mean()



            recent = df["TotTime"][-100:]/1000
            print(max(recent))
            #rangeo = np.range(0, max(recent), max(recent)//10)
            # counts, bins = np.histogram(recent, bins=range(0, max(recent), max(recent)//10))
            # print(counts)
            # print(bins)



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
              Input('yaxis-type' , 'value')],
              [State('upload-data', 'filename')]
              )
def update_output(list_of_contents, yLabel, list_of_names):
    if list_of_contents is not None:
        return make_graphic(list_of_contents[0] , list_of_names[0] , yLabel=="Count")

@app.callback(Output('output-data-hist', 'children'),
              [Input('upload-data', 'contents'),
              Input('yaxis-type' , 'value')],
              [State('upload-data', 'filename')]
              )
def update_hist(list_of_contents, yLabel, list_of_names):
    if list_of_contents is not None:
        return make_hist(list_of_contents[0] , list_of_names[0] )



if __name__ == '__main__':
    app.run_server(debug=True)