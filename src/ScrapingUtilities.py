import requests

def construct_boss_strategy_url(boss):
    return "https://oldschool.runescape.wiki/w/" + boss.replace(" ", "_") + "/Strategies"


def url_is_good(url):
    good_url = False
    try:
        request = requests.get(url)
        if request.status_code == 200:
            good_url = True
    except:
        pass

    return good_url
