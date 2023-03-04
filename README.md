# SPC-Plot
Class to build statistical process control charts using `plotly graph_objs`.

***

The current implementation of this project revolves around specifying custom styles in the config file. 
While I'd like to turn this into a package of its own, the first implementation of this class was as a module
in a `streamlit` dashboard, hence the chosen file structure.

Additionally, the `AnomalyDetector` was pasted from [this project](https://github.com/omerfarukozturk/AnomalyDetection) 
with some minor logic changes.

***

### How to use

```
import pandas as pd
import spc

# dummy data
data = (
    (4.13, '2022-01-29', 'NBELINSKI','None'),
    (4.11, '2022-01-30', 'DDEVITO', 'None'),
    (4.07, '2022-01-30', 'PSMITH', 'None'),
    (4.12, '2022-01-30', 'ERICHTOFEN', 'None'),
    (3.99, '2022-01-31', 'DDEVITO', 'Humidity out of tolerance'),
    (4.11, '2022-01-31', 'PSMITH', 'None'),
    (4.11, '2022-01-31', 'DDEVITO', 'None'),
    (4.12, '2022-02-01', 'DDEVITO', 'None'),
    (4.09, '2022-02-02', 'DDEVITO', 'None'),
    (4.13, '2022-02-02', 'PSMITH', 'None'),
    (4.06, '2022-02-02', 'ERICHTOFEN', 'Extra five minutes in oven'),
    (4.11, '2022-02-02', 'ERICHTOFEN', 'None'),
    (4.11, '2022-02-02', 'PSMITH', 'None'),
    (4.14, '2022-02-02', 'PSMITH', 'None'),
    (4.12, '2022-02-03', 'NBELINSKI', 'None'),
    (4.09, '2022-02-03', 'TMASAKI', 'None')
)
cols = ('Width (mm)', 'Date of Manufacture', 'Operator', 'Comments')
df = pd.DataFrame(data, columns=cols)


# create Plot object, calculates statistics
# and violations on construction
chart = Plot(df, y='Width (mm)', fig_layout='light',
           spec_limits={'USL':4.15,'LSL':4.05})

chart.LCL, chart.mean, chart.UCL
>> (3.99137185359222, 4.100625000000001, 4.209878146407782)
```

Generating plots:

```
chart.draw_scatter(plot_layout='light')
chart.draw_spc_zones()
chart.draw_lines(show_value=True, line_style='light')
chart.draw_violations()

chart.fig
>>
```
![plot](readme_refs/basic_demo.png)

***

### Known Bugs

- Default hover labels duplicate the specified "y"
- Default hover label for control violations has values offset from their labels
