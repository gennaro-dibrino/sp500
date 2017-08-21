from flask import Flask, render_template, request
import pandas as pd
import os
import dill
#from bkcharts import Histogram #bokeh.charts
from bokeh.embed import components
#the imports below were added for the line plot
import numpy as np
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool, CrosshairTool
import datetime

app = Flask(__name__)

# Load the Data Set
cur_dir = os.path.dirname(__file__)
data = dill.load(open('dill_objects/model/sp500_train.dill', 'rb')) #rb for win
feature_names = ['adj_close', 'ARMA'] #data.columns.values.tolist()
#feature_names = data.columns.values.tolist()
col_dict = {'adj_close':'#A6CEE3', 'ARMA':'#7FC97F'}

# Create the main plot -- lineplot
def create_figure_w_tltp(current_feature_name):
    other_feature = [i for i in feature_names if i != current_feature_name][0] #comment out in final?
    source = ColumnDataSource(data=dict(
        #x=data.index,
        #equally useless##x=[idx.strftime("%Y-%m-%d") for idx in data.index],
        y=data[current_feature_name]
        ))
    crosshair = CrosshairTool(dimensions='height')
    hover = HoverTool(tooltips=[
        #("date", "$x"), #was '$x' before -- $x yields exp notation, @x plain, $index
        ("", "@y{0.00}")
        ],
                      formatters={
                          #"date" : 'datetime', # use 'datetime' formatter for 'date' field
                          'value' : 'printf'   # use 'printf' formatter for 'adj close' field
                          # use default 'numeral' formatter for other fields
                          },
                      #display a tooltip whenever the cursor is vertically in line with a glyph
                      mode='vline')
    
    p = figure(x_axis_type='datetime', title='Actual value vs ARMA Model', plot_width=1000, plot_height=400, \
               tools=[hover, crosshair, 'pan','wheel_zoom','box_zoom','resize','previewsave','reset'], responsive=True)
    p.grid.grid_line_alpha=0.7
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Point Value'
    p.line(data.index, data[current_feature_name], color=col_dict[current_feature_name], legend=current_feature_name)
    p.line(data.index, data[other_feature], color=col_dict[other_feature], legend=other_feature) #comment out in final?
    p.legend.location = "bottom_right"
    return p

'''
# Create the main plot -- histogram
def create_figure(current_feature_name, bins):
	p = Histogram(iris_df, current_feature_name, title=current_feature_name, color='Species', 
	 	bins=bins, legend='top_right', width=600, height=400, tools='pan,wheel_zoom,box_zoom,resize,previewsave,reset')

	# Set the x axis label
	p.xaxis.axis_label = current_feature_name

	# Set the y axis label
	p.yaxis.axis_label = 'Count'
	return p
'''
# Index page
@app.route('/')
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "adj_close"   #the other column is 'model'

	# Create the plot
	plot = create_figure_w_tltp(current_feature_name)
		
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("index.html", script=script, div=div,
		feature_names=feature_names,  current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=33507, debug=False) #5000