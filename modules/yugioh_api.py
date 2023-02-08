import requests
import json

class YuGiOh_API:

    def __init__(self) -> None:
        self.url:str = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        
    def get_card(self, id:int):
        response = requests.get(self.url + "?id="+str(id))
        card = response.json()
        return card["data"][0]

    def get_all_cards(self):
        response = requests.get(self.url)
        all_cards = response.json()
        return all_cards["data"]
    
    def get_all_cards_prints(self):
        all_cards = self.get_all_cards()
        all_cards_prints = []
        list(map(lambda x:all_cards_prints.extend(self.get_all_prints(x)),all_cards))
        return all_cards_prints

    def get_all_prints(self,card)->list[dict]:
        card_prints = list(map(lambda x:{"name_card":card["name"],"id_print":x["id"],"type":card["type"]},card["card_images"]))
        return card_prints

# with open("all_cards.json", mode="w", encoding="utf-8") as json_file:
#     json_file.write(json.dumps(YuGiOh_API().get_all_cards_prints(), indent=6))