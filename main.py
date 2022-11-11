from flask import Flask, render_template, request, jsonify
from ClassyScraper import Scraper

app = Flask(__name__)

@app.route('/total')
def totals():
    """
    It takes a date from the URL, creates a scraper object, and then returns the total amount of money
    raised from that date
    
    Returns:
      A JSON object with the total number of donations and the total amount of money donated.
    """
    args = request.args
    date = args.get("start")
    message = args.get("message")
    scraper = Scraper(date, message, "./data/dono_cache.json")
    total = scraper.get_total()
    return jsonify(total)

@app.route('/rank')
def rank():
    """
    It takes a date from the URL, creates a scraper object, and then returns the total amount of money
    raised from that date
    
    Returns:
      A JSON object with the total number of donations and the total amount of money donated.
    """
    args = request.args
    date = args.get("start")
    scraper = Scraper(date, None, "./data/dono_cache.json")
    members = scraper.rank_members(scraper.get_donos())
    return jsonify(members)


@app.route("/")
def home():
    """
    The function home() returns the rendered template index.html
    
    Returns:
      The index.html file is being returned.
    """
    return render_template("new.html")

app.run("0.0.0.0", 3000)
