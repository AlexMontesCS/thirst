import urllib

class UrlBuilder:

    #TODO validate base url with regex 
    def __init__(self, base_url: str) -> None:
        """
        The function takes a base_url as a string and sets the url and params attributes to the base_url and
        an empty dictionary, respectively
        
        Args:
          base_url (str): The base URL of the API.
        """
        self.base_url = base_url
        self.url      = base_url
        self.params   = {}

    def add_param(self, key: str, value: str) -> None:
        """
        If the key exists, do not modify the url. If not, add it.
        
        Args:
          key (str): The parameter key
          value (str): The value of the parameter.
        
        Post-Condition:
          Parameter is added to the objects params dictionary
        """

        # If the key exists, do not modify the url
        if self.params.get(key) is not None:
            return 

        # Updating the url with the new parameter.
        self.params[key] = value
        self.url = self.base_url + urllib.parse.urlencode(self.params)

    #Repetive code isn't bad, I will fight those who say that :)
    def edit_param(self, key: str, value: str) -> None:
        """
        If the key exists, change the value. If it doesn't, add it
        
        Args:
          key (str): The parameter key
          value (str): The value of the parameter.

        Post-Condition:
            The object's params dictionary is modified with the new value.
        """

        if self.params.get(key) is None:
            self.add_param(key, value) #If param doesnt exist, add it!

        self.params[key] = value
        self.url = self.base_url + urllib.parse.urlencode(self.params)

    def get_url(self) -> str:
        """
        It returns the url of the current page
        
        Returns:
          The url of the object
        """
        return self.url
    
    def get_base(self) -> str:
        """
        It returns the base url of the API
        
        Returns:
          The base_url
        """
        return self.base_url
