from datetime import date
import math
import re
import requests
from UrlBuilder import UrlBuilder
import json
import os
from progress.bar import Bar

WI_THIRST_ID = "129803"
API_URL = f"https://my.thirstproject.org/frs-api/fundraising-teams/{WI_THIRST_ID}/feed-items?"

class Scraper:
    def __init__(self, date_start: str, message: str, cache_file: str):
        """
        This function takes a date and a cache file as input and initializes the date and cache file for the
        class
        
        Args:
          date_start (str): The date you want to start scraping from.
          cache_file (str): This is the file that will be used to store the data.
        """
        self.date    = date_start
        self.message = message
        self.cache   = cache_file

    def get_total(self) -> dict:
        """
        It gets the latest donations from the API, adds them to the cache, and then sums up the donations
        from the date specified by the user
        
        Returns:
          A dictionary with the total money collected from donations and the number of donations.
        """

        donations = self.get_donos()
    
        # If dono is from {date} or later add to the total
        date_cmpts = [int(d) for d in self.date.split("-")]

        dono_totals = self.sum_donos(donations, *date_cmpts)

        dono_totals["total"] = float("{0:.2f}".format(dono_totals["total"]))
        self.rank_members(donations)
        return dono_totals


    def get_donos(self):
      
        per_page = 100  # max results per page.

        # This is checking if the cache file exists, if it doesn't it creates it. Then it opens the file in
        # read and write mode.
        if not os.path.exists(self.cache):
            open(self.cache, "w")

        f = open(self.cache, "r+")

        # Attempts to load the json file into the donations variable. If it
        # fails (invalid json), it sets the donations variable to an empty list.
        try:
            donations = json.load(f)
        except:
            donations = []

        f.close()
            # Checks if the donations list is empty. If it is, it sets the latest_id to -1. If
        # it isn't, it sets the latest_id to the id of the first donation in the list.
        latest_id = donations[0]["id"] if len(donations) > 0 else -1

        # Creating a url with the parameters that are needed to get the data from the API.
        url = UrlBuilder(API_URL)
        url.add_param("with", "linkable") 
        url.add_param("per_page", per_page)
        url.add_param("sort", "linkable_effective_at:desc") 
        url.add_param("campaignId", "137927") 
        url.add_param("page", "1")

        # Get the total number of pages that the API returns.
        request_url = url.get_url()
        response = self.req_json(request_url)
        max_page = math.ceil(response["total"] / per_page)
        
        # Adding the new donations to the old donations.
        new_donos = []
        new_donos += self.collect_donos(url, max_page, latest_id)
        donations = new_donos + donations

        # Writing the donations to the cache file.
        with open(self.cache, "w") as f:
            f.write(json.dumps(donations))

    
        if self.message is not None:
          donations = self.filter_message(donations, self.message)
        return donations


    def req_json(self, url: str) -> dict:
        """
        It takes a url as a string and returns a dictionary of the json response
        
        Args:
          url (str): The URL of the API endpoint you want to call.
        
        Returns:
          The json response as a dictionary
        """
        res = requests.get(url)
        return res.json()


    def add_to_donos(self, response: dict, donos: list, latest_id: int) -> bool:
        """
        It takes a response from the API, a list of donos, and the latest id of the dono. It then iterates
        through the response and adds the donos to the list until it reaches the latest id
        
        Args:
          response (dict): The response from the API call
          donos (list): list of dicts, each dict is a dono
          latest_id (int): The latest id of the dono you have.
        
        Returns:
          A list of dictionaries.
        """
        for data in response["data"]:
            if data["id"] == latest_id:
                return True
            else:
                donos.append(data)
        return False

    def is_current(self, year: int, month: int, day: int, date) -> bool:
        """
        It takes a date in the format of YYYY-MM-DD and returns True if the date is equal to or greater
        than the supplied donation date
        
        Args:
          year (int): int
          month (int): int
          day (int): int
          date: the date of the donation
        
        Returns:
          True if the donation is current, False if not
        """
        date_parts = date.split("-")
        date_year = int(date_parts[0])
        date_month = int(date_parts[1])
        date_day = int(date_parts[2][:2])


        #TODO: please make readable 
        return (date_year > year) or \
                ((date_year == year) and ((date_month > month) or \
                (date_month == month and date_day >= day)))

    def sum_donos(self, donations: list, start_year: int, start_month: int, start_date: int) -> dict:
        """
        It takes a list of donations, a start year, a start month, and a start date, and returns a
        dictionary with the total amount of money from the donations and the number of donations submitted
        
        Args:
          donations (list): list of donations
          start_year (int): first valid year
          start_month (int): first valid month
          start_date (int): first valid date
        
        Returns:
          A dictionary with the total amount of donations and the number of donations.
        """
        dono_date = [start_year, start_month, start_date]
        dono_totals = {
            "total": 0,
            "donation_count": 0
        }
        for dono in donations:
            try:
                linkable = dono["linkable"]
                if linkable is not None and self.is_current(*dono_date, linkable["purchased_at"]):
                    dono_totals["total"] += linkable["donation_net_amount"]
                    dono_totals["donation_count"] += 1
            except Exception as e:
              pass  # TODO handle any errors...

        return dono_totals


    def collect_donos(self, url: UrlBuilder, max_page: int, latest_id: int) -> list:
        """
        It takes a URL, a maximum page number, and a latest ID, and returns a list of new donos
        
        Args:
          url (UrlBuilder): UrlBuilder - this is the url that we're going to be using to get the data 
          from the API.
          
          max_page (int): The maximum number of pages to check.
          latest_id (int): The latest donation ID that was already processed.
        
        Returns:
          A list of new donos that aren't cached
        """
        new_donos = []
        for p in range(1, max_page + 1):
            url.edit_param("page", p)
            response = self.req_json(url.get_url())
            done = self.add_to_donos(response, new_donos, latest_id)
            if done:
                break
        return new_donos


    def filter_message(self, donations: list, message: str) -> list:
      """
      It takes a list of dictionaries and a string, and returns a list of dictionaries where the string is
      in the comment
      
      Args:
        donations (list): list of dictionaries
        message (str): The message to filter by.
      
      Returns:
        A list of dictionaries.
      """
      return [x for x in donations if message in str(x.get("comment")).lower()]

    #TODO: refactor. late night code :/
    def rank_members(self, donations: list) -> dict:
      member_count = { }
      date = [int(d) for d in self.date.split("-")]
      for dono in donations:
        if dono.get("linkable") is not None:
          if(self.is_current(*date, dono["linkable"]["purchased_at"])):
            name = dono["feedable_value"]
            amount = dono["linkable"]["donation_net_amount"]
            if member_count.get(name) is None:
              member_count[name] = amount
            else:
              member_count[name] += amount 
      return member_count

