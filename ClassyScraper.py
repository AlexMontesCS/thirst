import math
import re
import requests
from UrlBuilder import UrlBuilder
import json
import os
from progress.bar import Bar

WI_THIRST_ID = "129803"
API_URL = f"https://my.thirstproject.org/frs-api/fundraising-teams/{WI_THIRST_ID}/feed-items?"
CACHE = "dono_cache.json"

def get_total() -> dict:

    #start *fresh*
    dono_totals = {
        "total": 0,
        "donation_count": 0
    }
    new_donos = []
    per_page = 100 #max results per page.

    #If cache file does not exist, create it!
    if not os.path.exists(CACHE):
        open(CACHE, "w")

    #open cache for reading
    f = open(CACHE, "r+") 

    #If not valid json get that out of here >:(
    try:
        donations = json.load(f) 
    except:
        donations = []

    f.close()

    #latest id stored in cache!
    latest_id = donations[0]["id"] if len(donations) > 0 else -1

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
    done = add_to_donos(response, new_donos, latest_id)
    bar.next()

    #iterate through every page, adding data to big list :o
    for p in range(2, max_page + 1):
        if done:
            bar.goto(max_page)
            break
        url.edit_param("page", p)
        response = req_json(url.get_url())
        done = add_to_donos(response, new_donos, latest_id)
      
        bar.next()
    bar.finish()

    donations = new_donos + donations

    #save new data :o
    with open(CACHE, "w") as f:
        f.write(json.dumps(donations))


    #If dono is from this year add to the total
    #TODO adapatble by parameters
    for dono in donations:
        try:
            linkable = dono["linkable"]
            if is_current(2022, 8, linkable["purchased_at"]):
              dono_totals["total"] += linkable["donation_net_amount"]
              dono_totals["donation_count"] += 1
        except:
            pass #TODO yucky pass



    dono_totals["total"] = float("{0:.2f}".format(dono_totals["total"]))
    return dono_totals


#Get json as dict from an api
def req_json(url: str) -> dict:
    res = requests.get(url)
    return res.json()


#If cached dono is found we return True to show that there is no need to continue.
def add_to_donos(response: dict, donos: list, latest_id: int) -> bool:
    for data in response["data"]:
        if data["id"] == latest_id:
            return True
        else:
            donos.append(data)
    return False
    
#if dono is past x date, return True!
def is_current(year: int, month: int, date) -> bool:
    date_parts = date.split("-")
    date_year  = int(date_parts[0])
    date_month = int(date_parts[1])
    return year <= date_year and month <= date_month
