import os
from subprocess import Popen, PIPE
import re
import PySimpleGUI as sg
from modules import yugioh_api

api = yugioh_api.YuGiOh_API()

class Window:

    def __init__(self):
        layout = [  
                    [sg.Text("Decks: ", size=(15), justification="right"),sg.InputText(key="inputPath"),sg.FilesBrowse(file_types=[("Deck File","*.ydk")])],
                    [sg.Push(), sg.Column([[sg.Button("Importar", key="BtnOk")]],element_justification='c'), sg.Push()]
                ]
        self.icon = "C:\\Users\\felipe.tavares\\Desktop\YuGiOh-API\\assets\\executable_icon.ico" 
        self.window = sg.Window('Deck List YuGiOh', layout,icon=self.icon)
        self.all_cards = api.get_all_cards_prints()

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

    def create_deck_list(self, file_list:str) -> list[str]:
        card_list:list[str] = list()
        file_list:list[str] = file_list.split(";")
        qtd_files = file_list.__len__()
        file_count = 1
        for file in file_list:
            txt_deck = open(file, encoding="utf-8").read()
            deck_name = os.path.basename(file)
            id_list:list[int] = re.findall(r'\d{1,9}',txt_deck)
            layout = [
                [sg.Push(), sg.Column([[sg.Text(str(file_count)+"/"+str(qtd_files))]],element_justification='c'), sg.Push()],
                [sg.ProgressBar(id_list.__len__(), orientation='h', size=(30, 20), key='progbar')]
            ]
            progress_window = sg.Window("Lendo o deck: "+deck_name,layout, icon=self.icon)
            event, values = progress_window.read(timeout=False)
            count = 1
            progress_window["progbar"].update_bar(count)
            for card in id_list:
                find_card = list(filter(lambda x:int(card)==x["id_print"],self.all_cards))[0]["name_card"]
                card_list.append(find_card)
                progress_window["progbar"].update_bar(count)
                count+=1
            progress_window.close()
            file_count+=1
        return card_list

    def create_txt(self, data:list[str])->None:
        txt_data = ""
        qtd = 0
        card_list:list[dict] = list()
        for card in list(dict.fromkeys(data)):
            card_qtd = list(filter(lambda x:x==card,data)).__len__()
            card_list.append({"name":card,"qtd":card_qtd})
            qtd+=card_qtd
        card_list = sorted(card_list,key=lambda x:x["name"])
        card_list = sorted(card_list,key=lambda x:x["qtd"],reverse=True)
        actually_qtd = card_list[0]["qtd"]
        for card in card_list:
            if actually_qtd != card["qtd"]:
                actually_qtd = card["qtd"]
                txt_data+="\n"
            txt_data+= card["name"]+" x"+str(card["qtd"])+"\n"
        txt_data+="\n"
        txt_data+="Quantidade de cartas: "+str(qtd)
        with open("resultado.txt",mode="w") as txt_file:
            txt_file.write(txt_data)