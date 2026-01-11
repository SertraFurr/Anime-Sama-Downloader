import requests
import re
from bs4 import BeautifulSoup
from src.var import get_domain
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

def check_link_support(res, headers):
    try:
        r = requests.get(res['url'], headers=headers, timeout=5)
        if r.status_code == 200:
            content = r.text
            anime_matches = re.findall(r'panneauAnime\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', content)
            valid_anime = [m for m in anime_matches if m[0] != "nom" and m[1] != "url"]
            
            if valid_anime:
                res['support'] = "Anime Supported"
            else:
                scan_matches = re.findall(r'panneauScan\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', content)
                valid_scan = [m for m in scan_matches if m[0] != "nom" and m[1] != "url"]
                if valid_scan:
                    res['support'] = "Scans Unsupported"
                else:
                    res['support'] = "Unsupported"
        else:
            res['support'] = "Unknown"
    except Exception:
        res['support'] = "Unknown"
    return res

def search_anime(query, headers=None):
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
            if href:
                full_url = urljoin(f"https://{get_domain()}/", href)
                results.append({"title": title, "url": full_url, "support": None})
        
        if results:
            with ThreadPoolExecutor(max_workers=10) as executor:
                list(executor.map(lambda r: check_link_support(r, headers), results))
                
        return results
    except Exception:
        return []
