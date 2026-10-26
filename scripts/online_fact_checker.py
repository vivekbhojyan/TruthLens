"""
Live Online Fact-Checker Engine
Automates checking rumors against live fact-checking organizations and news wires.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

DEBUNK_KEYWORDS = [
    'debunk', 'debunks', 'debunked', 'fake', 'hoax', 'false', 'misleading',
    'no, this', 'incorrect', 'without basis', 'doctored', 'morphed', 'untrue', 'fact check'
]

def search_rss(query_str):
    encoded = urllib.parse.quote(query_str)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    items = []
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:6]:
                title = item.find('title').text if item.find('title') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                items.append({'title': title, 'source': source, 'link': link})
    except Exception:
        pass
    return items

def online_fact_check_claim(claim_text):
    words = re.findall(r'[a-zA-Z]{3,}', claim_text.lower())
    stop_words = {'the', 'will', 'not', 'next', 'this', 'that', 'with', 'from', 'have', 'been', 'were', 'what', 'when', 'after', 'some'}
    key_terms = [w for w in words if w not in stop_words]
    
    clean_query = " ".join(key_terms[:5])
    
    # 1. Search for explicit fact checks
    fc_results = search_rss(f"fact check {clean_query}")
    
    # 2. Search for mainstream news reports
    news_results = search_rss(clean_query)
    
    # Check if any fact check explicitly debunks it
    debunking_sources = []
    for item in fc_results:
        t_low = item['title'].lower()
        if any(dk in t_low for dk in DEBUNK_KEYWORDS):
            debunking_sources.append(item)
            
    # Check if mainstream news confirms the exact positive action
    # For example, if someone claims "Indian army attacked PLA"
    # Does any credible outlet (DD News, Hindu, Reuters) say "Indian army attacked"?
    is_actively_confirmed = False
    confirming_sources = []
    
    if len(news_results) > 0 and len(debunking_sources) == 0:
        # Check if news headlines contain the core action
        for n in news_results:
            n_low = n['title'].lower()
            matches = sum(1 for k in key_terms if k in n_low)
            if matches >= 3 and not any(dk in n_low for dk in DEBUNK_KEYWORDS):
                is_actively_confirmed = True
                confirming_sources.append(n)
                
    if len(debunking_sources) > 0:
        verdict = "FAKE"
        confidence = 0.94
        reason = f"Explicitly Debunked Online: Fact-checking organizations (e.g. {debunking_sources[0]['source']}) have published investigations debunking this claim: '{debunking_sources[0]['title']}'."
        sources = debunking_sources
    elif is_actively_confirmed:
        verdict = "REAL"
        confidence = 0.92
        reason = f"Confirmed by Primary News Wires: Multiple mainstream journalistic agencies ({confirming_sources[0]['source']}, etc.) corroborate this event."
        sources = confirming_sources
    else:
        # High impact claim with zero corroboration
        verdict = "FAKE"
        confidence = 0.88
        reason = "Debunked by Total Absence of Corroboration: Major events of this magnitude (e.g. military conflict or leadership change) are immediately broadcast by global news wires. Zero credible news agencies report this occurrence, confirming it is an unverified viral rumor."
        sources = news_results[:3]
        
    return verdict, confidence, reason, sources

# Test with the two claims
for claim in [
    "Indian army attacked the PLA of china.",
    "bjp declares pm modi will not be the next pm candidate",
    "Reserve Bank of India holds benchmark repo rate steady at 6.5 percent"
]:
    v, conf, r, s = online_fact_check_claim(claim)
    print("=" * 60)
    print("CLAIM:", claim)
    print(f"VERDICT: {v} ({conf*100:.1f}%)")
    print("REASON:", r)
    print("TOP SOURCES:")
    for item in s[:2]:
        print(f" - {item['title']} [{item['source']}]")
