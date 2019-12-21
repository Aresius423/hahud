import os
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from datamodels import car
from glob import glob

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
menu_template = env.get_template('menu.html')
delta_template = env.get_template('delta.html')

def epoch2timestamp(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def generateDelta(dirpath: str, changes: List[car], results: List[car]):
    dfilename = dirpath + "/" + str(time.time()) + ".html"

    with open(dfilename[:-5] + ".full.html", "w+", encoding="utf-8") as full_delta_file:
        full_delta_file.write(delta_template.render(changes=results))

    with open(dfilename, 'w+', encoding='utf-8') as delta_file:
        delta_file.write(delta_template.render(changes=changes))


@dataclass
class ChangeSet:
    def __init__(self, file_path: str) -> None:
        self.delta_path = file_path
        self.full_path = f'{file_path[:-5]}.full.html'
        self.link_text = epoch2timestamp(
            float(file_path[file_path.find("data_") :].split("/")[-1][:-5])
        )


@dataclass
class MenuItem:
    query: str
    htmls: List[ChangeSet]


def get_menu_items() -> List[MenuItem]:
    dirs = glob("data_*/")
    menu_items: List[MenuItem] = []
    for directory in dirs:
        query_name = directory.split("data_")[-1][:-1]

        allhtmls = glob(directory + "*.html")[::-1]
        htmls = sorted(filter(lambda h: not h.endswith("full.html"), allhtmls))
        change_sets: List[ChangeSet] = list(map(ChangeSet, htmls))
        menu_items.append(MenuItem(query_name, change_sets))

    return menu_items


def generateMenu():
    menu_items = get_menu_items()

    with open(os.getcwd() + "/menu.html", "w+", encoding="utf-8") as menu_file:
        menu_file.write(
            menu_template.render(menu_items=menu_items)
        )
