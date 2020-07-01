import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
cyto.load_extra_layouts()

import dash_reusable_components as drc

import os
import zkextract
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

asset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'assets'
)

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                assets_folder=asset_path)
server = app.server


# ###################### DATA PREPROCESSING ######################
# Load data
zettel_path = '/Users/hubert/Nextcloud/Personal/Zettelkasten/'

zettels = zkextract.list_zettels(zettel_path)
docs = zkextract.parse_zettels(zettels)
# elements = zkextract.create_graph(docs)

print('zettels successfully loaded')

# Define follower/following relations
nodes = set()

following_node_di = {}  # user id -> list of users they are following
following_edges_di = {}  # user id -> list of cy edges starting from user id

followers_node_di = {}  # user id -> list of followers (cy_node format)
followers_edges_di = {}  # user id -> list of cy edges ending at user id

cy_edges = []
cy_nodes = []

for zkn_id, zettel in docs.items():

    source = zkn_id
    cy_source = {"data": {"id": source, "label": zettel['title'], 'text': zettel['text']}}

    for target in zettel['links']:
        cy_edge = {'data': {'id': source+target, 'source': source, 'target': target}}
        cy_edges.append(cy_edge)
        cy_target = {"data": {"id": target,
                     "label": docs[target]['title']}}

        if source not in nodes:
            nodes.add(source)
            cy_nodes.append(cy_source)
        if target not in nodes:
            nodes.add(target)
            cy_nodes.append(cy_target)

        # Process dictionary of following
        if not following_node_di.get(source):
            following_node_di[source] = []
        if not following_edges_di.get(source):
            following_edges_di[source] = []

        following_node_di[source].append(cy_target)
        following_edges_di[source].append(cy_edge)

        # Process dictionary of followers
        if not followers_node_di.get(target):
            followers_node_di[target] = []
        if not followers_edges_di.get(target):
            followers_edges_di[target] = []

        followers_node_di[target].append(cy_source)
        followers_edges_di[target].append(cy_edge)

genesis_node = cy_nodes[0]
genesis_node['classes'] = "genesis"
default_elements = cy_nodes

default_stylesheet = [
    {
        "selector": 'node',
        'style': {
            "opacity": 0.65,
            'z-index': 9999
        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.45,
            'z-index': 5000
        }
    },
    {
        'selector': '.followerNode',
        'style': {
            'background-color': '#0074D9'
        }
    },
    {
        'selector': '.followerEdge',
        "style": {
            "mid-target-arrow-color": "blue",
            "mid-target-arrow-shape": "vee",
            "line-color": "#0074D9"
        }
    },
    {
        'selector': '.followingNode',
        'style': {
            'background-color': '#FF4136'
        }
    },
    {
        'selector': '.followingEdge',
        "style": {
            "mid-target-arrow-color": "red",
            "mid-target-arrow-shape": "vee",
            "line-color": "#FF4136",
        }
    },
    {
        "selector": '.genesis',
        "style": {
            'background-color': '#B10DC9',
            "border-width": 2,
            "border-color": "purple",
            "border-opacity": 1,
            "opacity": 1,

            "label": "data(label)",
            "color": "#B10DC9",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    },
    {
        'selector': ':selected',
        "style": {
            "border-width": 2,
            "border-color": "black",
            "border-opacity": 1,
            "opacity": 1,
            "label": "data(label)",
            "color": "black",
            "font-size": 12,
            'z-index': 9999
        }
    }
]


# ################################# APP LAYOUT ################################
styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 80px)'}
}

app.layout = html.Div([
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=cy_edges + cy_nodes,
            style={
                'height': '95vh',
                'width': '100%'
            }
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Control Panel', children=[
                drc.NamedDropdown(
                    name='Layout',
                    id='dropdown-layout',
                    options=drc.DropdownOptionsList(
                        'random',
                        'grid',
                        'circle',
                        'concentric',
                        'breadthfirst',
                        'cose',
                        'cose-bilkent',
                        'dagre',
                        'cola',
                        'klay',
                        'spread',
                        'euler'
                    ),
                    value='grid',
                    clearable=False
                ),

                drc.NamedDropdown(
                    name='Node Shape',
                    id='dropdown-node-shape',
                    value='ellipse',
                    clearable=False,
                    options=drc.DropdownOptionsList(
                        'ellipse',
                        'triangle',
                        'rectangle',
                        'diamond',
                        'pentagon',
                        'hexagon',
                        'heptagon',
                        'octagon',
                        'star',
                        'polygon',
                    )
                ),

                drc.NamedInput(
                    name='Followers Color',
                    id='input-follower-color',
                    type='text',
                    value='#0074D9',
                ),

                drc.NamedInput(
                    name='Following Color',
                    id='input-following-color',
                    type='text',
                    value='#FF4136',
                ),
            ]),

            dcc.Tab(label='JSON', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Node Object JSON:'),
                    html.Pre(
                        id='tap-node-json-output',
                        style=styles['json-output']
                    ),
                    html.P('Edge Object JSON:'),
                    html.Pre(
                        id='tap-edge-json-output',
                        style=styles['json-output']
                    )
                ])
            ])
        ]),
    ])
])

# ############################## CALLBACKS ####################################
@app.callback(Output('tap-node-json-output', 'children'),
              [Input('cytoscape', 'tapNode')])
def display_tap_node(data):
    return json.dumps(data, indent=2)


@app.callback(Output('tap-edge-json-output', 'children'),
              [Input('cytoscape', 'tapEdge')])
def display_tap_edge(data):
    return json.dumps(data, indent=2)


@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}


@app.callback(Output('cytoscape', 'stylesheet'),
              [Input('cytoscape', 'tapNode'),
               Input('input-follower-color', 'value'),
               Input('input-following-color', 'value'),
               Input('dropdown-node-shape', 'value')])
def generate_stylesheet(node, follower_color, following_color, node_shape):
    if not node:
        return default_stylesheet

    stylesheet = [{
        "selector": 'node',
        'style': {
            'opacity': 0.3,
            'shape': node_shape
        }
    }, {
        'selector': 'edge',
        'style': {
            'opacity': 0.2,
            "curve-style": "bezier",
        }
    }, {
        "selector": 'node[id = "{}"]'.format(node['data']['id']),
        "style": {
            'background-color': '#B10DC9',
            "border-color": "purple",
            "border-width": 2,
            "border-opacity": 1,
            "opacity": 1,

            "label": "data(label)",
            "color": "#B10DC9",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    }]

    for edge in node['edgesData']:
        if edge['source'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['target']),
                "style": {
                    'background-color': following_color,
                    'opacity': 0.9
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": following_color,
                    "mid-target-arrow-shape": "vee",
                    "line-color": following_color,
                    'opacity': 0.9,
                    'z-index': 5000
                }
            })

        if edge['target'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['source']),
                "style": {
                    'background-color': follower_color,
                    'opacity': 0.9,
                    'z-index': 9999
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": follower_color,
                    "mid-target-arrow-shape": "vee",
                    "line-color": follower_color,
                    'opacity': 1,
                    'z-index': 5000
                }
            })

    return stylesheet

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
