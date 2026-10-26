"""
Comprehensive Multi-Domain News Corpus Builder
Generates a wide-vocabulary dataset covering real and fake news across politics,
elections, health, economy, science, global diplomacy, scandals, and conspiracy theories.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# Load original dataset to preserve its 500 records and column structure
orig_df = pd.read_csv("dataset.csv")

# 1. Comprehensive topic templates for diverse real news
real_topics = [
    # Indian & Global Politics
    ("Prime Minister Narendra Modi Inaugurates Multi-Billion Dollar High-Speed Rail Corridor",
     "Prime Minister Narendra Modi inaugurated the newly constructed high-speed transit corridor during a state ceremony attended by union ministers and infrastructure experts. Government officials confirmed the project was completed on schedule and under budget, providing improved connectivity across industrial zones. The Ministry of Railways reported that the network will enhance freight efficiency and reduce inter-city commute times."),
    ("Election Commission of India Issues Revised Guidelines for General Election Security",
     "The Election Commission of India held a high-level briefing today announcing updated security protocols and polling booth logistics for the upcoming general election. Chief Election Commissioners emphasized the deployment of central paramilitary forces, strict oversight of electronic voting machines, and comprehensive monitoring of model code of conduct compliance across all parliamentary constituencies."),
    ("Supreme Court of India Delivers Landmark Ruling on Electoral Funding Transparency",
     "A constitution bench of the Supreme Court of India delivered a unanimous verdict establishing strict transparency benchmarks for political campaign funding and donor disclosures. The bench held that citizens possess a fundamental right to know the financial origins of political organizations. Legal analysts praised the judicial directive as a critical milestone for democratic accountability."),
    ("Parliament Concludes Winter Session Passing Key Digital Data and Economic Bills",
     "Both houses of parliament concluded their scheduled legislative sessions today after passing major statutory frameworks addressing digital privacy, trade infrastructure, and telecommunications reform. Ministers from treasury and opposition benches participated in extensive clause-by-clause debates before the legislation was sent for presidential assent."),
    ("Narendra Modi Addresses G20 Summit Highlighting Sustainable Development and Digital Infrastructure",
     "Addressing world leaders at the international G20 leadership plenary, Prime Minister Narendra Modi advocated for multilateral collaboration on renewable energy transition, global south representation, and open digital public infrastructure. Bilateral discussions with partner heads of state focused on supply chain diversification and counter-terrorism cooperation."),
    ("Opposition Parties Form Joint Strategic Coordination Panel Ahead of Assembly Elections",
     "Leaders of major opposition parties convened in the capital to announce a formal seat-sharing mechanism and common minimum program ahead of state legislative elections. Spokespersons confirmed that joint campaign rallies and policy working groups will be launched starting next month."),
    ("Ministry of External Affairs Reaffirms Strategic Diplomatic Neutrality in Border Discussions",
     "The Ministry of External Affairs conducted bilateral diplomatic consultations today, underscoring India's commitment to peaceful territorial integrity and diplomatic dialogue. Special envoys emphasized that continuous military communications have successfully de-escalated localized tensions along northern border posts."),
     
    # Economy & Finance
    ("Reserve Bank of India Holds Benchmark Repo Rate Steady Amid Moderating Inflation",
     "The Monetary Policy Committee of the Reserve Bank of India voted unanimously to keep the key policy repo rate unchanged at 6.5 percent. Governor noted that domestic consumption indicators remain resilient while retail inflation is tracking within the central bank's target tolerance band of 4 plus or minus 2 percent."),
    ("Ministry of Finance Reports Record Monthly Goods and Services Tax Collections",
     "Gross revenue from the Goods and Services Tax surpassed historic monthly targets, reflecting sustained economic expansion and improved automated tax compliance. Revenue department statistics revealed double-digit growth in manufacturing and services sector tax collections across tier-1 and tier-2 metropolitan hubs."),
    ("Global Tech Giants Expand Semiconductor and Manufacturing Plants in India",
     "Major multinational electronics manufacturers signed formal investment memorandums to build state-of-the-art semiconductor fabrication and hardware assembly facilities. Industry analysts forecast the initiative will generate over 25,000 skilled engineering jobs and deepen domestic supply chains."),
     
    # Healthcare & Science
    ("Indian Council of Medical Research Publishes Nationwide Study on Diabetes Management",
     "Scientists at the Indian Council of Medical Research published peer-reviewed findings from a multi-year demographic health study. The clinical guidelines emphasize dietary interventions, routine glycemic screening, and early preventive pharmacotherapy to mitigate metabolic disorders."),
    ("ISRO Successfully Conducts Orbital Maneuver for Solar and Deep Space Research Craft",
     "Scientists at the Indian Space Research Organisation confirmed the flawless execution of an orbital insertion trajectory for its scientific observation satellite. Spacecraft telemetry confirmed all scientific payloads and imaging spectrographs are transmitting high-resolution atmospheric data to ground tracking stations."),
    ("World Health Organization Validates Phase III Trial Results for Malaria Vaccine",
     "International epidemiological panels certified safety and efficacy data from multicenter clinical trials evaluating an advanced pediatric malaria vaccine. Public health authorities noted that widespread deployment will significantly lower infant mortality across high-transmission geographic regions.")
]

# 2. Comprehensive topic templates for fake news, clickbait, rumors & conspiracy theories
fake_topics = [
    # Political Rumors & Disinformation
    ("SHOCKING CLAIM: Narendra Modi Will Not Be The Next Prime Minister Candidate Due To Secret Health Crisis",
     "An explosive underground political blog has stunned the nation by claiming that Prime Minister Narendra Modi will not be the next prime minister candidate and has secretly agreed to step down immediately. The unauthorized report claims panicked emergency meetings are taking place inside secret party bunkers to replace the entire leadership. Mainstream media is completely blacking out the story, but insiders claim the official announcement will shock the world. Share this before it gets deleted!"),
    ("BOMBSHELL LEAK: Election Voting Machines Rigged by International Hackers, Proof Exposed",
     "A brave whistleblower has leaked classified software code proving that thousands of electronic voting machines were secretly manipulated to flip votes! Independent investigators claim foreign intelligence agents installed backdoors into voting hardware. The electoral board is trying desperately to bury this video and censor anyone who speaks out. Demand an immediate audit right now before the election is stolen!"),
    ("SECRET AUDIO EXPOSED: High-Ranking Politicians Caught In Multi-Million Dollar Offshore Bribe Deal",
     "Tremors in the political establishment after an unedited undercover audio recording surfaced online showing top cabinet ministers negotiating illegal cash bribes with international oligarchs. Whistleblowers say military intelligence is preparing midnight raids on private estates. Millions of furious citizens are protesting on social media. Read the full leaked transcript right now!"),
    ("THEY DONT WANT YOU TO KNOW: Secret Plan to Cancel Currency Notes and Freeze All Bank Accounts Next Week",
     "Emergency warning to all citizens! A confidential memo leaked from central banking sources reveals that government authorities are preparing to suddenly demonetize high-denomination currency notes and freeze all personal checking accounts by midnight. Insiders urge everyone to withdraw all physical cash immediately before the financial lockdown goes into effect!"),
    ("ARREST WARRANT ISSUED: Top Opposition Leader Flees Country Disguised in Private Jet After Police Raid",
     "Dramatic scenes at the international airport as prominent opposition leaders were reportedly caught attempting to escape police custody in disguise! Eyewitnesses claim black SUVs surrounded the private tarmac following a sudden midnight treason warrant. The mainstream press is lying to protect them, but leaked cell phone footage reveals the truth!"),

    # Health & Miracle Cures Disinformation
    ("DOCTORS BAFFLED: Common Kitchen Herb Eradicates Stage 4 Cancer Cells Overnight, Big Pharma Panicking",
     "Greedy pharmaceutical billionaires are terrified after a courageous renegade doctor exposed a simple 2-ingredient kitchen remedy that destroys malignant tumors in less than 48 hours. Corrupt medical boards threatened to revoke his medical license if he told the public. Thousands of cured patients are sharing this underground miracle recipe across banned forums!"),
    ("CENSORED REPORT: New Vaccine Contains Nanotechnology Tracking Particles, Scientist Whistleblower Murdered",
     "Horrifying secret documents recovered from an abandoned laboratory reveal that routine public immunizations contain microscopic tracking microchips designed to monitor citizens 24/7. The lead researcher was found dead under mysterious circumstances just hours before testifying. Protect your family and spread this uncensored truth everywhere!"),
     
    # Science & Apocalypse Hoaxes
    ("NASA EMERGENCY WARNING: Giant Asteroid On Direct Collision Course With Earth Next Month, Government Hiding Truth",
     "Amateur astronomers have confirmed what space agencies are desperately keeping secret: a massive rogue asteroid is headed directly for earth on a catastrophic impact trajectory. Elite billionaires have already begun fleeing to subterranean nuclear bunkers while keeping the public in the dark. Stock up on food and water immediately before total collapse!"),
    ("ALIEN BODIES RETRIEVED: Leaked Underground Military Footage Shows Living Extraterrestrial Captured in Jungle",
     "Unbelievable leaked 4K military footage has confirmed that defense forces recovered extraterrestrial survivors from an uncharted UFO crash site. High-ranking intelligence officials have confirmed that global treaties were signed with alien visitors decades ago. Watch the shocking suppressed video before government censors wipe it off the web!")
]

# Build an expanded 1,200 article balanced corpus
expanded_records = []

# First, enrich the 500 rows from orig_df with realistic, matched content
for idx, row in orig_df.iterrows():
    is_fake = (row['label'] == 'FAKE')
    excl = int(row['exclamation_count'])
    caps = float(row['all_caps_pct'])
    sent = float(row['sentiment_score'])
    
    if is_fake:
        tpl_hl, tpl_body = random.choice(fake_topics)
    else:
        tpl_hl, tpl_body = random.choice(real_topics)
        
    expanded_records.append({
        'article_id': int(row['article_id']),
        'headline': tpl_hl,
        'body_text': tpl_body,
        'source': row['source'],
        'publish_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        'word_count': int(row['word_count']),
        'sentiment_score': float(row['sentiment_score']),
        'exclamation_count': excl,
        'all_caps_pct': caps,
        'political_lean': row['political_lean'],
        'label': row['label']
    })

# Add 500 additional diverse training rows with rich real-world political, economic & health vocabulary
curr_id = 501
for _ in range(350):
    # Real news variations
    hl, body = random.choice(real_topics)
    expanded_records.append({
        'article_id': curr_id,
        'headline': hl,
        'body_text': body,
        'source': f"source_{random.randint(1, 20)}",
        'publish_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        'word_count': len(body.split()),
        'sentiment_score': round(random.uniform(-0.4, 0.4), 3),
        'exclamation_count': random.randint(0, 2),
        'all_caps_pct': round(random.uniform(0.01, 0.08), 3),
        'political_lean': random.choice(['Center', 'Left', 'Right', 'Unknown']),
        'label': 'REAL'
    })
    curr_id += 1

for _ in range(350):
    # Fake news variations
    hl, body = random.choice(fake_topics)
    # inject sensational buzzwords
    buzz = random.choice(["BOMBSHELL:", "SHOCKING:", "LEAKED:", "MUST READ:", "BREAKING:"])
    if not hl.startswith(buzz):
        hl = f"{buzz} {hl}"
    expanded_records.append({
        'article_id': curr_id,
        'headline': hl,
        'body_text': body,
        'source': f"source_{random.randint(1, 20)}",
        'publish_date': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        'word_count': len(body.split()),
        'sentiment_score': round(random.uniform(-0.9, 0.9), 3),
        'exclamation_count': random.randint(3, 14),
        'all_caps_pct': round(random.uniform(0.12, 0.35), 3),
        'political_lean': random.choice(['Center', 'Left', 'Right', 'Unknown']),
        'label': 'FAKE'
    })
    curr_id += 1

comp_df = pd.DataFrame(expanded_records)
comp_df.to_csv("news_dataset_nlp.csv", index=False)
print(f"Built comprehensive news_dataset_nlp.csv with {len(comp_df)} articles across diverse domains!")
print("Label counts:\n", comp_df['label'].value_counts())
