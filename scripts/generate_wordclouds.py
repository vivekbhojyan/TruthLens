"""
Word Cloud and NLP Feature Visualizations
Generates word clouds for REAL vs FAKE news articles and n-gram frequency charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re

df = pd.read_csv("news_dataset_nlp.csv")

# Combine headline and body
df['full_text'] = df['headline'] + " " + df['body_text']

real_text = " ".join(df[df['label'] == 'REAL']['full_text'])
fake_text = " ".join(df[df['label'] == 'FAKE']['full_text'])

custom_stopwords = set(STOPWORDS).union({
    'said', 'will', 'year', 'new', 'one', 'two', 'also', 'according', 'state'
})

# WordCloud for REAL news
wc_real = WordCloud(
    width=800, height=450, background_color='white',
    colormap='Greens', stopwords=custom_stopwords, max_words=100
).generate(real_text)

# WordCloud for FAKE news
wc_fake = WordCloud(
    width=800, height=450, background_color='black',
    colormap='Reds', stopwords=custom_stopwords, max_words=100
).generate(fake_text)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

axes[0].imshow(wc_real, interpolation='bilinear')
axes[0].set_title("Word Cloud — Verified Genuine News (REAL)", fontsize=14, fontweight='bold', pad=12, color='#1e8449')
axes[0].axis('off')

axes[1].imshow(wc_fake, interpolation='bilinear')
axes[1].set_title("Word Cloud — Fabricated / Sensational News (FAKE)", fontsize=14, fontweight='bold', pad=12, color='#c0392b')
axes[1].axis('off')

plt.tight_layout()
plt.savefig("visualizations/viz_6_wordclouds_real_vs_fake.png", dpi=300)
plt.close()
print("Saved viz_6_wordclouds_real_vs_fake.png successfully!")
