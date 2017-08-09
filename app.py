from flask import Flask, render_template, request
import pandas as pd
import os
import dill
#from bkcharts import Histogram #bokeh.charts
from bokeh.embed import components
#the imports below were added for the line plot
import numpy as np
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file

app = Flask(__name__)

# Load the Data Set
cur_dir = os.path.dirname(__file__)
data = dill.load(open('dill_objects/model/test_me_AB_grid_2010.dill', 'rb'))
#pd.read_csv(names=["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Species"])
feature_names = data.columns.values.tolist()

# Create the main plot -- lineplot
def create_figure(current_feature_name):
	p = figure(x_axis_type='datetime', title="Actual Value vs GS_AdaBoost", plot_width=800, plot_height=400, \
               tools='pan,wheel_zoom,box_zoom,resize,previewsave,reset')
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label = current_feature_name
	p.yaxis.axis_label = 'Date'
	p.line(data.index, data[current_feature_name], color='#A6CEE3', legend=current_feature_name)
	#show(p)
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
		current_feature_name = "actual"   #the other column is 'model'

	# Create the plot
	plot = create_figure(current_feature_name)
		
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("index.html", script=script, div=div,
		feature_names=feature_names,  current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=33507, debug=False) #5000