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
DEFAULT_DATE = "2022-08-01"

def get_total(date: str = DEFAULT_DATE) -> dict:
    per_page = 100  # max results per page.

    # If cache file does not exist, create it!
    if not os.path.exists(CACHE):
        open(CACHE, "w")

    # open cache for reading
    f = open(CACHE, "r+")

    # If not valid json get that out of here >:(
    try:
        donations = json.load(f)
    except:
        donations = []

    f.close()

    # latest id stored in cache!
    latest_id = donations[0]["id"] if len(donations) > 0 else -1

    # build da url 🧃
    url = UrlBuilder(API_URL)
    url.add_param("with", "linkable") # gimme only fields that have data i need 💢
    url.add_param("per_page", per_page)
    url.add_param("sort", "linkable_effective_at:desc") # newest monies on top 😎 (desc, descending)
    url.add_param("campaignId", "137927") # TODO what even is this, do i need it
    url.add_param("page", "1")

    # request page one to find how many pages we need to iterate through
    request_url = url.get_url()
    response = req_json(request_url)
    max_page = math.ceil(response["total"] / per_page)
    new_donos = []

    # iterate through every page, adding data to big list :o
    new_donos += collect_donos(url, max_page, latest_id)
    donations = new_donos + donations

    # cache new data :o
    with open(CACHE, "w") as f:
        f.write(json.dumps(donations))

    # If dono is from {date} or later add to the total
    date_cmpts = date.split("-")
    dono_totals = sum_donos(donations, int(date_cmpts[0]), int(date_cmpts[1]), int(date_cmpts[2]))

    dono_totals["total"] = float("{0:.2f}".format(dono_totals["total"]))

    return dono_totals


# Get json as dict from an api
def req_json(url: str) -> dict:
    res = requests.get(url)
    return res.json()


# If cached dono is found we return True to show that there is no need to continue.
def add_to_donos(response: dict, donos: list, latest_id: int) -> bool:
    for data in response["data"]:
        if data["id"] == latest_id:
            return True
        else:
            donos.append(data)
    return False

# if dono is past x date, return True!
def is_current(year: int, month: int, day: int, date) -> bool:
    date_parts = date.split("-")

    date_year = int(date_parts[0])
    date_month = int(date_parts[1])
    date_day = int(date_parts[2][:2])

    return year <= date_year and month <= date_month and day <= date_day

#add all donations together in list
def sum_donos(donations: list, start_year: int, start_month: int, start_date: int) -> dict:
    dono_totals = {
        "total": 0,
        "donation_count": 0
    }
    for dono in donations:
        try:
            linkable = dono["linkable"]
            if is_current(start_year, start_month, start_date, linkable["purchased_at"]):
                dono_totals["total"] += linkable["donation_net_amount"]
                dono_totals["donation_count"] += 1
        except:
            pass  # TODO yucky pass
    return dono_totals


def collect_donos(url: UrlBuilder, max_page: int, latest_id: int) -> list:
    new_donos = []
    for p in range(1, max_page + 1):
        url.edit_param("page", p)
        response = req_json(url.get_url())
        done = add_to_donos(response, new_donos, latest_id)
        if done:
            break
    return new_donos