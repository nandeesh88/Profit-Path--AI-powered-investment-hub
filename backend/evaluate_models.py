"""
Model Evaluation Script
Computes: Accuracy, Loss, Precision, F1 Score, Confusion Matrix
for all classification models in the Profit-Path AI engine.
"""
import os
import sys
import numpy as np
import pandas as pd
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    log_loss,
    precision_score,
    f1_score,
    confusion_matrix,
    classification_report,
    mean_squared_error,
    r2_score,
)

from ai_engine.train_models import RealFinancialDataTrainer

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "evaluation_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

RISK_LABELS = ["Low Risk", "Medium Risk", "High Risk"]


def plot_confusion_matrix(cm, model_name, labels):
    """Save a confusion matrix heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title(f"Confusion Matrix — {model_name}")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    logger.info(f"  Saved: {path}")


def evaluate():
    trainer = RealFinancialDataTrainer()

    # ── Generate data ──────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  PROFIT-PATH MODEL EVALUATION")
    logger.info("=" * 60)
    logger.info("\n[1/4] Generating training data from real market data...")

    df = trainer.generate_training_data_from_real_market(n_samples=1000)

    X = trainer.get_feature_matrix(df)
    y_risk = df["risk_label"].values
    y_return = df["expected_return"].values

    # ── Train / Test split ─────────────────────────────────────────
    X_train, X_test, y_risk_train, y_risk_test, y_ret_train, y_ret_test = (
        train_test_split(X, y_risk, y_return, test_size=0.2, random_state=42, stratify=y_risk)
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    # ── Train models ───────────────────────────────────────────────
    logger.info("[2/4] Training models...")

    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression

    rf_clf = RandomForestClassifier(
        n_estimators=200, max_depth=10, min_samples_split=5,
        min_samples_leaf=2, random_state=42, n_jobs=-1,
    )
    rf_clf.fit(X_train_sc, y_risk_train)

    lr_clf = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    lr_clf.fit(X_train_sc, y_risk_train)

    gb_reg = GradientBoostingRegressor(
        n_estimators=150, max_depth=5, learning_rate=0.1,
        subsample=0.8, random_state=42,
    )
    gb_reg.fit(X_train_sc, y_ret_train)

    # ── Evaluate classifiers ───────────────────────────────────────
    logger.info("[3/4] Computing metrics on TEST set (20 %)...\n")

    classifiers = {
        "Random Forest Classifier": rf_clf,
        "Logistic Regression": lr_clf,
    }

    for name, clf in classifiers.items():
        y_pred = clf.predict(X_test_sc)
        y_proba = clf.predict_proba(X_test_sc)

        acc = accuracy_score(y_risk_test, y_pred)
        loss = log_loss(y_risk_test, y_proba)
        prec = precision_score(y_risk_test, y_pred, average="weighted")
        f1 = f1_score(y_risk_test, y_pred, average="weighted")
        cm = confusion_matrix(y_risk_test, y_pred)

        logger.info("-" * 60)
        logger.info(f"  MODEL: {name}")
        logger.info("-" * 60)
        logger.info(f"  Accuracy  : {acc:.4f}  ({acc:.2%})")
        logger.info(f"  Log Loss  : {loss:.4f}")
        logger.info(f"  Precision : {prec:.4f}  (weighted)")
        logger.info(f"  F1 Score  : {f1:.4f}  (weighted)")
        logger.info(f"\n  Confusion Matrix:")
        logger.info(f"  {RISK_LABELS}")
        for i, row in enumerate(cm):
            logger.info(f"  {RISK_LABELS[i]:>12s}  {row}")
        logger.info("")
        logger.info(f"  Full Classification Report:")
        logger.info(classification_report(y_risk_test, y_pred, target_names=RISK_LABELS))

        plot_confusion_matrix(cm, name, RISK_LABELS)

    # ── Evaluate regressor ─────────────────────────────────────────
    y_ret_pred = gb_reg.predict(X_test_sc)
    mse = mean_squared_error(y_ret_test, y_ret_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_ret_test, y_ret_pred)

    logger.info("-" * 60)
    logger.info("  MODEL: Gradient Boosting Regressor (Return Prediction)")
    logger.info("-" * 60)
    logger.info(f"  MSE       : {mse:.4f}")
    logger.info(f"  RMSE      : {rmse:.4f}")
    logger.info(f"  R² Score  : {r2:.4f}  ({r2:.2%})")
    logger.info("")

    # ── Summary table ──────────────────────────────────────────────
    logger.info("[4/4] Summary")
    logger.info("=" * 60)
    header = f"{'Model':<35} {'Accuracy':>9} {'Loss':>9} {'Precision':>10} {'F1':>9}"
    logger.info(header)
    logger.info("-" * 60)
    for name, clf in classifiers.items():
        y_pred = clf.predict(X_test_sc)
        y_proba = clf.predict_proba(X_test_sc)
        acc = accuracy_score(y_risk_test, y_pred)
        loss = log_loss(y_risk_test, y_proba)
        prec = precision_score(y_risk_test, y_pred, average="weighted")
        f1 = f1_score(y_risk_test, y_pred, average="weighted")
        logger.info(f"{name:<35} {acc:>9.4f} {loss:>9.4f} {prec:>10.4f} {f1:>9.4f}")

    logger.info("=" * 60)
    logger.info(f"\nConfusion matrix plots saved to: {RESULTS_DIR}/")
    logger.info("Done ✅")


if __name__ == "__main__":
    evaluate()
