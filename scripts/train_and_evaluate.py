"""
Model Training, Benchmarking & Explainability Pipeline
Trains multiple NLP classifiers (TF-IDF + Classifiers, BERT Embeddings, Ensemble)
Evaluates on Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
Saves serialized models and generates confusion matrices, ROC curves, and LIME explanations.
"""

import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.pipeline import Pipeline
from lime.lime_text import LimeTextExplainer

os.makedirs("models", exist_ok=True)
os.makedirs("visualizations", exist_ok=True)

# 1. Load NLP dataset
df = pd.read_csv("news_dataset_nlp.csv")
df['full_text'] = df['headline'] + ". " + df['body_text']

# Target encoding: REAL = 0, FAKE = 1 (or string labels)
X = df['full_text']
y = df['label'].map({'REAL': 0, 'FAKE': 1})
class_names = ['REAL', 'FAKE']

# Train/Test Split (80% train, 20% test stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Dataset split: Train = {len(X_train)} samples, Test = {len(X_test)} samples")

# 2. Build Models with TF-IDF Pipelines
tfidf_params = {
    'ngram_range': (1, 2),
    'max_features': 5000,
    'stop_words': 'english',
    'sublinear_tf': True
}

base_models = {
    "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
    "Passive-Aggressive Classifier": CalibratedClassifierCV(
        PassiveAggressiveClassifier(max_iter=1000, random_state=42, C=0.5)
    ),
    "Linear SVM": CalibratedClassifierCV(LinearSVC(C=1.0, random_state=42, max_iter=2000)),
    "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
}

# 3. Fit TF-IDF Vectorizer
vectorizer = TfidfVectorizer(**tfidf_params)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Save vectorizer
joblib.dump(vectorizer, "models/tfidf_vectorizer.joblib")
print("Saved TF-IDF Vectorizer to models/tfidf_vectorizer.joblib")

# Train and evaluate individual models
results = []
trained_models = {}
y_probs = {}

for name, clf in base_models.items():
    clf.fit(X_train_vec, y_train)
    y_pred = clf.predict(X_test_vec)
    
    # Probability estimation for ROC-AUC
    if hasattr(clf, "predict_proba"):
        prob = clf.predict_proba(X_test_vec)[:, 1]
    else:
        prob = clf.decision_function(X_test_vec)
        prob = (prob - prob.min()) / (prob.max() - prob.min())
        
    y_probs[name] = prob
    trained_models[name] = clf
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, prob)
    
    results.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1-Score": round(f1, 4),
        "ROC-AUC": round(roc, 4)
    })
    
    # Save model
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    joblib.dump(clf, f"models/{safe_name}.joblib")

# 4. Build and Train Soft-Voting Ensemble Classifier
print("\nTraining Soft-Voting Ensemble Classifier (LR + PAC + MNB + SVM)...")
ensemble_clf = VotingClassifier(
    estimators=[
        ('lr', base_models["Logistic Regression"]),
        ('pac', base_models["Passive-Aggressive Classifier"]),
        ('mnb', base_models["Multinomial Naive Bayes"]),
        ('svm', base_models["Linear SVM"])
    ],
    voting='soft'
)
ensemble_clf.fit(X_train_vec, y_train)
ens_pred = ensemble_clf.predict(X_test_vec)
ens_prob = ensemble_clf.predict_proba(X_test_vec)[:, 1]

y_probs["Ensemble (Soft Voting)"] = ens_prob
trained_models["Ensemble (Soft Voting)"] = ensemble_clf
joblib.dump(ensemble_clf, "models/ensemble_voting.joblib")

results.append({
    "Model": "Ensemble (Soft Voting)",
    "Accuracy": round(accuracy_score(y_test, ens_pred), 4),
    "Precision": round(precision_score(y_test, ens_pred), 4),
    "Recall": round(recall_score(y_test, ens_pred), 4),
    "F1-Score": round(f1_score(y_test, ens_pred), 4),
    "ROC-AUC": round(roc_auc_score(y_test, ens_prob), 4)
})

# Complete End-to-End Pipeline for Instant Inference & LIME
inference_pipeline = Pipeline([
    ('vectorizer', vectorizer),
    ('classifier', ensemble_clf)
])
joblib.dump(inference_pipeline, "models/fake_news_pipeline.joblib")
print("Saved complete pipeline to models/fake_news_pipeline.joblib")

# 5. Display Benchmark Results Table
results_df = pd.DataFrame(results).sort_values(by="F1-Score", ascending=False)
results_df.to_csv("models/model_comparison_results.csv", index=False)

print("\n" + "=" * 70)
print("MODEL BENCHMARK PERFORMANCE COMPARISON")
print("=" * 70)
print(results_df.to_string(index=False))
print("=" * 70)

# 6. Visualization: Model Comparison Bar Chart
plt.figure(figsize=(12, 6))
metrics_plot = pd.melt(results_df, id_vars=['Model'], value_vars=['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
                       var_name='Metric', value_name='Score')

sns.barplot(data=metrics_plot, x='Model', y='Score', hue='Metric', palette='viridis')
plt.title("Comparative Performance Metrics Across NLP Models", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Classifier Model", fontsize=12)
plt.ylabel("Score (0.0 - 1.0)", fontsize=12)
plt.ylim(0.7, 1.05)
plt.xticks(rotation=15, ha='right')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig("visualizations/viz_7_model_metrics_comparison.png", dpi=300)
plt.close()
print("Saved viz_7_model_metrics_comparison.png")

# 7. Visualization: ROC Curves Comparison
plt.figure(figsize=(9, 7))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

for (name, prob), color in zip(y_probs.items(), colors):
    fpr, tpr, _ = roc_curve(y_test, prob)
    roc_score = auc(fpr, tpr)
    plt.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC = {roc_score:.3f})")

plt.plot([0, 1], [0, 1], color='navy', lw=1.5, linestyle='--', label="Random Guess (AUC = 0.500)")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
plt.ylabel("True Positive Rate (Sensitivity)", fontsize=12)
plt.title("Receiver Operating Characteristic (ROC) Curves", fontsize=14, fontweight='bold', pad=15)
plt.legend(loc="lower right", fontsize=10)
plt.tight_layout()
plt.savefig("visualizations/viz_8_roc_curves_comparison.png", dpi=300)
plt.close()
print("Saved viz_8_roc_curves_comparison.png")

# 8. Visualization: Confusion Matrix for Best Model (Ensemble)
plt.figure(figsize=(7, 6))
cm = confusion_matrix(y_test, ens_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['REAL (0)', 'FAKE (1)'],
            yticklabels=['REAL (0)', 'FAKE (1)'],
            annot_kws={'size': 14, 'weight': 'bold'})
plt.title("Confusion Matrix — Soft Voting Ensemble", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Predicted Class", fontsize=12)
plt.ylabel("Actual True Class", fontsize=12)
plt.tight_layout()
plt.savefig("visualizations/viz_9_confusion_matrix_ensemble.png", dpi=300)
plt.close()
print("Saved viz_9_confusion_matrix_ensemble.png")

# 9. LIME Explainability Demonstration
print("\n" + "=" * 70)
print("GENERATING LIME EXPLAINABILITY ARTIFACTS")
print("=" * 70)

explainer = LimeTextExplainer(class_names=class_names)

# Pick one sample predicted as FAKE and one as REAL
test_sample_fake = X_test[y_test == 1].iloc[0]
test_sample_real = X_test[y_test == 0].iloc[0]

exp_fake = explainer.explain_instance(
    test_sample_fake,
    inference_pipeline.predict_proba,
    num_features=10,
    labels=[1]
)
exp_fake.save_to_file("visualizations/lime_explanation_fake_article.html")
print("Saved lime_explanation_fake_article.html")

exp_real = explainer.explain_instance(
    test_sample_real,
    inference_pipeline.predict_proba,
    num_features=10,
    labels=[0]
)
exp_real.save_to_file("visualizations/lime_explanation_real_article.html")
print("Saved lime_explanation_real_article.html")

print("\nModel training, benchmarking, and LIME explanations completed successfully!")
