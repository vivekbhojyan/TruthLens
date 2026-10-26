import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def check_google_news(query):
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    articles = []
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                articles.append({'title': title, 'source': source, 'pubDate': pubDate})
    except Exception as e:
        print("RSS Error:", e)
    return articles

news = check_google_news("bjp pm modi candidate")
print(f"Retrieved {len(news)} Google News articles:")
for n in news:
    print("-", n['title'], f"({n['source']})")
