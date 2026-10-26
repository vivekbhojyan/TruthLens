"""
NLP Dataset Generation & Text Synthesis Script
Generates realistic news headlines and body text aligned with dataset.csv metadata
(article_id, source, word_count, sentiment_score, exclamation_count, all_caps_pct, label, political_lean).
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set deterministic seed for reproducibility
np.random.seed(42)
random.seed(42)

df = pd.read_csv("dataset_cleaned.csv")

# Realistic Real News Headlines & Body Paragraphs across Domains
real_domains = [
    {
        "domain": "Economy & Markets",
        "headline_templates": [
            "Federal Reserve Signals Measured Interest Rate Adjustments Amid Inflation Trends",
            "Global Supply Chain Indices Moderate as Port Congestion Eases Quarterly",
            "Central Bank Publishes Comprehensive Fiscal Audit Following Monetary Review",
            "Treasury Department Reports Modest Growth in Domestic Manufacturing Output",
            "Energy Sector Investments Pivot Toward Renewable Grid Infrastructure Upgrades",
            "Bilateral Trade Agreement Finalized to Reduce Tariffs on Agricultural Exports"
        ],
        "body_templates": [
            "Financial analysts and central banking officials convened this week to review the latest economic indicators. The quarterly report highlighted a steady stabilization in wholesale price indices, supported by resilient consumer spending and stabilized energy markets. According to official government data released on Tuesday, industrial productivity increased by 1.4 percent year-over-year, aligning with consensus projections. Economists emphasize that long-term macroeconomic stability remains contingent on fiscal policy discipline and international trade cooperation.",
            "Representatives from commerce ministries and multilateral trade institutions completed bilateral negotiations today, ratifying a framework designed to streamline customs clearance and harmonize cross-border tariffs. Official documentation shows that export volumes increased moderately over the past two quarters, despite localized logistics bottlenecks. Industry stakeholders expressed cautious optimism, citing lower compliance overhead and increased supply chain predictability."
        ]
    },
    {
        "domain": "Science, Health & Environment",
        "headline_templates": [
            "Peer-Reviewed Clinical Trial Demonstrates Efficacy of Novel Immunotherapy Protocol",
            "Atmospheric Research Team Deploys Satellite Constellation for Ocean Heat Tracking",
            "Health Ministry Updates Pediatric Vaccination Guidelines Based on Multicenter Study",
            "Geological Survey Detects Low-Magnitude Tectonic Activity Along Regional Fault",
            "Renewable Energy Grid Achieves Record Efficiency Milestone in Independent Audit",
            "Epidemiological Surveillance Network Confirms Seasonal Decline in Respiratory Infections"
        ],
        "body_templates": [
            "A collaborative study conducted across university medical centers and published in a leading peer-reviewed journal has confirmed positive outcomes in early-phase clinical evaluations. Researchers monitored patient cohorts over a 24-month observation window, observing statistically significant therapeutic responses with standard safety profiles. The lead investigator noted during a press briefing that subsequent Phase III multi-site trials are scheduled to commence next quarter under regulatory oversight.",
            "Environmental scientists utilizing high-resolution orbital sensors reported updated measurements regarding marine surface temperatures and coastal currents. Data collected across forty monitoring buoys indicate gradual fluctuations consistent with decadal meteorological models. The research institute published its open-access methodology to encourage independent verification by international climate consortia."
        ]
    },
    {
        "domain": "Policy, Technology & Governance",
        "headline_templates": [
            "Parliamentary Committee Concludes Public Hearings on Digital Privacy Framework",
            "Municipal Council Approves Comprehensive Urban Transit Modernization Plan",
            "Cybersecurity Directorate Issues Standards for Critical Infrastructure Resilience",
            "Supreme Court Delivers Unanimous Ruling on Administrative Jurisdictional Limits",
            "Telecom Regulatory Authority Allocates New Frequency Bands for Rural Broadband",
            "State Education Board Adopts Revised STEM Curriculum Following Expert Panel Review"
        ],
        "body_templates": [
            "Legislative representatives concluded three weeks of committee hearings addressing regulatory oversight for digital data systems and consumer protection. Testimony was provided by academic researchers, civil liberties organizations, and industry representatives. The finalized draft legislation emphasizes transparency in automated decision systems, mandatory disclosure of data breaches, and standardized audit procedures across telecommunication providers.",
            "Local government officials and civil engineering consultants voted to authorize capital funding for municipal transit upgrades. The multi-phase development involves replacing aging rail equipment, deploying low-emission commuter buses, and digitizing signaling operations. Public review sessions will be conducted monthly to ensure fiscal transparency and adherence to environmental impact guidelines."
        ]
    }
]

# Sensationalist / Clickbait Fake News Headlines & Body Paragraphs
fake_domains = [
    {
        "domain": "Conspiracy & Cover-up",
        "headline_templates": [
            "BOMBSHELL LEAK: Secret Shadow Government Documents Exposed Online Before Total Blackout",
            "MAINSTREAM MEDIA SILENT: Whistleblower Reveals Shocking Hidden Surveillance Project",
            "THEY CANNOT HIDE THIS ANYMORE: Leaked Video Shows What Really Happened Behind Closed Doors",
            "TOP OFFICIAL FIRED AFTER ATTEMPTING TO EXPOSE THE TRUTH TO THE PUBLIC",
            "EMERGENCY WARNING: Elite Insiders Caught Planning Massive Coordinated Global Takeover",
            "PROOF REVEALED: Deep State Operation Exposed by Anonymous Intelligence Insider"
        ],
        "body_templates": [
            "In an unbelievable turn of events that mainstream news channels refuse to cover, an anonymous insider has leaked explosive confidential files revealing a massive coordinated cover-up. Sources claim that powerful globalists and secret agencies have been manipulating records for years to control the population. Millions of citizens are waking up to this shocking truth before the internet gets shut down. Share this urgent report immediately before authorities delete it from every server forever.",
            "A brave whistleblower has come forward with undeniable smoking-gun evidence proving what millions have suspected all along. Deep inside locked vaults, shadowy elites were caught plotting the ultimate deception against honest citizens. The mainstream press is in complete panic mode, desperately trying to censor and ban anyone who asks questions. Do not let them silence the truth; spread this story everywhere right now."
        ]
    },
    {
        "domain": "Miracle Cures & Science Hoaxes",
        "headline_templates": [
            "DOCTORS ARE STUNNED: Ancient Backyard Plant Eradicates Severe Illness in Just 48 Hours",
            "BIG PHARMA HYSTERIA: Revolutionary Natural Cure They Kept Banned for Decades Is Finally Exposed",
            "SCIENTISTS BAFFLED: Miracle Superfood Cures Every Known Chronic Condition Over Night",
            "CONFIDENTIAL LAB SECRETS: The 100% Free Kitchen Remedy That Big Hospitals Want Banned",
            "SHOCKING DISCOVERY: Harvard Professor Claims Common Spice Reverses Aging Process Completely",
            "THE MEDICAL CARTEL EXPOSED: Why They Do Not Want You to Know About This Simple Secret"
        ],
        "body_templates": [
            "Greedy pharmaceutical giants are scrambling to shut down an explosive underground report revealing a miraculous natural remedy that cures all ailments effortlessly. Top doctors were threatened with losing their medical licenses if they ever revealed this simple 3-ingredient mixture found in common kitchens. Big pharma makes billions keeping people sick, but thousands of former patients are now reporting miraculous instant cures. Read the censored recipe right now before it is taken down.",
            "A renegade physician has broken decades of strict secrecy to expose the horrifying truth about modern hospital treatments. In a viral underground interview, he revealed how ordinary household spices completely regenerate failing organs and reverse cellular aging without prescription pills. The medical establishment is trying desperately to scrub this video from the web. Act fast before access is blocked."
        ]
    },
    {
        "domain": "Fabricated Scandals & Outrage",
        "headline_templates": [
            "CAUGHT ON CAMERA: High-Ranking Politician In Massive Illegal Bribe Scandal Exposed Live",
            "IT IS OVER FOR THEM: Smoking Gun Audio Recording Leaked Online Hours Ago",
            "PANIC IN THE CAPITAL: Shocking Evidence Found Inside Secret Safe Changes Everything",
            "TREASON CHARGES PENDING: Military Enters Headquarters as Treacherous Plot Unfolds",
            "BREAKING SCANDAL: Massive Voter Machine Fraud Caught in 4K High Definition Video",
            "TOTAL CHAOS: Insider Reveals Secret Plan to Seize All Private Bank Accounts Overnight"
        ],
        "body_templates": [
            "Explosive leaked audio has sent shockwaves through the political establishment, exposing treasonous corruption and illicit millions transferred into offshore secret accounts. High-ranking figures were caught bragging about deceiving the public and manipulating policy behind guarded gates. Insiders report emergency meetings taking place right now as panicked leaders look for scapegoats. The public is furious and demanding immediate arrests of everyone involved.",
            "Guards and high-level personnel watched in disbelief as military investigators raided private offices late last night, seizing encrypted hard drives containing proof of the greatest heist in modern history. Whistleblowers confirmed that high-level officials plotted to confiscate savings and silence critics. The corporate media is actively blacking out the story, but the truth can no longer be contained."
        ]
    }
]

# Generate synthesized text aligned with each row
headlines = []
bodies = []
publish_dates = []

start_date = datetime(2025, 1, 1)

for idx, row in df.iterrows():
    is_fake = (row['label'] == 'FAKE')
    exclamation_cnt = int(row['exclamation_count'])
    all_caps_ratio = float(row['all_caps_pct'])
    sentiment = float(row['sentiment_score'])
    
    # Generate publish date
    random_days = random.randint(0, 365)
    pub_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    publish_dates.append(pub_date)
    
    if is_fake:
        domain_choice = random.choice(fake_domains)
        base_headline = random.choice(domain_choice['headline_templates'])
        base_body = random.choice(domain_choice['body_templates'])
        
        # Format exclamation marks according to exclamation_count
        if exclamation_cnt > 0:
            excl_str = "!" * min(exclamation_cnt, 5)
            headline = f"{base_headline}{excl_str}"
        else:
            headline = base_headline
            
        # Add sensationalist sentiment amplification
        if sentiment < -0.3:
            base_body += " The public outrage is catastrophic, and the devastation caused by this corrupt betrayal is sickening and tragic."
        elif sentiment > 0.3:
            base_body += " This glorious, miraculous breakthrough is the most wonderful victory for freedom and health in human history!"
            
        # Add exclamation marks to body if needed
        if exclamation_cnt > 3:
            base_body = base_body.replace(".", "! ", min(exclamation_cnt - 2, 4))
            
    else:
        domain_choice = random.choice(real_domains)
        headline = random.choice(domain_choice['headline_templates'])
        base_body = random.choice(domain_choice['body_templates'])
        
        # Real news uses formal tone
        if sentiment < -0.3:
            base_body += " Independent analysts noted potential headwinds and fiscal risks that warrant persistent monitoring."
        elif sentiment > 0.3:
            base_body += " Government and institutional stakeholders expressed confidence that strategic benchmarks will be satisfied."
            
        if exclamation_cnt > 0:
            # Real articles rarely have multiple exclamations, but match column if needed
            headline += "."
            
    headlines.append(headline)
    bodies.append(base_body)

# Assemble comprehensive dataset
df['headline'] = headlines
df['body_text'] = bodies
df['publish_date'] = publish_dates

# Reorder columns logically
cols = [
    'article_id', 'headline', 'body_text', 'source', 'publish_date',
    'word_count', 'sentiment_score', 'exclamation_count', 'all_caps_pct',
    'political_lean', 'label'
]
df_nlp = df[cols]
df_nlp.to_csv("news_dataset_nlp.csv", index=False)
print(f"Generated news_dataset_nlp.csv with {len(df_nlp)} articles!")
print("Sample NLP records:")
print(df_nlp[['article_id', 'headline', 'label']].head())
