from BestInSlots import BestInSlots
from BossesScraper import BossesScraper
import ScrapingUtilities
import Utilities

from colorlog import ColoredFormatter
from fuzzywuzzy import process
import argparse
import concurrent.futures
import logging


def create_arg_parser():
    parser = argparse.ArgumentParser(
        description='Scrapes the OSRS wiki for items that are best in slot at a list of bosses.')

    parser.add_argument(
        '--no-print-items',
        dest="print_items",
        action='store_false',
        default=True,
        help='do not print items that are best in slot.')
    parser.add_argument(
        '--no-print-bosses',
        dest="print_bosses",
        action='store_false',
        default=True,
        help='do not print the best in slot setup for each boss.')

    parser.add_argument(
        '--bosses-of-interest',
        nargs='+',
        default=["All"],
        help='list of bosses we wish to scrape best in slot items for.')
    parser.add_argument(
        '--items-of-interest',
        nargs='+',
        default=["All"],
        help='list of items we wish to check where they are best in slot.')

    parser.add_argument(
        '--setups-to-print',
        type=int,
        choices=range(1, 6),
        default=1,
        help='number of best in slot setups to print. 1 is only best in slot, 5 is all five setups.')

    return parser


def is_valid_boss(boss):
 return ScrapingUtilities.url_is_good(ScrapingUtilities.construct_boss_strategy_url(boss))


def scrape_bosses(bosses_url, logger):
    logger.info("Scraping wiki for list of valid bosses...")
    bosses_scraper = BossesScraper()
    bosses_of_interest = bosses_scraper.scrape(bosses_url)

    # Some bosses have strategy pages that are not the same as the bosses listed.
    # Ex: Raids have an overall page instead of separated by boss.
    # Same for barrows, jad, zuk, DKs.
    # Deranged arch has an inconsistency where the boss listed uses a capital "A" but the strategy page is lowercase.
    extra_bosses = [
        "Chambers of Xeric",
        "Theatre of Blood",
        "TzHaar Fight Cave",
        "Inferno",
        "Barrows",
        "Dagannoth Kings",
        "Deranged archaeologist"
    ]
    bosses_of_interest += extra_bosses

    # Validate the bosses. Remove any boss that does not have a valid strategy page.
    logger.info("Removing bosses with no valid strategy page...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        valid_bosses = [
            valid_boss for valid_boss in executor.map(is_valid_boss, bosses_of_interest)
        ]
    bosses_of_interest_filtered = [boss for (boss, is_valid) in zip(bosses_of_interest, valid_bosses) if is_valid]
    for removed_boss in list(set(bosses_of_interest) - set(bosses_of_interest_filtered)):
        logger.warning("No strategy page found for %s. Removing from list of bosses.", removed_boss)

    return bosses_of_interest_filtered


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(log_color)s%(levelname)s:%(message)s%(reset)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    bosses_url = "https://oldschool.runescape.wiki/w/Boss"

    levenshtein_ratio_threshold = 60

    all_bosses = scrape_bosses(bosses_url, logger)
    bosses_of_interest = []
    if args.bosses_of_interest == ["All"]:
        bosses_of_interest = all_bosses
    else:
        # Try to match the boss to a boss in all bosses. This will attempt to circumvent spelling/capitalization errors.
        for boss in args.bosses_of_interest:
            boss_match_found = False
            if is_valid_boss(boss):
                bosses_of_interest.append(boss)
                boss_match_found = True
            else:
                logger.warning("Could not find strategy page for %s", boss)
                matches = process.extract(boss, all_bosses)
                sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
                for matched_boss, ratio in sorted_matches:
                    if ratio >= levenshtein_ratio_threshold:
                        user_question =\
                            "Similar matched boss is " +\
                            matched_boss +\
                            " with ratio "\
                            + str(ratio) +\
                            " is this the boss you meant?"
                        if Utilities.query_yes_no(user_question):
                            bosses_of_interest.append(matched_boss)
                            boss_match_found = True
                            break
                if not boss_match_found:
                    bosses_of_interest.append(boss)

    best_in_slots = BestInSlots(
        bosses_of_interest,
        levenshtein_ratio_threshold=levenshtein_ratio_threshold,
        logger=logger)

    if args.print_items:
        if args.items_of_interest == ["All"]:
            best_in_slots.print_best_in_slot_items()
        else:
            for item in args.items_of_interest:
                best_in_slots.print_bosses_where_item_is_best_in_slot(item)
    if args.print_bosses:
        for boss in bosses_of_interest:
            best_in_slots.print_best_in_slot_items_for_boss(boss, setups_to_print=args.setups_to_print)


if __name__ == '__main__':
    main()
