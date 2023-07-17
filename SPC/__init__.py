import plotly.graph_objs as go
import pandas as pd
import numpy as np
from copy import deepcopy
from . import config as cfg
from .anomaly_detector import AnomalyDetector

presets = dict(
    FIGURE_LAYOUT=cfg.FIGURE_LAYOUT,
    PLOT_LAYOUT=cfg.PLOT_LAYOUT,
    SCATTER_STYLE=cfg.SCATTER_STYLE,
    ANNOTATED_LINE_STYLE=cfg.ANNOTATED_LINE_STYLE,
    SHAPE_LAYOUT=cfg.SHAPE_LAYOUT,
    CUSTOMDATA=cfg.CUSTOMDATA,
    HOVERTEMPLATE=cfg.HOVERTEMPLATE,
    COLOR_SCHEME=cfg.COLOR_SCHEME
)


class SPCPlot:
    """This class holds shortcuts for creating 'plotly' figures annotated with SPC elements. Style presets can be
    created and modified via the `presets` dictionary.

    - *df*: dataframe containing the series you will plot
    - *y*: the column name of the series you will plot
    - *control_sidedness*: options are 'two', 'one_upper', and 'one_lower'; specifies if your controls are one or two-sided; if one-sided, which half has controls
    - *spec_limits*: draws spec lines using the draw_lines method. USL and LSL must be the keys of the passed dictionary to be used in capability calculations.
    - *fig_layout*: style options for the Plotly Figure object. Can either specify the name of a preset,
    or pass a dictionary with custom options. You can create your own presets by modifying the SPC.presets dictionary like rcParams in matplotlib.
    - *global_custom*: under construction

    Class Attributes:
    - *fig*: Plotly Figure object
    - *df*: the passed Pandas dataframe
    - *x*: the index of the passed dataframe
    - *y*: series from passed dataframe using label specified as `y`
    - *mean*: mean of y
    - *std*: standard deviation of y
    - *min*: min of y
    - *max*: max of y
    - *sides*: value passed as `control_sidedness`
    - *LSL*:
    - *USL*:
    - *UCL*: Upper Control Limit for y
    - *LCL*: Lower Control Limit for y
    - *L1s*: one stdev below y's mean
    - *U1s*: one stdev above y's mean
    - *zones*: y-value ranges for SPC shading
    - *violations*: series containing list of rule violations per df index
    """

    def __init__(self, df: pd.DataFrame, y: str,
                 control_sidedness: str = 'two',
                 spec_limits: dict = None,
                 fig_layout: dict | str = 'default',
                 violations: list = [1, 2, 3, 4, 5, 6, 7, 8],
                 color_scheme: dict | str = 'Classic'
                 ):

        # to be modified by methods
        self.hovertemplate = None
        self.customdata = None

        # Exception handling
        if control_sidedness not in ('two', 'one_upper', 'one_lower'):
            raise ValueError('`control_sidedness` must be "two", "one_lower", or "one_upper"')

        if isinstance(fig_layout, str):
            fig_layout = presets['FIGURE_LAYOUT'][fig_layout]
        elif not isinstance(fig_layout, dict):
            raise ValueError('`fig_layout` must be either a key pointing to an existing preset, or a dictionary '
                             'conforming to the Plotly Figure Layout requirements.')

        if isinstance(color_scheme, str):
            self.color_scheme = presets['COLOR_SCHEME'][color_scheme]
        elif isinstance(color_scheme, dict):
            self.color_scheme = color_scheme

        self.fig = go.Figure(layout=fig_layout)
        self.df = df
        self.x = df.reset_index().index  # force start at zero and increment by one. Expects ordered data.
        self.y = df[y]       # used in lieu of self.df[self.y_label] later on
        self.y_label = y     # for hover labels

        self.mean = self.y.mean()
        self.std = self.y.std()
        self.min = self.y.min()
        self.max = self.y.max()

        self.sides = control_sidedness

        self.UCL = self.mean + 3 * self.std
        self.LCL = self.mean - 3 * self.std
        self.L1s = self.mean - self.std  # one sigma lower
        self.U1s = self.mean + self.std  # one sigma upper

        # arbitrary constant used to set visual limits
        spacer = self.UCL - self.mean

        self.zones = {
            '+2': (self.UCL, self.UCL+5*spacer),
            '+1': (self.U1s, self.UCL),
            '0' : (self.L1s, self.U1s),
            '-1': (self.LCL, self.L1s),
            '-2': (self.LCL-5*spacer, self.LCL)
        }
        if self.sides == 'one_lower':
            del self.zones['+2']
            del self.zones['+1']
            self.zones['0'][1] = self.max + 4 * self.mean

        elif self.sides == 'one_upper':
            del self.zones['-2']
            del self.zones['-1']
            self.zones['0'][0] = self.min - 4 * self.mean

        # older min max based
        # view = (self.max - self.min) / 2
        # yrange = [self.min - view, view + self.max]
        # yrange[0] = 0 if yrange[0] < 0 else yrange[0]

        # centers around mean, shows fraction of red zone
        yrange = [self.LCL - spacer*0.25, self.UCL + spacer*0.25]

        if self.sides == 'one_upper':
            yrange[0] = self.min
        elif self.sides == 'one_lower':
            yrange[1] = self.max

        self.fig.update_yaxes(range=yrange)
        self.fig.update_xaxes(range=[-self.x[-1]*0.01, self.x[-1]*1.15])

        self.LSL = spec_limits.get('LSL') if spec_limits else None
        self.USL = spec_limits.get('USL') if spec_limits else None

        if spec_limits:
            self.draw_lines(annotated_hline_y=spec_limits,
                            show_value=True, line_style='spec')

        try:
            self.detector = AnomalyDetector(self.y)
            self.detector.apply_rules(violations)
            self.violations = self.detector.violations()
        except Exception as e:
            self.violations = 'Issue encountered: ' + str(e)

    def draw_scatter(self,
                     scatter_style='default',
                     plot_layout='default',
                     hovertemplate='default'):
        """Add scatter plot trace onto the figure. Uses data specified in the constructor as "y." Hoverlabels are assigned and created by referencing the settings defined in 'config.py.'

        custom options: scatter_opts, plot_layout, hovertemplate
        """

        if isinstance(scatter_style, str):
            scatter_style = presets['SCATTER_STYLE'][scatter_style]
        if isinstance(plot_layout, str):
            plot_layout = presets['PLOT_LAYOUT'][plot_layout]

        n = 6 if len(self.df.columns) > 6 else len(self.df.columns)
        customdata = np.stack(
            ([self.df[col] for col in list(self.df.columns)[:n]]),
            axis=-1)

        if hovertemplate == 'default':
            hovertemplate = '<br>'.join([f"Index: %{{x}}"] +
                                            # f"{self.y_label}: %{{y}}"] +
                                        [
                                            f"{col}: %{{customdata[{i}]}}"
                                            for i, col in enumerate(
                                            list(self.df.columns)[:n])
                                        ]
                                        )
        else:
            cols = cfg.CUSTOMDATA[hovertemplate]
            hovertemplate = cfg.HOVERTEMPLATE[hovertemplate]
            customdata = np.stack(([self.df[col] for col in cols]), axis=-1)

        # copy template for violations drawing
        self.customdata = customdata
        self.hovertemplate = hovertemplate

        self.fig.add_trace(go.Scatter(
            x=self.x, y=self.y, **scatter_style,
            customdata=customdata, hovertemplate=hovertemplate,
        ))

        self.fig.update_layout(**plot_layout)

    def draw_spc_zones(self, shape_layout='default'):
        """Draw shaded regions corresponding to standard deviations around the mean
        """
        shape_layout = cfg.SHAPE_LAYOUT[shape_layout]

        for zone, limits in self.zones.items():
            fillcolor = self.color_scheme['zone' + zone[-1]]
            y0, y1 = limits
            self.fig.add_hrect(
                fillcolor=fillcolor,
                y0=y0, y1=y1,
                **shape_layout
            )

    def draw_lines(self, show_value: bool = True, line_style: dict | str = 'default'):
        """Annotate the figure with lines. Specifying no arguments will draw the standard lines associated with SPC charts.

        - *show_value*: for annotated lines, add "(value)" to the end of the label; rounded to 2 decimal places
        - *line_style*: style arguments for line style (plotly line arguments or kw bound to config's ANNOTATED_LINE_STYLE)
        """

        if isinstance(line_style, str):
            line_style = presets['ANNOTATED_LINE_STYLE'][line_style]

        stats = {
            'Mean': self.mean,
            '-1S': self.L1s,
            '+1S': self.U1s,
            'UCL': self.UCL,
            'LCL': self.LCL
        }
        stat_2_line = {
            'Mean': 'mean',
            '-1S': 'line0',
            '+1S': 'line0',
            'UCL': 'line1',
            'LCL': 'line1'
        }
        if self.sides == 'one_upper':
            del stats['-1S']
            del stats['LCL']
        elif self.sides == 'one_lower':
            del stats['+1S']
            del stats['UCL']

        hlines = {v: k for k, v in stats.items()}
        if hlines:
            for y_value, label in hlines.items():
                line_style['line_color'] = self.color_scheme[stat_2_line[label]]
                line_style['line_dash'] = 'solid'
                if show_value and label:
                    label = f'{label} ({round(y_value, 2)})'
                self.fig.add_hline(y=y_value, annotation_text=label, **line_style)

    def draw_violations(self):
        if type(self.violations) != str and self.customdata is not None:
            # adapted from Stack Overflow a while back, might be a cleaner way
            cd = self.customdata[self.violations.index]
            arr_v = np.array([self.violations])
            a, b = arr_v.shape
            arr_v.resize(b, a)
            customdata = np.concatenate((cd, arr_v), axis=1)

            n = str(customdata.shape[1] - 1)
            prefix = f'Violated Rules: %{{customdata[{n}]}}<br>'
            hovertemplate = prefix + self.hovertemplate

            self.fig.add_trace(
                go.Scatter(
                    name='Control Violation',
                    x=(x := self.violations.index),
                    y=self.y.loc[x],
                    mode='markers',
                    marker=dict(
                        symbol='x-thin',
                        line_width=3,
                        line_color='red',
                        size=10
                    ),
                    customdata=customdata,
                    hovertemplate=hovertemplate
                )
            )

    def capability(self):
        if any((self.LSL, self.USL)):
            cp = {
                'mean': self.mean,
                'LCL': self.LCL,
                'UCL': self.UCL,
                'Process Width': self.UCL - self.LCL,
                'LSL': self.LSL,
                'USL': self.USL
            }
            # two-sided specs
            if all((self.LSL, self.USL)):
                cp['Spec Width'] = self.USL - self.LSL
                cp['Cp Lower'] = (self.mean - self.LSL) / (self.mean - self.LCL)
                cp['Cp Upper'] = (self.USL - self.mean) / (self.UCL - self.mean)

            # one-sided, lower spec
            elif self.LSL:
                cp['Spec Width'] = self.mean - self.LSL

            # one-sided, upper spec
            elif self.USL:
                cp['Spec Width'] = self.USL - self.mean
            cp['Cp'] = cp['Spec Width'] / cp['Process Width']
            return cp
