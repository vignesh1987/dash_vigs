import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io

# Create a new Dash app
app = dash.Dash(__name__)
server=app.server
# Define the layout of the app
app.layout = html.Div([
    # Add a file upload component to the app
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow users to upload a single file
        multiple=False
    ),
    # Display the contents of the uploaded file to the user
    html.Div(id='output-data-upload')
])

# Define a function to parse the contents of the uploaded file
def parse_contents(contents, filename):
    # Split the contents of the file into a content type and a content string
    content_type, content_string = contents.split(',')

    # Decode the content string into bytes
    decoded = base64.b64decode(content_string)
    
    try:
        # If the file is a CSV file, read it into a pandas DataFrame
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        # If the file is an Excel file, read it into a pandas DataFrame
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        # If there is an error reading the file, display an error message
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # Display the contents of the file to the user
    return html.Div([
        html.H5(filename),
        html.Hr(),
        html.Div([
            dcc.Markdown('### Raw Content'),
            html.Pre(df.head().to_markdown())
        ])
    ])

# Define a callback function to update the contents of the output component when a file is uploaded
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        # If a file has been uploaded, call the parse_contents function to process it
        children = [
            parse_contents(contents, filename)
        ]
        return children

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
