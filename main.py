from ClassyScraper import *
from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route('/total')
def totals():
    total = open("total.json", "r")
    return json.load(total)
  
@app.route("/")
def home():
  return render_template("index.html")

app.run("0.0.0.0", 3000)
