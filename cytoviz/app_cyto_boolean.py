import dash
import dash_cytoscape as cyto
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-elements-boolean',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=[
            {
                'data': {'id': 'one', 'label': 'Locked'},
                'position': {'x': 75, 'y': 75},
                'locked': True
            },
            {
                'data': {'id': 'two', 'label': 'Selected'},
                'position': {'x': 75, 'y': 200},
                'selected': True
            },
            {
                'data': {'id': 'three', 'label': 'Not Selectable'},
                'position': {'x': 200, 'y': 75},
                'selectable': False
            },
            {
                'data': {'id': 'four', 'label': 'Not grabbable'},
                'position': {'x': 200, 'y': 200},
                'grabbable': False
            },
            {'data': {'source': 'one', 'target': 'two'}},
            {'data': {'source': 'two', 'target': 'three'}},
            {'data': {'source': 'three', 'target': 'four'}},
            {'data': {'source': 'two', 'target': 'four'}},
        ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
