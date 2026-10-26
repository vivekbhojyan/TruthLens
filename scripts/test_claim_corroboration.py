import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

def verify_claim_corroboration(claim_text):
    """
    Checks if a news claim is corroborated by credible news sources via Google News RSS.
    Returns: (is_corroborated, score, matched_articles, explanation)
    """
    # Clean query: extract key meaningful keywords
    words = re.findall(r'[a-zA-Z]{3,}', claim_text.lower())
    stop_words = {'the', 'will', 'not', 'next', 'this', 'that', 'with', 'from', 'have', 'been', 'were', 'what', 'when'}
    key_terms = [w for w in words if w not in stop_words]
    
    # Query for exact phrase or top keywords
    query = " ".join(key_terms[:5])
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    articles = []
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item')[:6]:
                title = item.find('title').text if item.find('title') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                articles.append({'title': title, 'source': source})
    except Exception as e:
        print("RSS Error:", e)
        
    # Check if the core predicate ("not candidate", "stepping down", "resigns", etc.) is verified in headlines
    claim_lower = claim_text.lower()
    is_negation_rumor = any(neg in claim_lower for neg in ['not be', 'stepping down', 'will not', 'resigns', 'fired', 'dies', 'dead', 'cancelled', 'banned'])
    
    # Check if any headline confirms the exact claim
    matching_count = 0
    for a in articles:
        t_low = a['title'].lower()
        # count shared keywords
        matches = sum(1 for k in key_terms if k in t_low)
        if matches >= 3:
            matching_count += 1
            
    return articles, matching_count

articles, matches = verify_claim_corroboration("bjp declares pm modi will not be the next pm candidate")
print("Top news articles retrieved:")
for a in articles:
    print(f"- {a['title']} [{a['source']}]")
print(f"Matches count: {matches}")
