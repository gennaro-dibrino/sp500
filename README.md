# Financial Index Predictor App

The aim of this project is to build a Heroku web app allowing the user to perform some exploratory analysis of 
some major financial indices, as well as to predict the future trend of such indices. The prediction is carried out
using a machine learning model for time series, which is the core of this project.
The model was selected by minimizing AIC, which appears to be a good way to prevent overfitting.
In a way, the selection mimics the `auto.arima` function available in R.

## Some details

The whole project, from the initial exploratory analysis to the web app deployment, was carried out using Python.
In particular, the data are downloaded in real time from Yahoo Finance using the `pandas_datareader` module, the
functions needed to fit the model come from Python's `statsmodels`, and all data frames and series are handled using
`pandas`. Finally, the visualization uses Python's `bokeh` and the interaction of the Python and HTML codes is managed
using Python's `flask`. 