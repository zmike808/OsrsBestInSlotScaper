from BestInSlots import BestInSlots
from BossesScraper import BossesScraper

import argparse


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


def scrape_bosses(bosses_url):
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
    return bosses_of_interest


def main():
    parser = create_arg_parser()

    args = parser.parse_args()

    if args.bosses_of_interest == ["All"]:
        bosses_url = "https://oldschool.runescape.wiki/w/Boss"
        bosses_of_interest = scrape_bosses(bosses_url)
    else:
        bosses_of_interest = args.bosses_of_interest

    best_in_slots = BestInSlots(bosses_of_interest)

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
