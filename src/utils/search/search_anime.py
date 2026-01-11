import requests
from bs4 import BeautifulSoup
from src.utils.config.config import get_cookies
from src.var import get_domain

def search_anime(query):
    url = f"https://{get_domain()}/template-php/defaut/fetch.php"
    headers = {
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Cookie": "cf_clearance=" + get_cookies()
    }
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
            if href:
                results.append({"title": title, "url": href})
        return results
    except Exception:
        return []
