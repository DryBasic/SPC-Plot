FIGURE_LAYOUT = {
    'default': {
        'template': 'plotly_dark+ygridoff+xgridoff'
    },
}

PLOT_LAYOUT = {
    'default': {
        'height': 188,
        'margin': {'t': 0, 'b': 0, 'l': 0, 'r': 0},
        # 'font': {'size': 8, 'color': 'white'},
        # 'paper_bgcolor': '#9eb3ba',
        # 'plot_bgcolor': '#F0F0F0',
        'showlegend': False,
        'xaxis_visible': False,
        'xaxis_zeroline': False,
        'yaxis_zeroline': False,
    },
    'light': {},
    'dark': {
        'height': 188,
        'margin': {'t': 6, 'b': 12, 'l': 6, 'r': 6},
        'font': {
            # 'size': 8,
            'color': 'white'
        },
        # 'paper_bgcolor': '#4F5A67',
        # 'plot_bgcolor': '#F0F0F0',
        'showlegend': False
    },
}

SCATTER_STYLE = {
    'default': {
        'name': '',
        'line': {'color': 'black', 'dash': 'dot'},
        'mode': 'lines+markers',
    },
    'dark': {
        'name': '',
        'line': {'color': 'white', 'dash': 'dot'},
        'mode': 'lines+markers',
    }
}

ANNOTATED_LINE_STYLE = {
    'default': {
        'line_dash': 'solid',
        'line_color': 'gray',
        # 'annotation_bgcolor': '',
        # 'annotation_bordercolor': '',
        # 'annotation_font': {
        #     'color': ''
        # },
    }
}

SHAPE_LAYOUT = {
    'default': {
        'opacity': 1.0,
        'layer': 'below',
        'line_width': 0,
    },
}

CUSTOMDATA = {
    'generic': [
        'OrderNumber',
        'MaterialNumber',
        'StartDate',
        'EndDate'
    ],
    'violation': '',
}

HOVERTEMPLATE = {
    'generic': '<br>'.join([
                'y-value: %{y:.2f}',
                'Lot: %{customdata[0]}',
                'MN: %{customdata[1]}',
                'MFG Start: %{customdata[2]}',
                'MFG End: %{customdata[3]}'
            ]),
    'violation': '',
}

COLOR_SCHEME = {
    'Classic': {
        'zone0': '#B8EEBE',
        'zone1': '#FFF1C8',
        'zone2': '#F2AFB1',
        'line0': '#00AA44',
        'line1': '#FF0000',
        'mean':  '#444444'
    },
    'Glacial': {
        'zone0': '#FFFFFF',
        'zone1': '#3cc3e8',
        'zone2': '#356ccc',
        'line0': '#9dddf5',
        'line1': '#89f0df',
        'mean':  '#727bfc',
    },
    'Fairytale': {
        'zone0': '#B8FBC0',
        'zone1': '#FFF5BE',
        'zone2': '#FFC9E9',
        'line0': '#16EA94',
        'line1': '#F186D9',
        'mean':  '#00FFE0',
    },
    'Monochrome': {
        'zone0': '#DDDDDD',
        'zone1': '#C2C2C2',
        'zone2': '#AAAAAA',
        'line0': '#000000',
        'line1': '#000000',
        'mean':  '#000000',
    },
    'Out-of-Ink': {
        'zone0': '#FFFFFF',
        'zone1': '#FFFFFF',
        'zone2': '#FFFFFF',
        'line0': '#000000',
        'line1': '#000000',
        'mean':  '#000000',
    }
}