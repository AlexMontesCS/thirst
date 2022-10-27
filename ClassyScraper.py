import math
from os import link
import re
import requests
from UrlBuilder import UrlBuilder
import json
from tqdm import tqdm
from decimal import Decimal
from progress.bar import Bar

WI_THIRST_ID = "129803"
API_URL = f"https://my.thirstproject.org/frs-api/fundraising-teams/{WI_THIRST_ID}/feed-items?"

dono_totals = {
    "total": 0,
    "donation_count": 0
}

def get_total() -> dict:
    per_page = 100 #eek, max is 100
    donations = []

    #build da url 🧃
    url = UrlBuilder(API_URL)
    url.add_param("with", "linkable") #gimme only fields that have data i need 💢
    url.add_param("per_page", per_page) 
    url.add_param("sort", "linkable_effective_at:desc") #newest monies on top 😎 (desc, descending)
    url.add_param("campaignId", "137927") #TODO what even is this, do i need it
    url.add_param("page", "1") 

    #request page one to find how many pages we need to iterate through
    request_url = url.get_url()
    response = req_json(request_url)
    max_page = math.ceil(response["total"] / per_page)

    #setup progress bar bc look cewl
    bar = Bar('Getting Data...', max=max_page)
    donations += response["data"]
    bar.next()

    #iterate through every page, adding data to big list :o
    for p in range(2, max_page + 1):
        url.edit_param("page", p)
        response = req_json(url.get_url())
        donations +=  response["data"]
        bar.next()

    bar.finish()

    print("Filtering Donations...")
    # donations = list(filter(lambda x: x.get("linkable_type") == "donation", donations))


    #If dono is from this year add to the total
    for dono in donations:
        try:
            linkable = dono["linkable"]
            if is_current(2022, 8, linkable["purchased_at"]):
              dono_totals["total"] += linkable["donation_net_amount"]
              dono_totals["donation_count"] += 1
        except:
            pass #TODO 

    dono_totals["total"] = float("{0:.2f}".format(dono_totals["total"]))
    return dono_totals


#Get json as dict from an api
def req_json(url: str) -> dict:
    res = requests.get(url)
    return res.json()

def is_current(year: int, month: int, date):
    date_parts = date.split("-")
    date_year  = int(date_parts[0])
    date_month = int(date_parts[1])
    return year <= date_year and month <= date_month
