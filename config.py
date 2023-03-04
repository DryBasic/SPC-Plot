FIGURE_LAYOUT = {
    'default': {
        'template':'plotly_dark+ygridoff+xgridoff'
    },
    'light': {
        'template':'plotly_white+ygridoff+xgridoff'
    },
    'dark': {
        'template':'plotly_dark+ygridoff+xgridoff'
    },
}
PLOT_LAYOUT = {
    'default': {
        'height': 200,
        'margin': {'t': 2, 'b': 2, 'l': 2, 'r': 2,'pad':2,'autoexpand':True},
        #'font': {'size': 8, 'color': 'white'},
        #'paper_bgcolor': '#9eb3ba',
        'plot_bgcolor': 'black',
        'showlegend': False,
        'xaxis':{'zeroline':False},
        'yaxis':{'zeroline':False}
    },
    'light': {
        'height': 200,
        'margin': {'t': 2, 'b': 2, 'l': 2, 'r': 2,'pad':2,'autoexpand':True},
        'font': {'color': 'black'},
        'plot_bgcolor': 'black',
        'showlegend': False,
        'xaxis':{'zeroline':False},
        'yaxis':{'zeroline':False}
    },
    'dark': {
        'height': 200,
        'margin': {'t': 2, 'b': 2, 'l': 2, 'r': 2,'pad':2,'autoexpand':True},
        'font': {'color': 'white'},
        'plot_bgcolor': 'white',
        'showlegend': False,
        'xaxis':{'zeroline':False},
        'yaxis':{'zeroline':False}
    },
}
SCATTER_STYLE = {
    'default': {
        'name': '',
        'line':{'color':'black', 'dash':'solid','width':1},
        'mode':'lines+markers',
    },
    'light': {
        'name': '',
        'line':{'color':'black', 'dash':'solid','width':1},
        'mode':'lines+markers',
    },
    'dark': {
        'name': '',
        'line':{'color':'black', 'dash':'solid','width':1},
        'mode':'lines+markers',
    }
}
ANNOTATED_LINE_STYLE = {
    'default': {
        'line_dash': 'dot',
        'line_color': 'black'
        #'line_color': '#adadad',
    },
    'spec': {
        'line_dash': 'dash',
        'line_color': 'black'
    },
    'light': {
        'line_dash': 'dot',
        'line_color': 'black',
        'annotation_bgcolor': 'white',
        'annotation_bordercolor': 'black',
        'annotation_font': {
            'color': 'black'
        }
    },
    'dark': {
        'line_dash': 'dot',
        'line_color': 'white',
        'annotation_bgcolor': 'black',
        'annotation_bordercolor': 'white',
        'annotation_font': {
            'color': 'white'
        }
    },
}
SHAPE_LAYOUT = {
    'default': {
        'opacity': 1.0,
        'layer': 'below',
        'line_width':0,
    },
}
CUSTOMDATA = {
    'generic': [
        'Lot Number',
        'name',
        'Comment',
        'Issues Observed',
    ],
    'violation':'',
}

HOVERTEMPLATE = {
    'generic': '<br>'.join([
                'y-value: %{y:.2f}',
                'Lot: %{customdata[0]}',
                'MN: %{customdata[1]}',
                'Comment: %{customdata[2]}',
                'Issues Observed: %{customdata[3]}'
            ]),
    'violation': '',
}
COLORS = {
    'classic': {
        'zone0':'#B8EEBE',
        'zone1':'#FFF1C8',
        'zone2':'#F2AFB1',
        'Mean': 'gray'
    },
    'striking': {
        'zone0':'green',
        'zone1':'yellow',
        'zone2':'red',
        'Mean':'black'
    },
    'blues': {
        'zone0':'#9dddf5',
        'zone1':'#89f0df',
        'zone2':'#727bfc',
        'Mean':'black'
    },
    'iceberg': { 
        'zone0':'white',
        'zone1':'#3cc3e8',
        'zone2':'#356ccc',
        'Mean':'black'
    },
    'unicorn' : {
        'zone0':'#bbeefc',
        'zone1':'white',
        'zone2':'#f5a2dc',
        'Mean':'black'
    },
    'white': {
        'zone0':'white',
        'zone1':'white',
        'zone2':'white',
        'Mean': 'black'
    },
    'black': {
        'zone0':'black',
        'zone1':'black',
        'zone2':'black',
        'Mean':'black'
    },
    'grays': {
        'zone0':'#ddd',
        'zone1':'#c2c2c2',
        'zone2':'#aaa',
        'Mean':'black'
    }
}