import requests
from bs4 import BeautifulSoup

from gui.utils import get_domain


def search_anime_query(query, headers=None):
    url = f"https://{get_domain()}/template-php/defaut/fetch.php"

    data = {"query": query}

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for a in soup.find_all('a'):
            href = a.get('href')
            h3 = a.find('h3')
            title = h3.text.strip() if h3 else "Unknown"
            img = a.find('img')["src"]
            if href:
                results.append({"title": title, "url": href, "img": img})

        return results
    except Exception:
        return []
