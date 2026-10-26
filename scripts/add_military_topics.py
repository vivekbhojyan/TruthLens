"""
Military & Conflict Topic Expander for Fake News Corpus
"""

import pandas as pd
import random
from datetime import datetime, timedelta

df = pd.read_csv("news_dataset_nlp.csv")

military_real = [
    ("Ministry of External Affairs Reaffirms Commitment to Peaceful Dialogue Along LAC",
     "The Ministry of External Affairs confirmed that diplomatic and military commander-level talks between India and China are progressing through established bilateral communication channels. Officials stated that both sides have maintained disengagement protocols in friction areas and denied unverified rumors of military aggression."),
    ("Indian Army Conducts Routine High-Altitude Preparedness Exercise in Northern Sector",
     "The Indian Army successfully concluded routine seasonal defensive maneuvers in the high-altitude Himalayan sector. Senior defense commanders reviewed logistics, aerial surveillance capabilities, and troop rotation schedules, emphasizing strict adherence to established international border agreements."),
    ("Indian Army Rebuts False Reports Alleging Border Encroachment or Skirmishes",
     "Defense spokespersons issued a categorical clarification refuting fabricated claims circulating on social media regarding border clashes. Military authorities confirmed the situation along the Line of Actual Control remains stable and governed by standard de-escalation protocols.")
]

military_fake = [
    ("WAR ALERT: Indian Army Officially Attacked PLA of China in Massive Midnight Offensive",
     "Shocking reports circulating online claim that after ongoing tensions, the Indian army has now officially attacked the PLA of China across disputed border posts. Unverified sources claim heavy casualties on both sides with fighter jets scrambled. Mainstream media is blacking out the war news as panicked authorities meet in emergency bunkers. Share this breaking alert immediately before all telecom networks are disconnected!"),
    ("BREAKING: Fierce Border Clash Erupts as Indian Armed Forces Launch Preemptive Strike on PLA",
     "Unbelievable leaked military communications claim that Indian army units launched a surprise cross-border strike against Chinese military bases. Social media is flooded with unconfirmed footage of explosions. The government is desperately trying to suppress the reports, but military insiders say full-scale hostilities have officially begun!"),
    ("SECRET CASUALTY REPORT: Indian Army Attacked Chinese Outposts After Provocation",
     "Confidential defense files leaked by an anonymous insider claim a major offensive was officially launched by Indian troops against Chinese PLA positions. Officials are actively censoring public reports to prevent panic across border states.")
]

new_rows = []
curr_id = df['article_id'].max() + 1

for _ in range(150):
    hl, body = random.choice(military_real)
    new_rows.append({
        'article_id': curr_id,
        'headline': hl,
        'body_text': body,
        'source': f"source_{random.randint(1, 20)}",
        'publish_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        'word_count': len(body.split()),
        'sentiment_score': round(random.uniform(-0.2, 0.2), 3),
        'exclamation_count': random.randint(0, 1),
        'all_caps_pct': round(random.uniform(0.01, 0.05), 3),
        'political_lean': random.choice(['Center', 'Left', 'Right', 'Unknown']),
        'label': 'REAL'
    })
    curr_id += 1

for _ in range(150):
    hl, body = random.choice(military_fake)
    new_rows.append({
        'article_id': curr_id,
        'headline': hl,
        'body_text': body,
        'source': f"source_{random.randint(1, 20)}",
        'publish_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        'word_count': len(body.split()),
        'sentiment_score': round(random.uniform(-0.8, -0.4), 3),
        'exclamation_count': random.randint(2, 10),
        'all_caps_pct': round(random.uniform(0.12, 0.30), 3),
        'political_lean': random.choice(['Center', 'Left', 'Right', 'Unknown']),
        'label': 'FAKE'
    })
    curr_id += 1

updated_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
updated_df.to_csv("news_dataset_nlp.csv", index=False)
print(f"Added military and geopolitical conflict data. Total records: {len(updated_df)}")
