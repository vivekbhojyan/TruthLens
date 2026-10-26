import urllib.request
import urllib.parse
import re
import json

def check_claim_web(query):
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            html = response.read().decode('utf-8')
            # Extract titles and snippets
            titles = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)
            for s in snippets[:4]:
                clean_s = re.sub(r'<[^>]+>', '', s).strip()
                if clean_s:
                    results.append(clean_s)
    except Exception as e:
        print("Search error:", e)
    return results

snippets = check_claim_web("bjp declares pm modi will not be next pm candidate")
print(f"Retrieved {len(snippets)} search verification snippets:")
for s in snippets:
    print("-->", s)
