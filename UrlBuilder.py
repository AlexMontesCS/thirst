import urllib

class UrlBuilder:

    #TODO validate url with some super duper cool regex 
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.url      = base_url
        self.params   = {}

    #Encode and add parameter onto url
    def add_param(self, key: str, value: str) -> None:

        if self.params.get(key) is not None: #TODO, something better than "return"
            return #If param exists, do not modify

        self.params[key] = value
        self.url = self.base_url + urllib.parse.urlencode(self.params)

    #Edit parameter and update url
    #Repetive code isn't bad, I will fight those who say that :)
    def edit_param(self, key: str, value: str) -> None:

        if self.params.get(key) is None:
            self.add_param(key, value) #If param doesnt exist, add it!

        self.params[key] = value
        self.url = self.base_url + urllib.parse.urlencode(self.params)

    #Returns built url with query params
    def get_url(self) -> str:
        return self.url
    
    #Return original API url
    def get_base(self) -> str:
        return self.base_url
