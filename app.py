import streamlit as st
import os 
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


test_url = "https://www.royalroad.com/fiction/117255/rend"

veränderte_novels = {}
neue_novels ={}


novel_chapter = []
json_neu_data = {}

script_path = os.path.dirname(os.path.abspath(__file__))

novel_path = os.path.join(script_path, "novels.txt")
jason_path = os.path.join(script_path, "novel_status.json")
zettle_path = os.path.join(script_path, "zettel.txt")


def load_json():
    with open(jason_path, "r") as j:
         return json.load(j)

def update_json():
    with open(jason_path, "w") as j:
        json.dump(json_neu_data,j ,indent=2)



def ropen_txt(datei):
    with open(datei,"r") as d:
        return [line.strip() for line in d if line.strip()]
    
def wright_txt(datei):
        txt_inhalt = ropen_txt(datei)
        with open(datei,"w") as d:
            
            for line in txt_inhalt:
                d.write(f"{line}\n")

            for novels in veränderte_novels.keys():
                d.write(f"{get_novelname_from_url(novels)} NEUES CHAPTER. Status: {datetime.now().date()}\n")
        

def wright_novel_stauts(inhalt):
    with open(jason_path, "w") as wj:
        json.dump(inhalt, wj, indent=2)


def get_chapter_info(seite):
    
    response = requests.get(seite)
    soup = BeautifulSoup(response.text, "html.parser")

    if seite.split(".")[0] == "https://novelight":

        find = soup.find_all(class_= "title")

        for bit in find:
            if "chapter" in bit.text:
                return bit.text.strip()

    else:
        element = soup.find_all("span", class_="label")

        for span in element:
            if "Chapters" in span.text:
                return span.text


def get_novelname_from_url(url):
    return url.rstrip("/").split("/")[-1]


def check_novel_stauts(keys:list, old_data:dict, new_data: dict):
    for key in keys:
        old_chapter = old_data.get(key)
        new_chapter = new_data.get(key)

        if old_chapter == None:
            #fügt der json die neue novel hinzu 
            neue_novels[key] = new_chapter
        
        elif old_chapter != new_chapter:
            veränderte_novels[key] = new_chapter

def farb_text(text, farbe):
    return f'<span style="color:{farbe}">{text}</span>'

class Webseite:

    def __init__(self) -> None:
        self.status = "NA"

    def set_status(self, new_status: str):
        self.status = new_status


#START DER MAIN
web = Webseite()

st.title("🧙‍♂️ Willkommen zum Kapitel Checker von Finn")


if st.button("prüfen"):
    curren_json_data = load_json()
    novel_data = ropen_txt(novel_path)

    for novels in novel_data:
        novel_chapter.append(get_chapter_info(novels))


    #kombination der beiden listen Novel_chapter und novel_url als key in ein dict
    for i, key in enumerate(novel_data):
        json_neu_data[key] = novel_chapter[i]

    #prüft ob die novels ein neues chapter haben (hat sich die chapter zahl verändert)
    check_novel_stauts(novel_data, curren_json_data, json_neu_data)

    #fügt der neuen json inhalt die neuen novels hinzu 
    for key in neue_novels.keys():
        json_neu_data[key] = neue_novels[key]

    wright_txt(zettle_path)
    update_json()

    if not len(veränderte_novels) == 0:
        st.markdown(farb_text("Neues Chapter gefunden", "green"), unsafe_allow_html=True)
    
    else:
        st.markdown(farb_text("Leider kein neues Chapter", "red"), unsafe_allow_html=True)


st.markdown("---")
if not len(veränderte_novels) == 0:
    
    for vonels in veränderte_novels:
        inhalt = get_novelname_from_url(str(vonels)).replace('-',' ')
        novel_chapter.append(f"{inhalt}")
        st.write(f"__{inhalt}__")

#auflistung von den sachen die gecheckt werden
novels = ropen_txt(novel_path)
with st.expander("Aktuelle Novels"):
    for eintrag in novels:
        name = get_novelname_from_url(eintrag).replace('-',' ')
        st.markdown(f"[{name}]({eintrag})")#get_novelname_from_url(eintrag).replace('-',' '))
