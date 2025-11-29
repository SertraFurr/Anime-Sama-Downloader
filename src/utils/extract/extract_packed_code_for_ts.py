from utils.var import print_status, Colors
import re
from bs4 import BeautifulSoup
import requests

def extract_packed_code_for_ts(html_content):
    pattern = r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)\)\)"
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3)), match.group(4).split('|')
    print("No packed JavaScript code found.")
    return None, None, None, None
