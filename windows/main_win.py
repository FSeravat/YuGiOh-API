import os
from subprocess import Popen, PIPE
import re
import PySimpleGUI as sg
from modules import yugioh_api
from modules import pdf_editer

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
                    card_list = list(map(lambda x:x["name_card"],data))
                    self.create_txt(card_list)
                    sg.popup_notify("Lista criada com sucesso !")
                except Exception as e:
                    sg.popup(str(e))

    def close(self):
        self.window.close()

    def create_pdf_format(self, data:dict)->dict:
        pdf_data = dict()
        side = list(filter(lambda x:x["location"]=="side",data))
        extra = list(filter(lambda x:x["location"]=="extra",data))
        main = list(filter(lambda x:x["location"]=="main",data))
        count = 1
        for x in list(dict.fromkeys(list(map(lambda x:x["name_card"],side)))):
            pdf_data["Card SD "+str(count)] = x
            pdf_data["Number SD "+str(count)] = list(filter(lambda item:item["name_card"]==x, side)).__len__()
            count+=1
        pdf_data["Total Side Deck"] = side.__len__()
        count = 1
        for x in list(dict.fromkeys(list(map(lambda x:x["name_card"],extra)))):
            pdf_data["Card ED "+str(count)] = x
            pdf_data["Number ED "+str(count)] = list(filter(lambda item:item["name_card"]==x, extra)).__len__()
            count+=1
        pdf_data["Total Extra Deck"] = extra.__len__()
        count = 1
        monsters_main = list(filter(lambda x:x["type"].__contains__("Monster"),main))
        for x in list(dict.fromkeys(list(map(lambda x:x["name_card"],monsters_main)))):
            pdf_data["Card Monster "+str(count)] = x
            pdf_data["Number Monster "+str(count)] = list(filter(lambda item:item["name_card"]==x, monsters_main)).__len__()
            count+=1
        pdf_data["Total Monster Cards"] = monsters_main.__len__()
        count = 1
        spell_main = list(filter(lambda x:x["type"].__contains__("Spell"),main))
        for x in list(dict.fromkeys(list(map(lambda x:x["name_card"],spell_main)))):
            pdf_data["Card Spell "+str(count)] = x
            pdf_data["Number Spell "+str(count)] = list(filter(lambda item:item["name_card"]==x, spell_main)).__len__()
            count+=1
        pdf_data["Total Spell Cards"] = spell_main.__len__()
        count = 1
        trap_main = list(filter(lambda x:x["type"].__contains__("Trap"),main))
        for x in list(dict.fromkeys(list(map(lambda x:x["name_card"],trap_main)))):
            pdf_data["Card Trap "+str(count)] = x
            pdf_data["Number Trap "+str(count)] = list(filter(lambda item:item["name_card"]==x, trap_main)).__len__()
            count+=1
        pdf_data["Total Trap Cards"] = trap_main.__len__()
        count = 1
        return pdf_data

    def create_deck_list(self, file_list:str) -> dict:
        card_list:list[dict] = list()
        file_list:list[str] = file_list.split(";")
        qtd_files = file_list.__len__()
        file_count = 1
        for file in file_list:
            txt_deck = open(file, encoding="utf-8").read()
            deck_name = os.path.basename(file)
            id_list:list[dict] = []
            side_deck:list[str] = txt_deck.split("!side")
            extra_deck:list[str] = side_deck[0].split("#extra")
            main_deck:list[str] = extra_deck[0].split("#main")
            main_deck_list:list[int] = re.findall(r'\d{1,9}',main_deck[1])
            extra_deck_list:list[int] = re.findall(r'\d{1,9}',extra_deck[1])
            side_deck_list:list[int] = re.findall(r'\d{1,9}',side_deck[1])
            id_list = {"main":main_deck_list,"extra":extra_deck_list,"side":side_deck_list}
            layout = [
                [sg.Push(), sg.Column([[sg.Text(str(file_count)+"/"+str(qtd_files))]],element_justification='c'), sg.Push()],
                [sg.ProgressBar(id_list.__len__(), orientation='h', size=(30, 20), key='progbar')]
            ]
            progress_window = sg.Window("Lendo o deck: "+deck_name,layout, icon=self.icon)
            event, values = progress_window.read(timeout=False)
            count = 1
            progress_window["progbar"].update_bar(count)
            deck_list = list()
            for key in id_list:
                for card in id_list[key]:
                    find_card = list(filter(lambda x:int(card)==x["id_print"],self.all_cards))[0]
                    find_card["location"] = key
                    card_list.append(find_card)
                    deck_list.append(find_card)
                    progress_window["progbar"].update_bar(count)
                    count+=1
            pdf_data = self.create_pdf_format(deck_list)
            pdf_data["pdf_name"] = os.path.splitext(deck_name)[0]
            pdf_editer.PDFReader().fill_form(pdf_data)
            progress_window.close()
            file_count+=1
        card_list
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