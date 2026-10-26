"""
Exploratory Data Analysis (EDA) & Data Cleaning Script
Project: Fake News Detection Using NLP (HCLTech Industry Project 31)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

os.makedirs("visualizations", exist_ok=True)

# 1. Load dataset
data_path = "dataset.csv"
df = pd.read_csv(data_path)

print("=" * 60)
print("DATASET OVERVIEW & SUMMARY STATISTICS")
print("=" * 60)
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")
print(f"Column Names: {list(df.columns)}")
print("\nMissing Values:")
print(df.isnull().sum())
print("\nData Types:")
print(df.dtypes)
print("\nClass Distribution:")
class_counts = df['label'].value_counts()
print(class_counts)
print(f"REAL: {class_counts.get('REAL', 0)} ({class_counts.get('REAL', 0)/len(df)*100:.1f}%)")
print(f"FAKE: {class_counts.get('FAKE', 0)} ({class_counts.get('FAKE', 0)/len(df)*100:.1f}%)")

print("\nNumerical Feature Summary by Label:")
print(df.groupby('label')[['word_count', 'sentiment_score', 'exclamation_count', 'all_caps_pct']].mean())

# 2. Visualization 1: Class Distribution
plt.figure(figsize=(7, 5))
palette = {'REAL': '#2ecc71', 'FAKE': '#e74c3c'}
ax = sns.countplot(data=df, x='label', palette=palette, order=['REAL', 'FAKE'])
plt.title("Distribution of Real vs Fake News Articles", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Article Label", fontsize=12)
plt.ylabel("Number of Articles", fontsize=12)
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f'{height}\n({height/len(df)*100:.1f}%)',
                (p.get_x() + p.get_width() / 2., height / 2),
                ha='center', va='center', fontsize=11, color='white', fontweight='bold')
plt.tight_layout()
plt.savefig("visualizations/viz_1_class_distribution.png", dpi=300)
plt.close()
print("Saved viz_1_class_distribution.png")

# 3. Visualization 2: Correlation Heatmap
plt.figure(figsize=(8, 6))
num_cols = ['word_count', 'sentiment_score', 'exclamation_count', 'all_caps_pct']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt=".3f", cmap="coolwarm", cbar=True, vmin=-1, vmax=1,
            linewidths=1, square=True, mask=mask)
plt.title("Feature Correlation Heatmap", fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("visualizations/viz_2_feature_correlation_heatmap.png", dpi=300)
plt.close()
print("Saved viz_2_feature_correlation_heatmap.png")

# 4. Visualization 3: Exclamation Count & All Caps % Comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Exclamation count
sns.boxplot(data=df, x='label', y='exclamation_count', palette=palette, ax=axes[0], order=['REAL', 'FAKE'])
axes[0].set_title("Exclamation Mark Frequency by Article Class", fontsize=13, fontweight='bold')
axes[0].set_xlabel("Article Label", fontsize=11)
axes[0].set_ylabel("Exclamation Mark Count", fontsize=11)

# All Caps Percentage
sns.boxplot(data=df, x='label', y='all_caps_pct', palette=palette, ax=axes[1], order=['REAL', 'FAKE'])
axes[1].set_title("Capitalized Characters Percentage by Article Class", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Article Label", fontsize=11)
axes[1].set_ylabel("All-Caps Ratio", fontsize=11)

plt.tight_layout()
plt.savefig("visualizations/viz_3_exclamation_allcaps_distribution.png", dpi=300)
plt.close()
print("Saved viz_3_exclamation_allcaps_distribution.png")

# 5. Visualization 4: Political Lean vs Authenticity
plt.figure(figsize=(10, 5))
lean_order = ['Left', 'Center', 'Right', 'Unknown']
sns.countplot(data=df, x='political_lean', hue='label', palette=palette, order=lean_order)
plt.title("Article Authenticity Distribution across Political Leans", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Political Lean", fontsize=12)
plt.ylabel("Article Count", fontsize=12)
plt.legend(title="Label", loc='upper right')
plt.tight_layout()
plt.savefig("visualizations/viz_4_political_lean_vs_authenticity.png", dpi=300)
plt.close()
print("Saved viz_4_political_lean_vs_authenticity.png")

# 6. Visualization 5: Sentiment Score Density Distribution
plt.figure(figsize=(9, 5))
sns.kdeplot(data=df[df['label']=='REAL']['sentiment_score'], label='REAL', fill=True, color='#2ecc71', alpha=0.4, linewidth=2)
sns.kdeplot(data=df[df['label']=='FAKE']['sentiment_score'], label='FAKE', fill=True, color='#e74c3c', alpha=0.4, linewidth=2)
plt.title("Sentiment Score Density: Real vs Fake News", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Sentiment Score (-1.0 Negative to +1.0 Positive)", fontsize=12)
plt.ylabel("Density", fontsize=12)
plt.axvline(0, color='grey', linestyle='--', alpha=0.7)
plt.legend(title="Article Class")
plt.tight_layout()
plt.savefig("visualizations/viz_5_sentiment_density.png", dpi=300)
plt.close()
print("Saved viz_5_sentiment_density.png")

# 7. Clean and save dataset_cleaned.csv
df_cleaned = df.copy()
# Check for any whitespace or formatting anomalies
df_cleaned['label'] = df_cleaned['label'].str.strip().str.upper()
df_cleaned['source'] = df_cleaned['source'].str.strip()
df_cleaned['political_lean'] = df_cleaned['political_lean'].str.strip()
df_cleaned.to_csv("dataset_cleaned.csv", index=False)
print("Saved dataset_cleaned.csv successfully!")
print("=" * 60)
