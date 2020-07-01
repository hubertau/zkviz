import dash
import dash_cytoscape as cyto
import dash_html_components as html

my_stylesheet = [
    # Group selectors
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },

    # Class selectors
    {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': '.triangle',
        'style': {
            'shape': 'triangle'
        }
    }
]

app = dash.Dash(__name__)

app.layout = html.Div([
    cyto.Cytoscape(
    id='cytoscape-elements-classes',
    layout={'name': 'preset'},
    style={'width': '100%', 'height': '400px'},
    stylesheet=my_stylesheet,
    elements=[
        {
            'data': {'id': 'one', 'label': 'Modified Color'},
            'position': {'x': 75, 'y': 75},
            'classes': 'red' # Single class
        },
        {
            'data': {'id': 'two', 'label': 'Modified Shape'},
            'position': {'x': 75, 'y': 200},
            'classes': 'triangle' # Single class
        },
        {
            'data': {'id': 'three', 'label': 'Both Modified'},
            'position': {'x': 200, 'y': 75},
            'classes': 'red triangle' # Multiple classes
        },
        {
            'data': {'id': 'four', 'label': 'Regular'},
            'position': {'x': 200, 'y': 200}
        },
        {'data': {'source': 'one', 'target': 'two'}, 'classes': 'red'},
        {'data': {'source': 'two', 'target': 'three'}},
        {'data': {'source': 'three', 'target': 'four'}, 'classes': 'red'},
        {'data': {'source': 'two', 'target': 'four'}},
    ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
