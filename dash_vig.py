#Importing libraries
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_table
import plotly.express as px

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)
server=app.server
app.layout = html.Div([
    # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    html.Div(
            [    html.H3(
                'Laos Energy model',
                style={"margin-bottom": "1px"},
                 ),
                 html.H5(
                "OSeMOSYS application",
                style={"margin-top": "0px"},
                 ),
            ],
            
            id="title",
            ),
    html.Hr(className='row'),
    html.Hr(className='row'),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Please uplaod the Result CSV for "total Capacity Annual" :  Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-div'),
    html.Div(id='output-datatable'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.Button(id="submit-button", children="Create Graph"),
        html.Hr(),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'))

def make_graphs(n, data):
    if n is None:
        return dash.no_update
    else:
        #d1=data[(data['t'].str[:3]=="PWR")]
        #print(data[2])
        #filtered_data = []
        #for index in range(len(data)):
         #   for key in data[index]:
          #      print(key)
           #     print(data[index][key])
        totalcapacityannual=pd.DataFrame(data)
        totalcapacityannual=totalcapacityannual[(totalcapacityannual['t'].str[:3]=="PWR") 
                                                 & (totalcapacityannual['t'].str[3:6]!=("TRN")) 
                                                 & (totalcapacityannual['t'].str[3:6]!=("DIS"))].copy()
        totalcapacityannual.drop(('r'),axis=1,inplace=True)
        bar_fig= px.bar(totalcapacityannual, x='y', y='TotalCapacityAnnual', width=1200, height=400, color='t', barmode='stack',title="Total Annual Capacity_Lao PDR-GW")
        # print(data)
        return dcc.Graph(figure=bar_fig)



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
