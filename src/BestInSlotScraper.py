from collections import defaultdict
import requests
from bs4 import BeautifulSoup


class BestInSlotScraper:

    def __init__(self, equipment_string=None, slots_of_interest=None):
        if equipment_string is None:
            self.equipment_string = "Recommended equipment"
        else:
            self.equipment_string = equipment_string

        if slots_of_interest is None:
            self.slots_of_interest = [
                "Head",
                "Neck",
                "Back",
                "Body",
                "Legs",
                "Weapon",
                "Shield",
                "Ammo/Spell",
                "Gloves",
                "Boots",
                "Ring",
                "Special attack"
            ]
        else:
            self.slots_of_interest = slots_of_interest

    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        current_slot = ""
        best_in_slots = defaultdict(dict)
        for table in soup.find_all('table'):
            caption = table.find('caption')
            if table.get('class') == ['wikitable'] or (caption is not None and self.equipment_string in caption.string):
                for tr in table.find_all('tr'):
                    for rank, td in enumerate(tr.find_all('td')):
                        img = td.find('img')
                        if img is not None:
                            alt = img.get("alt")
                            if alt is not None and alt == "Special attack":
                                current_slot = "Special attack"
                        for a in td.find_all('a'):
                            title = a.get('title', '')
                            if title in self.slots_of_interest:
                                current_slot = title
                                continue
                            if current_slot != "" and title != "":
                                if rank in best_in_slots and current_slot in best_in_slots[rank]:
                                    if title not in best_in_slots[rank][current_slot]:
                                        best_in_slots[rank][current_slot].append(title)
                                else:
                                    best_in_slots[rank][current_slot] = [title]
        return dict(best_in_slots)
