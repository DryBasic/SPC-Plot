import pandas as pd
import numpy as np
import plotly.graph_objs as go
from copy import deepcopy

from config import *

class Plot:
    '''This class holds shortcuts for creating 'plotly' figures annotated with SPC elements. Uses settings defined in 'config.py.'
    
    - *df*: dataframe containing the series you will plot
    - *y*: the column name of the series you will plot
    - *control_sidedness*: options are 'two', 'one_upper', and 'one_lower'; specifies if your controls are one or two-sided; if one-sided, which half has controls
    - *spec_limits*: draws spec lines using the draw_lines method. USL and LSL must be the keys of the passed dictionary to be used in capability calculations.
    - *fig_layout*: style options for the plotly Figure object
    - *global_custom*: under construction
    - *exclude*: the column name which contains a boolean marker of whether or not the record should be excluded (True = exclude) in the control calculations (will not remove points from figure)
    
    
    Class Attributes:
    - *global_style*:
    - *fig*:
    - *df*:
    - *x*: the index of the passed dataframe
    - *y*: series from passed dataframe using label specified as `y`
    - *mean*: mean of y
    - *dev*: standard deviation of y
    - *min_*: min of y
    - *max_*: max of y
    - *sides*: value passed as `control_sidedness`
    - *LSL*:
    - *USL*:
    - *UCL*: Upper Control Limit for y
    - *LCL*: Lower Control Limit for y
    - *L1s*: one stdev below y's mean
    - *U1s*: one stdev above y's mean
    - *zones*: y-value ranges for SPC shading
    - *violations*: series containing list of rule violations per df index
    '''
    def __init__(self, df:pd.DataFrame, y:str,
                 control_sidedness:str='two',
                 spec_limits:dict=None,
                 fig_layout:dict='default',
                 violations:list=[1,2,3,4,5,6,7,8],
                 exclude=None):
        
        # Exception handling
        if control_sidedness not in ('two','one_upper','one_lower'):
            raise Exception('`control_sidedness` must be two, one_lower, or one_upper')     
        
        fig_layout = FIGURE_LAYOUT[fig_layout]
              
        self.fig = go.Figure(layout=fig_layout)
        self.df  = df
        self.x   = df.index
        self.y   = df[y]
        
        # for hover labels...
        self.y_label = y
        
        if exclude:
            excluded = df[df[exclude].isna()][y]
            self.mean = excluded.mean()
            self.dev  = excluded.std()
            self.min_ = excluded.min()
            self.max_ = excluded.max()
        
        else:
            self.mean = self.y.mean()
            self.dev  = self.y.std()
            self.min_ = self.y.min()
            self.max_ = self.y.max()
        
        self.sides = control_sidedness
        
        self.UCL = self.mean + 3*self.dev
        self.LCL = self.mean - 3*self.dev
        self.L1s = self.mean - self.dev # one sigma lower
        self.U1s = self.mean + self.dev # one sigma upper

        self.zones = {
            '+2': (self.UCL,self.max_+4*self.mean),
            '+1': (self.U1s,self.UCL),
             '0': [self.L1s, self.U1s],
            '-1': (self.LCL, self.L1s),
            '-2': (self.min_-4*self.mean,self.LCL)
        }
        if self.sides == 'one_lower':
            del self.zones['+2']
            del self.zones['+1']
            self.zones['0'][1] = self.max_+4*self.mean
            
        elif self.sides == 'one_upper':
            del self.zones['-2']
            del self.zones['-1']
            self.zones['0'][0] = self.min_-4*self.mean
        
        view = (self.max_-self.min_)/2
        yrange = [self.min_-view,view+self.max_]
        yrange[0] = 0 if yrange[0] < 0 else yrange[0]
        
        if self.sides == 'one_upper':
            yrange[0] = self.min_
        elif self.sides == 'one_lower':
            yrange[1] = self.max_
        
        self.fig.update_yaxes(range=yrange)
        
        self.LSL = spec_limits.get('LSL') if spec_limits else None
        self.USL = spec_limits.get('USL') if spec_limits else None
        
        if spec_limits:
            self.draw_lines(annotated_hline_y=spec_limits,
                           show_value=True, line_style='spec')
        
        try:
            detector = AnomalyDetector(self.y)
            self.detector = detector
            self.violations = detector.violations(all_rules=True)
        except Exception as e:
            self.violations = 'Issue encountered: '+str(e)
    
    def draw_scatter(self,
                     scatter_style='default',
                     plot_layout='default',
                     hovertemplate='default'):
        '''Add scatter plot trace onto the figure. Uses data specified in the constructor as "y." Hoverlabels are assigned and created by referencing the settings defined in 'config.py.'
        
        custom options: scatter_opts, plot_layout, hovertemplate
        '''
        scatter_style = SCATTER_STYLE[scatter_style]
        plot_layout = PLOT_LAYOUT[plot_layout]
        
        n = 5 if len(self.df.columns) > 5 else len(self.df.columns)
        customdata = np.stack(
                        ([self.df[col] for col in list(self.df.columns)[:n]]),
                        axis=-1)
        
        if hovertemplate == 'default':
            hovertemplate = '<br>'.join([
                f"Index: %{{x}}",
                f"{self.y_label}: %{{y}}"] + 
                [ # slightly hidden list comprehension
                    f"{col}: %{{customdata[{i}]}}" 
                    for i, col in enumerate(
                        list(self.df.columns)[:n])
                ]
            )
        else:
            cols = CUSTOMDATA[hovertemplate]
            hovertemplate = HOVERTEMPLATE[hovertemplate]
            customdata = np.stack(([self.df[col] for col in cols]), axis=-1)

        # copy template for violations drawing
        self.customdata = customdata
        self.hovertemplate = hovertemplate
                
        self.fig.add_trace(go.Scatter(
            x=self.x, y=self.y, **scatter_style,
            customdata=customdata, hovertemplate=hovertemplate,
        ))
        
        self.fig.update_layout(**plot_layout)
                  
    def draw_spc_zones(self, color='classic', shape_layout='default'):
        '''Draw shaded regions corresponding to standard deviations around the mean
        '''
        shape_layout = SHAPE_LAYOUT[shape_layout]
        palette = COLORS[color]
            
        for zone, limits in self.zones.items():
            fillcolor = palette['zone'+zone[-1]]
            y0, y1 = limits
            self.fig.add_hrect(
                fillcolor=fillcolor,
                y0=y0,y1=y1,
                **shape_layout
            )
    
    def draw_lines(self, hline_y:list = None, annotated_hline_y:dict = None,
                  vline_x:list = None, annotated_vline_x:dict = None,
                  show_value:bool=True, color:str=False, line_style:dict='default'):        
        """Annotate the figure with lines. Specifying no arguments will draw the standard lines associated with SPC charts.
        
        - *hline_y*: list of y-values you wish to draw horizontal lines over *[can specify stats labels]
        - *annotated_hline_y*: dictionary of label: y-value for horizontal lines *[can specify stats labels, y_value will be ignored]
        - *vline_x*: list of x-values you wish to draw vertical lines over
        - *annotated_vline_x*: dictionary of label: x-value for vertical lines
        
        - *show_value*: for annotated lines, add "(value)" to the end of the label; rounded to 2 decimal places
        - *color*: takes color palette names as argument. Only to be used when no x- or y-value args are passed. Colors the default lines according to the color scheme referenced in the config. `line_style` still applies to "Mean"
        - *line_style*: style arguments for line style (plotly line arguments or kw bound to config's ANNOTATED_LINE_STYLE) 
        
        *stats labels for hline args: Mean, lower_1s, upper_1s, LCL, UCL
        """
        
        # Exception Handling
        if color:
            zones = {'-1S':'zone0','+1S':'zone0','LCL':'zone2','UCL':'zone2','Mean':'Mean'}
            if color not in COLORS.keys():
                raise Exception(f'`color` must correspond to a specified palette: {COLORS.keys()}')
        
        line_style = deepcopy(ANNOTATED_LINE_STYLE[line_style])
        
        hlines = {}
        vlines = {}
                    
        stats = {
            'Mean': self.mean,
            '-1S': self.L1s,
            '+1S': self.U1s,
            'UCL': self.UCL,
            'LCL': self.LCL
        }
        if self.sides == 'one_upper':
            del stats['-1S']
            del stats['LCL']
        elif self.sides == 'one_lower':
            del stats['+1S']
            del stats['UCL']
    
        # Default case when no args passed
        if not any((hline_y, annotated_hline_y, vline_x, annotated_vline_x)):
            vlines = None
            hlines = {v:k for k,v in stats.items()}
            
        # Merging annotated and unannotated horizontal lines into one dict
        if hline_y:
            for y_value in hline_y:
                if y_value in stats:
                    y_value = stats[y_value]
                hlines[y_value] = ''
                
        if annotated_hline_y:
            for label, y_value in annotated_hline_y.items():
                if label in stats:
                    y_value = stats[label]
                hlines[y_value] = label                
        
        # Draw horizontal lines
        if hlines:
            for y_value,label in hlines.items():
                if color:
                    line_style['line_color'] = COLORS[color][zones[label]]
                    line_style['line_dash'] = 'solid'
                if show_value and label:
                    label = f'{label} ({round(y_value,2)})'
                self.fig.add_hline(y=y_value, annotation_text=label,**line_style)
        
        # Merging annotated and unannotated vertical lines into one dict
        if vline_x:
            for x_value in vline_x:
                vlines[x_value] = ''
                
        if annotated_vline_x:
            for label, x_value in annotated_vline_x.items():
                vlines[x_value] = label
            
        # Draw vertical lines    
        if vlines: 
            for x_value,label in vlines.items():
                if show_value and label:
                    label = f'{label} ({round(x_value,2)})'
                self.fig.add_vline(x=x_value, annotation_text=label,**line_style)
                
    def draw_violations(self, color='red', symbol='x-thin', size=10, width=3):
        
        if type(self.violations) != str:

            if 'customdata' in dir(self):
                cd = self.customdata[self.violations.index]
                arr_v = np.array([self.violations])
                a,b = arr_v.shape
                arr_v.resize(b,a)
                customdata = np.concatenate((arr_v,cd),axis=1)

                prefix = 'Violated Rules: %{customdata[0]}<br>'
                hovertemplate = prefix+self.hovertemplate
            else: 
                customdata = np.stack((self.violations),axis=-1)
                hovertemplate = 'Violated Rules: %{customdata[0]}'

            self.fig.add_trace(
                go.Scatter(
                    name='Control Violation',
                    x = (x := self.violations.index),
                    y = self.y.loc[x],
                    mode='markers',
                    marker_symbol=symbol,
                    marker_line_width=width,
                    marker_line_color=color,
                    marker_size=size,
                    customdata=customdata,
                    hovertemplate=hovertemplate
                )
            )
    
    
    def capability(self):
        
        if any((self.LSL,self.USL)):
            cp = {}
            cp['mean'] = self.mean
            cp['LCL'] = self.LCL
            cp['UCL'] = self.UCL
            cp['Process Width'] = self.UCL-self.LCL
            cp['LSL'] = self.LSL
            cp['USL'] = self.USL

            # two sided specs
            if all((self.LSL,self.USL)):
                cp['Spec Width'] = self.USL-self.LSL
                cp['Cp Lower'] = (self.mean-self.LSL)/(self.mean-self.LCL)
                cp['Cp Upper'] = (self.USL-self.mean)/(self.UCL-self.mean)

            # one sided, lower spec
            elif self.LSL:
                cp['Spec Width'] = self.mean-self.LSL

            #one sided, upper spec
            elif self.USL:
                cp['Spec Width'] = self.USL-self.mean

            cp['Cp'] = cp['Spec Width']/cp['Process Width']

            return cp

    
class AnomalyDetector:      
    def __init__(self, series):
        self.data = pd.DataFrame(series.rename('amount'))
        self.mean = series.mean()
        self.sigma = series.std()
    
    # Rule 1: One point is more than 3 standard deviations from the mean (outlier)
    def rule1(self):

        def isBetween(value, lower, upper):
            isBetween = value < upper and value > lower
            return 0 if isBetween else 1

        upperLimit = self.mean + 3 * self.sigma
        lowerLimit = self.mean - 3 * self.sigma

        self.data['Rule1'] = self.data.apply(lambda row: isBetween(row['amount'], lowerLimit, upperLimit), axis = 1)

    # Rule 2: Nine (or more) points in a row are on the same side of the mean (shift)
    def rule2(self):
        values = [0]*len(self.data)

        # +1 means upside, -1 means downside
        upsideOrDownside = 0
        count = 0
        for i in range(len(self.data)):
            amount = self.data.iloc[i]['amount']
            if amount > self.mean:
                if upsideOrDownside == 1:
                    count += 1
                else: 
                    upsideOrDownside = 1
                    count = 1
            elif amount < self.mean: 
                if upsideOrDownside == -1:
                    count += 1
                else: 
                    upsideOrDownside = -1
                    count = 1

            if count >= 9:
                values[i] = 2

        self.data['Rule2'] = values              

    # Rule 3: Six (or more) points in a row are continually increasing (or decreasing) (trend)
    def rule3(self):
        values = [0]*len(self.data)

        previousAmount = self.data.iloc[0]['amount']
        # +1 means increasing, -1 means decreasing
        increasingOrDecreasing = 0
        count = 0
        for i in range(1, len(self.data)):
            amount = self.data.iloc[i]['amount']
            if amount > previousAmount:
                if increasingOrDecreasing == 1:
                    count += 1
                else:
                    increasingOrDecreasing = 1
                    count = 1
            elif amount < previousAmount:
                if increasingOrDecreasing == -1:
                    count += 1
                else:
                    increasingOrDecreasing = -1
                    count = 1

            if count >= 6:
                values[i] = 3

            previousAmount = amount

        self.data['Rule3'] = values 

    # Rule 4: Fourteen (or more) points in a row alternate in direction, increasing then decreasing (bimodal, 2 or more factors in data set)
    def rule4(self):
        values = [0]*len(self.data)

        previousAmount = self.data.iloc[0]['amount']
        # +1 means increasing, -1 means decreasing
        bimodal = 0
        count = 1
        for i in range(1, len(self.data)):
            amount = self.data.iloc[i]['amount']
            
            if amount > previousAmount:
                bimodal += 1
                if abs(bimodal) != 1:
                    count = 0
                    bimodal = 0
                else:
                    count += 1
            elif amount < previousAmount:
                bimodal -= 1
                if abs(bimodal) != 1:
                    count = 0
                    bimodal = 0
                else:
                    count += 1

            previousAmount = amount

            if count >= 14:
                values[i] = 4

        self.data['Rule4'] = values 

    # Rule 5: Two (or three) out of three points in a row are more than 2 standard deviations from the mean in the same direction (shift)
    def rule5(self):
        if len(self.data) < 3: return

        values = [0]*len(self.data)
        upperLimit = self.mean - 2 * self.sigma
        lowerLimit = self.mean + 2 * self.sigma        

        for i in range(len(self.data) - 3):
            first = self.data.iloc[i]['amount']
            second = self.data.iloc[i+1]['amount']
            third = self.data.iloc[i+2]['amount']
            
            setValue = False
            validCount = 0
            if first > self.mean and second > self.mean and third > self.mean:
                validCount += 1 if first > lowerLimit else 0
                validCount += 1 if second > lowerLimit else 0
                validCount += 1 if third > lowerLimit else 0
                setValue = validCount >= 2
            elif first < self.mean and second < self.mean and third < self.mean:
                validCount += 1 if first < upperLimit else 0
                validCount += 1 if second < upperLimit else 0
                validCount += 1 if third < upperLimit else 0
                setValue = validCount >= 2

            if setValue:
                values[i+2] = 5

        self.data['Rule5'] = values

    # Rule 6: Four (or five) out of five points in a row are more than 1 standard deviation from the mean in the same direction (shift or trend)
    def rule6(self):
        if len(self.data) < 5: return

        values = [0]*len(self.data)
        upperLimit = self.mean - self.sigma
        lowerLimit = self.mean + self.sigma   

        for i in range(len(self.data) - 5):
            pVals = list(map(lambda x: self.data.iloc[x]['amount'], range(i, i+5)))

            setValue = False
            if len(list(filter(lambda x: x > self.mean, pVals))) == 5:
                setValue = len(list(filter(lambda x: x > lowerLimit, pVals))) >= 4
            elif len(list(filter(lambda x: x < self.mean, pVals))) == 5:
                setValue = len(list(filter(lambda x: x < upperLimit, pVals))) >= 4

            if setValue:
                values[i+4] = 6

        self.data['Rule6'] = values

    # Rule 7: Fifteen points in a row are all within 1 standard deviation of the mean on either side of the mean (reduced variation or measurement issue)
    def rule7(self):
        if len(self.data) < 15: return
        values = [0]*len(self.data)
        upperLimit = self.mean + self.sigma
        lowerLimit = self.mean - self.sigma 
        
        for i in range(len(self.data) - 15):
            setValue = True
            for y in range(15):
                item = self.data.iloc[i + y]['amount']
                if item >= upperLimit or item <= lowerLimit: 
                    setValue = False
                    break
            
            if setValue:
                values[i+14] = 7

        self.data['Rule7'] = values

    # Rule 8: Eight points in a row exist with none within 1 standard deviation of the mean and the points are in both directions from the mean (bimodal, 2 or more factors in data set)
    def rule8(self):
        if len(self.data) < 8: return
        values = [0]*len(self.data)

        for i in range(len(self.data) - 8):
            setValue = True
            for y in range(8):
                item = self.data.iloc[i + y]['amount']
                if abs(self.mean - item) < self.sigma:
                    setValue = False
                    break

            if setValue:
                values[i+8] = 8

        self.data['Rule8'] = values
    
    def all_rules(self, except_=None):
        
        rules = list(range(1,9))
        if except_:
            for rule in except_:
                rules.remove(rule)
        
        for i in rules:
            eval(f'self.rule{i}()')
    
    def violations(self, all_rules=False):
        if all_rules:
            self.all_rules()
        columns = ['Rule1','Rule2','Rule3','Rule4','Rule5','Rule6','Rule7','Rule8']
        df = self.data[columns]
        df = df.loc[df.sum(axis=1)>0]
        df['violations'] = [list(filter(lambda x: bool(x), i)) for i in df.values]
        return df.violations