import pdfrw
import os
from pathlib import Path

class PDFReader:
    def __init__(self) -> None:
        self.pdf_path = "C:\\Users\\felipe.tavares\\Desktop\YuGiOh-API\\assets\\KDE_DeckList-PT.pdf"
        self.pdf_model = pdfrw.PdfReader(self.pdf_path)

    def fill_form(self, data):
        annotations:list[pdfrw.objects.pdfdict.PdfDict] = list(filter(lambda x:x["/Subtype"]=="/Widget" and x["/T"],self.pdf_model.pages[0]['/Annots']))
        annotations:list[pdfrw.objects.pdfdict.PdfDict] = list(filter(lambda x:list(data.keys()).__contains__(x["/T"][1:-1]),annotations))
        for annotation in annotations:
            annotation.update(pdfrw.PdfDict(**{"V":data[annotation["/T"][1:-1]]}))
        self.pdf_model.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
        pdfrw.PdfWriter().write(data["pdf_name"]+".pdf", self.pdf_model)