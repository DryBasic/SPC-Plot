# SPC-Plot
Class to build statistical process control charts using `plotly graph_objs`.

***

The current implementation of this project revolves around specifying custom styles in the config file. 
While I'd like to turn this into a package of its own, the first implementation of this class was as a module
in a `streamlit` dashboard, hence the chosen file structure.

Additionally, the `AnomalyDetector` was pasted from [this project](https://github.com/omerfarukozturk/AnomalyDetection) 
with some minor logic changes.
