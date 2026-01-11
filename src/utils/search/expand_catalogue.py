import re
import requests
from urllib.parse import urljoin
from src.utils.config.config import get_cookies

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

def expand_catalogue_url(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        matches = re.findall(r'panneauAnime\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', content)
        
        results = []
        seen_urls = set()
        
        for name, rel_url in matches:
            if name == "nom" or rel_url == "url":
                continue
                
            full_url = urljoin(url if url.endswith('/') else url + '/', rel_url)
            if not full_url.endswith('/'):
                full_url += '/'
            
            if full_url in seen_urls:
                continue
                
            seen_urls.add(full_url)
            results.append({"name": name, "url": full_url})
            
            if 'vostfr' in rel_url.lower():
                vf_rel = rel_url.lower().replace('vostfr', 'vf')
                vf_full = full_url.lower().replace('vostfr', 'vf')
                
                if vf_full not in seen_urls:
                    try:
                        probe = requests.head(vf_full, headers=headers, timeout=5)
                        if probe.status_code == 200:
                            vf_name = f"{name} (VF)"
                            results.append({"name": vf_name, "url": vf_full})
                            seen_urls.add(vf_full)
                    except:
                        pass

            
        return results
    except Exception:
        return []
