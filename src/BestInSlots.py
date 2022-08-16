from BestInSlotScraper import BestInSlotScraper
import ScrapingUtilities
import Utilities

from colorlog import ColoredFormatter
from fuzzywuzzy import process
import concurrent.futures
import sys
import yaml
import logging


class BestInSlots:

    def __init__(self, bosses_of_interest=[], levenshtein_ratio_threshold=60, logger=None):

        self.best_in_slots_all_bosses = {}
        self.best_in_slot_items = {}
        self.levenshtein_ratio_threshold = levenshtein_ratio_threshold

        if logger is None:
            self.logger = logging.getLogger(__name__)
            handler = logging.StreamHandler()
            handler.setFormatter(ColoredFormatter("%(log_color)s%(levelname)s:%(message)s%(reset)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger

        self.compute_best_in_slots(bosses_of_interest)

    def compute_best_in_slots(self, bosses_of_interest):
        self.best_in_slots_all_bosses.clear()
        self.best_in_slot_items.clear()
        if len(bosses_of_interest) > 0:
            self.best_in_slots_all_bosses = self.__compute_bosses_best_in_slots(bosses_of_interest)
            self.best_in_slot_items = self.__compute_best_in_slot_items(self.best_in_slots_all_bosses)

    def __compute_bosses_best_in_slots(self, bosses_of_interest):
        best_in_slots_all_bosses = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            all_best_in_slots = list(
                executor.map(self.__scrape_boss_best_in_slots, bosses_of_interest)
            )

        for boss, best_in_slots in zip(bosses_of_interest, all_best_in_slots):
            if len(best_in_slots) > 0:
                best_in_slots_all_bosses[boss] = best_in_slots
            else:
                self.logger.warning("No strategy page found for %s", boss)
        return best_in_slots_all_bosses

    def __compute_best_in_slot_items(self, best_in_slots_all_bosses):
        best_in_slot_items = {}
        for boss, best_in_slots in best_in_slots_all_bosses.items():
            for slot, best_items in best_in_slots[1].items():
                for item in best_items:
                    if item not in best_in_slot_items:
                        best_in_slot_items[item] = (1, [boss])
                    else:
                        current_count, current_bosses = best_in_slot_items[item]
                        current_count += 1
                        if boss not in current_bosses:
                            current_bosses.append(boss)
                        best_in_slot_items[item] = (current_count, current_bosses)
        return best_in_slot_items

    def __scrape_boss_best_in_slots(self, boss):
        best_in_slot_scraper = BestInSlotScraper()
        self.logger.info("Scraping best in slot gear for %s", boss)
        boss_strategy_url = ScrapingUtilities.construct_boss_strategy_url(boss)
        self.logger.debug("URL: %s", boss_strategy_url)
        return best_in_slot_scraper.scrape(boss_strategy_url)

    def print_best_in_slot_items(self, items_to_print=sys.maxsize):
        best_in_slot_items_sorted = sorted(self.best_in_slot_items.items(), key=lambda x: x[1], reverse=True)
        for i, (item, (count, bosses)) in enumerate(best_in_slot_items_sorted):
            print(item, "-", count, "-", bosses)
            if i >= items_to_print:
                break

    def print_bosses_where_item_is_best_in_slot(self, item):
        if item in self.best_in_slot_items:
            counts, bosses = self.best_in_slot_items[item]
            print(item, "is best in slot at", counts, "bosses.")
            for boss in bosses:
                print("-", boss)
        else:
            self.logger.warning("Could not find %s in any best in slot setups.", item)
            valid_items = list(self.best_in_slot_items.keys())
            matches = process.extract(item, valid_items)
            sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
            match_found = False
            for matched_item, ratio in sorted_matches:
                # Assume 100 ratio is good without asking the user. (Usually diffs in capitalization.
                if ratio == 100:
                    match_found = True
                    break
                elif ratio >= self.levenshtein_ratio_threshold:
                    user_question = \
                            "Similar matched boss is " + \
                            matched_item + \
                            " with ratio " \
                            + str(ratio) + \
                            " is this the boss you meant?"
                    if Utilities.query_yes_no(user_question):
                        match_found = True
                        break
            if match_found:
                self.print_bosses_where_item_is_best_in_slot(matched_item)
            else:
                self.logger.warning("No matching item found for %s.", item)

    def print_best_in_slot_items_for_boss(self, boss, setups_to_print=sys.maxsize):
        if boss in self.best_in_slots_all_bosses:
            best_in_slots = self.best_in_slots_all_bosses[boss]
            print("Best in slot gear for ", boss, ":", sep="")
            for i in range(1, setups_to_print + 1):
                if i in best_in_slots:
                    print("Rank ", i, ":", sep="")
                    print(yaml.dump(best_in_slots[i], allow_unicode=True, default_flow_style=False, sort_keys=False))
                else:
                    break
        else:
            self.logger.warning("Could not find any setups for %s.", boss)
