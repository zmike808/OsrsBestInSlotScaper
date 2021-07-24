import requests
from bs4 import BeautifulSoup


class BossesScraper:

    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        bosses = []
        for table in soup.find_all('table'):
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) > 0:
                    td = tds[0]
                    for a in td.find_all('a'):
                        title = a.get('title', '')
                        bosses.append(title)
        return bosses
