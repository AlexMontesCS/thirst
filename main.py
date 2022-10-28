from ClassyScraper import *
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/total')
def totals():
    args = request.args
    date = args.get("start")    
    total = get_total(date)
    return jsonify(total)

@app.route("/")
def home():
    return render_template("index.html")


app.run("0.0.0.0", 3000)
