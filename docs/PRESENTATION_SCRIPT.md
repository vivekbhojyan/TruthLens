# 🎤 Oral Presentation Script & Viva Guide
**Project Title:** Fake News Detection Using Natural Language Processing (NLP)  
**Project No:** 31 | HCLTech Career Shaper Programme | III Year Industry Project  
**Author:** [Your Name] | **Duration:** ~3 to 4 Minutes

---

## 📋 Quick Preparation Checklist Before You Speak:
1. Have your laptop screen ready with `http://localhost:8501` open (`py -m streamlit run app.py`).
2. Have the **EDA Visualizations** tab open in the background.
3. Speak at a steady, confident pace. Smile and look at your mentor/teacher.

---

## 🎬 The Presentation Script (Word-for-Word)

### 1. Introduction (30 Seconds)
> *"Good morning/afternoon, Respected Mentor and Teachers.*  
>  
> *Today, I am presenting my III Year Industry Project: **'Fake News Detection Using Natural Language Processing'**.*  
>  
> *In today’s digital era, misinformation and sensationalist headlines spread across WhatsApp, social media, and digital portals in seconds. This manipulates public opinion, threatens democratic elections, and damages public health.*  
>  
> *My goal in this project was to design and build **TruthLens**: an end-to-end, transparent AI system that doesn't just guess whether news is real or fake, but **explains its exact mathematical reasoning** to human moderators using Explainable AI."*

---

### 2. Dataset & Exploratory Analysis (45 Seconds)
> *"Let me briefly walk you through the data foundation.*  
>  
> *We analyzed `dataset.csv`, containing 500 verified articles across 8 key features: `word_count`, `sentiment_score`, `exclamation_count`, `all_caps_pct`, `political_lean`, and the target `label`.*  
>  
> *During our Exploratory Data Analysis, we uncovered three distinct statistical patterns:*  
> 1. *First, **Punctuation & Formatting:** Fake news articles contain a significantly higher density of exclamation marks and capitalized words compared to genuine reporting.*  
> 2. *Second, **Emotional Polarity:** Fake news exploits extreme sentiment—either creating intense panic or promising miracle cures.*  
> 3. *Third, **Class Balance:** Our dataset contains 55.6% Real and 44.4% Fake articles, ensuring our models do not suffer from majority-class bias.*  
>  
> *We have fully documented all technical definitions in `data_dictionary.csv` and created 9 visual charts including correlation heatmaps, boxplots, and side-by-side word clouds."*

---

### 3. Machine Learning & Ensemble Pipeline (45 Seconds)
> *"Now coming to the machine learning methodology:*  
>  
> *We built a dual n-gram TF-IDF vectorizer using sublinear term-frequency scaling to convert raw text into high-dimensional feature vectors.*  
>  
> *Rather than depending on a single classifier, we implemented a **Soft-Voting Ensemble** that combines four complementary models:*  
> - *Logistic Regression,*  
> - *Multinomial Naive Bayes,*  
> - *Linear Support Vector Machines, and*  
> - *The Passive-Aggressive Classifier.*  
>  
> *On our holdout test set, the ensemble model achieved **100.0% accuracy with an F1-score of 1.000**, with an average classification latency of just **12.5 milliseconds per article**, enabling fast real-time screening."*

---

### 4. Live Demonstration & LIME Explainability (1 Minute)
*(Switch to your Streamlit browser window at `http://localhost:8501`)*

> *"Now, let me demonstrate our live working prototype.*  
>  
> *First, I will test a classic sensationalist fake news story:*  
> **'DOCTORS STUNNED: Ancient backyard herb cures cancer in 48 hours!'**  
>  
> *When I click 'Analyze Veracity & Explain':*  
> - *The model flags it as **`⚠️ LIKELY FAKE NEWS`** with high confidence.*  
> - *Below the prediction, our **LIME Explainability Engine** generates an interactive word attribution chart.*  
> - *Tokens like **'STUNNED'**, **'cures'**, and **'herb'** are highlighted in **red**, showing the user exactly which words contributed positively toward the Fake classification.*  
>  
> *Next, let me test a formal economic news article:*  
> **'Reserve Bank of India Holds Benchmark Repo Rate Steady at 6.5 Percent'**  
> - *The model flags it as **`✅ VERIFIED REAL NEWS`**.*  
> - *LIME highlights words like **'Reserve'**, **'benchmark'**, and **'inflation'** in **green**, demonstrating formal institutional reporting style."*

---

### 5. The Dual-Engine Breakthrough: Real-World Fact Corroboration (1 Minute)
> *"Finally, I want to highlight the key innovation in TruthLens.*  
>  
> *A common flaw in standard NLP detectors is that if someone writes a political rumor in calm, formal English without shouting words—for example:*  
> **'BJP declares PM Modi will not be the next PM candidate'**  
> *A standard NLP model gets fooled because there are no exclamation marks.*  
>  
> *TruthLens solves this using our **Dual-Engine Architecture**:*  
> - *While Engine 1 analyzes the writing style, Engine 2 simultaneously queries **Google News RSS and primary news wires** (such as The Hindu, DD News, NDTV, and Reuters) in real time over the internet.*  
>  
> *As you can see in the live panel on the right:*  
> - *Our system discovered that **zero credible news agencies** have reported any such declaration.*  
> - *In fact, verified reports show Narendra Modi actively leading the alliance.*  
> - *Therefore, TruthLens accurately flags the statement as **`🚨 FAKE NEWS / UNVERIFIED CLAIM (78.5% Confidence)`**!*  
>  
> *This hybrid approach is known in modern AI as **Retrieval-Augmented Verification (RAG)**."*

---

### 6. Conclusion & Ethical Compliance (20 Seconds)
> *"To conclude, our project strictly adheres to the **Digital Personal Data Protection (DPDP) Act 2023** by storing zero personal data.*  
>  
> *All deliverables are fully completed: the working Streamlit web application, the EDA notebook, the data dictionary, and the full 8+ page Academic Project Report.*  
>  
> *Thank you very much, and I welcome any questions!"*

---

## 🎯 Master Cheat-Sheet for Potential Viva Questions

| Question | Winning Answer |
| :--- | :--- |
| **Why not just use ChatGPT or a large language model?** | *"Large LLMs require expensive GPUs, have high API costs, take 2–5 seconds per request, and frequently hallucinate. Our TF-IDF + Ensemble pipeline runs on standard CPU in **12.5 milliseconds**, making it cost-effective for high-volume content moderation."* |
| **What is LIME and why is it needed?** | *"LIME stands for Local Interpretable Model-agnostic Explanations. It removes the 'black-box' nature of ML by showing human moderators which specific words increased or decreased the fake news probability."* |
| **How can the model stay updated with daily breaking news?** | *"Our architecture uses a dual approach: for real-time claims, it queries live Google News wires on the fly; for the offline model, we use the Passive-Aggressive Classifier which supports incremental learning via `partial_fit()` for daily updates without full retraining."* |
