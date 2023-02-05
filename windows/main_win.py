import os
from subprocess import Popen, PIPE
import re
import PySimpleGUI as sg
from modules import yugioh_api

api = yugioh_api.YuGiOh_API()

class Window:

    def __init__(self):
        layout = [  
                    [sg.Text("Decks: ", size=(15), justification="right"),sg.InputText(key="inputPath"),sg.FilesBrowse(file_types=("Deck File","*.ydk"))],
                    [sg.Push(), sg.Column([[sg.Button("Importar", key="BtnOk")]],element_justification='c'), sg.Push()]
                ]
        self.window = sg.Window('Deck List YuGiOh', layout)

    def open(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                self.close()
                break
            if event == "BtnOk":
                try:
                    data = self.create_deck_list(values["inputPath"])
                    self.create_txt(data)
                    sg.popup_notify("Lista criada com sucesso !")
                except Exception as e:
                    sg.popup(str(e))

    def close(self):
        self.window.close()

    def create_deck_list(self, file_list:str) -> list[dict]:
        card_list:list[dict] = list()
        file_list:list[str] = file_list.split(";")
        for file in file_list:
            txt_deck = open(file, encoding="utf-8").read()
            deck_name = os.path.basename(file)
            id_list:list[int] = re.findall(r'\d{1,9}',txt_deck)
            layout = [[sg.ProgressBar(id_list.__len__(), orientation='h', size=(30, 20), key='progbar')]]
            progress_window = sg.Window("Lendo o deck: "+deck_name,layout)
            event, values = progress_window.read(timeout=False)
            count = 1
            for card in list(dict.fromkeys(id_list)):
                card_obj = dict()
                card_obj["id"] = card
                card_obj["name"] = api.get_card(card)["name"]
                card_obj["qtd"] = list(filter(lambda x:x==card,id_list)).__len__()
                card_list.append(card_obj)
                progress_window["progbar"].update_bar(count)
                count+=1
            progress_window.close()
        return card_list

    def create_txt(self, data:list[dict])->None:
        txt_data = ""
        qtd = 0
        three_copys = sorted(list(filter(lambda x:x["qtd"]==3,data)),key=lambda x:x["name"])
        qtd += three_copys.__len__() * 3
        two_copys = sorted(list(filter(lambda x:x["qtd"]==2,data)),key=lambda x:x["name"])
        qtd += two_copys.__len__() * 2
        one_copys = sorted(list(filter(lambda x:x["qtd"]==1,data)),key=lambda x:x["name"])
        qtd += one_copys.__len__()
        all_copys = [three_copys,two_copys,one_copys]
        for copy in all_copys:
            for card in copy:
                txt_data+=card["name"]+" x"+str(card["qtd"])+"\n"
            txt_data+="\n"
        txt_data+="Quantidade de cartas: "+str(qtd)
        with open("resultado.txt",mode="w") as txt_file:
            txt_file.write(txt_data)