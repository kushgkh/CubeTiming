import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

arr = []
with open("times.txt") as times:
    for time in times:
        strTime = time.split("\"")[1]
        #print(strTime)
        numTime = 0
        if(":" in strTime):
            numTime += int(strTime.split(":")[0]) * 60
            strTime = strTime.split(":")[1]
        numTime+= float(strTime)
        arr.append(numTime)
        #print(numTime)
print(arr[:4])


fig = dict({
    "data": [{"type": "line",
             
              "y": arr}],
    "layout": {"title": {"text": "3x3 solve times"},
               "xaxis": {"title" : "Solve Number"},
               "yaxis": {"title" : "Seconds"}}
})


app.layout = html.Div([
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                dict(
                    x=df[df['continent'] == i]['gdp per capita'],
                    y=df[df['continent'] == i]['life expectancy'],
                    text=df[df['continent'] == i]['country'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.continent.unique()
            ],
            'layout': dict(
                xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                yaxis={'title': 'Life Expectancy'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ) ,

    dcc.Graph(figure = fig)
])




if __name__ == '__main__':
    app.run_server(debug=True)