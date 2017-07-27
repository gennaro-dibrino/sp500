from flask import Flask, render_template, request, redirect
import dill
import numpy as np
import os

#Preparing the regressor
cur_dir = os.path.dirname(__file__)
#rgr = dill.load(open(os.path.join(cur_dir, 'dill_objects/model/grid_ada_10.dill'), 'r'))
#df = dill.load(open(os.path.join(cur_dir, 'dill_objects/model/test_me_AB_grid_2010.dill'), 'r'))

app = Flask(__name__)

@app.route('/')
def main():
	print cur_dir
	return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

if __name__ == '__main__':
  app.run(port=33507)  #debug=True