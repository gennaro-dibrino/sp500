from flask import Flask, render_template, request
import pandas as pd
import pandas_datareader.data as web
from pandas.tseries.offsets import BDay

import datetime as dt
import time
import statsmodels.tsa.api as smt

#import os
#import dill
#from bkcharts import Histogram #bokeh.charts
from bokeh.embed import components
#the imports below were added for the line plot
import numpy as np
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool, CrosshairTool, BoxAnnotation, Range1d

app = Flask(__name__)

#Business day difference function
def bday_diff(integer=1): #e.g. tomorrow = bday_diff()
    if integer == 0:
        return dt.date.today().strftime("%Y-%m-%d")
    else:
        return (dt.date.today() + BDay(integer)).strftime("%Y-%m-%d")
        
def data_loader(ticker='^GSPC', time_frame=1000): #returns a series
	start = bday_diff(-1000)
	end = bday_diff(0)
	return web.DataReader(ticker, 'yahoo', start=start, end=end).asfreq('B')
	
def fill_bf(dataf, column_list): #fills NaNs
    for col in column_list:
        dataf.loc[:,col] = dataf.loc[:,col].fillna(method='ffill')
        dataf.loc[:,col] = dataf.loc[:,col].fillna(method='bfill')
    return dataf
    
def fit_to_frame(series, order=(1,1,1), pred_time=250): #order was (5,2,0))
	arima = smt.SARIMAX(series, trend='c', order=order, enforce_invertibility=False, enforce_stationarity=False)
	arima_fit = arima.fit()
	ARIMA_pred = arima_fit.get_prediction(start=bday_diff(-1), dynamic=bday_diff(-1), end=bday_diff(pred_time)).predicted_mean
	ARIMA_CI = arima_fit.get_prediction(start=bday_diff(-1), dynamic=bday_diff(-1), end=bday_diff(pred_time)).conf_int()
	ARIMA_pred_df = pd.DataFrame(data={'Model':ARIMA_pred, 'Pred Lower Bound':ARIMA_CI.iloc[:, 0], 'Pred Upper Bound':ARIMA_CI.iloc[:, 1]}, index=ARIMA_CI.index)
	actual_end = series.index[-1]
	actual_end_val = series[-1]
	ARIMA_pred_df_plot = ARIMA_pred_df[ARIMA_pred_df.index > actual_end]
	pred_start = ARIMA_pred_df_plot.index[0]
	pred_start_val = ARIMA_pred_df_plot.loc[:,'Model'][0]
	data = pd.concat([series, ARIMA_pred_df_plot])
	data.columns = ['Actual', 'Model', 'Pred Lower Bound', 'Pred Upper Bound']
	data['date'] = data.index.values
	return data, ((actual_end, actual_end_val), (pred_start, pred_start_val))

# Load the Data Set
#cur_dir = os.path.dirname(__file__)
#data = dill.load(open('dill_objects/model/sp500_train.dill', 'rb')) #rb for win
#feature_names = ['adj_close', 'ARMA'] #data.columns.values.tolist()
#feature_names = data.columns.values.tolist()
#col_dict = {'adj_close':'#A6CEE3', 'ARMA':'#7FC97F'}

# Create the main plot -- lineplot
def create_figure(data, current_feature='Actual', tpl=None):
    col_dict = {'Model':'cyan', 'Actual':'green'}
    TOOLS = ['crosshair', 'pan','wheel_zoom','box_zoom','previewsave','reset']
    if current_feature == 'Model':
        source = ColumnDataSource(data)
        p = figure(x_axis_type='datetime', title='SP500 Index and Prediction', plot_width=1000, plot_height=400, \
            tools=TOOLS, \
            active_drag='box_zoom', active_scroll='wheel_zoom', active_inspect='crosshair', \
            responsive=True)
        hover = p.select(HoverTool)
        hover.tooltips = [
            ("date", "@date{%Y-%m-%d}"),
            ("model", "@Model{0.00}"),
            ('actual', '@Actual{0.00}')
            ]
        hover.mode = 'vline'
        hover.formatters = {"date" : 'datetime', # use 'datetime' formatter for 'date' field
            'actual' : 'printf', # use 'printf' formatter for 'Actual' field
            'model' : 'printf' # use 'printf' formatter for 'Model' field
            }
        p.x_range = Range1d(data.index.min(), data.index.max())
        box = BoxAnnotation(left=tpl[0][0], fill_color='gray', fill_alpha=0.2)
        p.add_layout(box)
        box1 = BoxAnnotation(left=tpl[0][0], right=tpl[1][0], fill_color='gray', fill_alpha=0.1)
        p.add_layout(box1)
        p.grid.grid_line_alpha=0.7
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Point Value'
        p.line('date', 'Model', line_width=4, color=col_dict[current_feature], legend=current_feature.lower(), \
            source=source)
        p.line('date', 'Pred Lower Bound', line_width=1, color='purple', source=source)
        p.line('date', 'Pred Upper Bound', line_width=1, color='purple', source=source)
        p.line('date', 'Actual', line_width=6, color=col_dict['Actual'], legend='actual', source=source)
        p.legend.location = 'bottom_right'
    else:
        source = ColumnDataSource(data)
        p = figure(x_axis_type='datetime', title='SP500 Index', plot_width=1000, plot_height=400, \
    	    tools=TOOLS, \
    	    active_drag='box_zoom', active_scroll='wheel_zoom', active_inspect='crosshair', \
    	    responsive=True)
        hover = p.select(HoverTool)
        hover.tooltips= [
            ("date", "@date{%Y-%m-%d}"),
            ("value", "@Actual{0.00}")
            ]
        hover.mode = 'vline'
        hover.formatters={
    	    "date" : 'datetime', # use 'datetime' formatter for 'date' field
    	    'value' : 'printf'   # use 'printf' formatter for 'adj close' field
    	    }
        p.x_range = Range1d(data.index.min(), tpl[0][0])
        p.grid.grid_line_alpha=0.7
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Point Value'
        p.line('date', 'Actual', line_width=6, color=col_dict[current_feature], legend=current_feature.lower(), \
    	    source=source)
        p.legend.location = 'bottom_right'
    return p


# Index page
@app.route('/')
def index():
	feature_names = ['Actual', 'Model']
	yahoo_data = data_loader()
	series_data = fill_bf(yahoo_data, yahoo_data.columns)
	data, tpl = fit_to_frame(series_data.loc[:, 'Adj Close'])
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "Actual"
	
	# Create the plot
	plot = create_figure(data, current_feature_name, tpl=tpl)
	
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("index.html", script=script, div=div, \
		feature_names=feature_names,  current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=33507, debug=False) #5000