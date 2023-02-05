import requests

class YuGiOh_API:

    def __init__(self) -> None:
        self.url:str = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        
    def get_card(self, id:int):
        response = requests.get(self.url + "?id="+str(id))
        card = response.json()
        return card["data"][0]

yugi = YuGiOh_API()