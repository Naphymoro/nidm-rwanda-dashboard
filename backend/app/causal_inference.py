import numpy as np
from sklearn.linear_model import LinearRegression


def average_treatment_effect(features, intervention, outcome):
    """
    Minimal ATE estimator using linear regression with controls.

    features: 2D array of covariates (e.g. trust, barrier, region dummies)
    intervention: 1D array (0/1 or intensity)
    outcome: 1D array (adoption)
    """
    X = np.column_stack([features, intervention])
    model = LinearRegression()
    model.fit(X, outcome)

    ate = model.coef_[-1]

    return {
        "ATE": float(ate),
        "interpretation": "Positive means intervention increases adoption"
    }


def counterfactual_effect(features, intervention, outcome):
    """
    Estimate counterfactual difference by toggling intervention.
    """
    X = np.column_stack([features, intervention])
    model = LinearRegression()
    model.fit(X, outcome)

    X_on = np.column_stack([features, np.ones_like(intervention)])
    X_off = np.column_stack([features, np.zeros_like(intervention)])

    y_on = model.predict(X_on)
    y_off = model.predict(X_off)

    return {
        "mean_with_intervention": float(np.mean(y_on)),
        "mean_without_intervention": float(np.mean(y_off)),
        "effect": float(np.mean(y_on - y_off))
    }
