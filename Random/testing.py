import numpy as np
# Monkey-patch missing alias so pandas_ta’s `from numpy import NaN` works
np.NaN = np.nan

import pandas as pd
import yfinance as yf
import pandas_ta as ta

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import precision_score, precision_recall_curve

import matplotlib.pyplot as plt


def fetch_assets(start_date="2000-01-01"):
    """Download NVDA, SPY, VIX and merge into one DataFrame."""
    tickers = {
        'NVDA': 'NVDA',
        'SPY': 'SPY',
        'VIX': '^VIX'
    }
    df = pd.concat({
        name: yf.Ticker(sym).history(period="max")['Close']
        for name, sym in tickers.items()
    }, axis=1)
    # if yf returns a MultiIndex column, drop the extra level
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df.loc[start_date:]


def add_basic_target(df, horizon=5):
    """
    Create a binary up/down target over `horizon` days:
      1 if (NVDA.shift(-horizon) / NVDA - 1) > 0, else 0
    """
    df['FutureRet'] = df['NVDA'].shift(-horizon) / df['NVDA'] - 1
    df['Target']    = (df['FutureRet'] > 0).astype(int)
    return df


def add_technical_features(df):
    """Compute TA indicators, lagged returns, volatility, and cross-asset signals."""
    # 1) Technical indicators via pandas_ta
    df['RSI_14']   = ta.rsi(df['NVDA'], length=14)
    df['MACD']     = ta.macd(df['NVDA'])['MACD_12_26_9']
    bb            = ta.bbands(df['NVDA'], length=20)
    df['BB_upper'] = bb['BBU_20_2.0']
    df['BB_lower'] = bb['BBL_20_2.0']
    df['ATR_14']   = ta.atr(df['High'], df['Low'], df['NVDA'], length=14)
    df['OBV']      = ta.obv(df['NVDA'], df['Volume'])
    # 2) Lagged returns & rolling volatility
    for lag in [1, 2, 5, 10]:
        df[f'Ret_{lag}'] = df['NVDA'] / df['NVDA'].shift(lag) - 1
    df['Vol_10'] = df['Ret_1'].rolling(10).std()
    df['Vol_30'] = df['Ret_1'].rolling(30).std()
    # 3) Cross-asset returns
    df['SPY_Ret_1'] = df['SPY'] / df['SPY'].shift(1) - 1
    df['VIX_Change'] = df['VIX'] - df['VIX'].shift(1)
    return df.dropna()


def tune_model(X, y):
    """Use TimeSeriesSplit + RandomizedSearchCV to pick best hyperparams."""
    tscv = TimeSeriesSplit(n_splits=5)
    param_dist = {
        'n_estimators':        [100, 200, 500],
        'max_depth':           [None, 5, 10],
        'min_samples_split':   [50, 100, 200]
    }
    rf = RandomForestClassifier(random_state=1, class_weight='balanced')
    gsearch = RandomizedSearchCV(
        rf, param_dist,
        n_iter=10,
        cv=tscv,
        scoring='precision',
        random_state=1,
        n_jobs=-1
    )
    gsearch.fit(X, y)
    print("Best RF params:", gsearch.best_params_)
    return gsearch.best_estimator_


def calibrate_threshold(model, X_val, y_val):
    """Find probability threshold that maximizes F1 on a validation slice."""
    probs = model.predict_proba(X_val)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_val, probs)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls)
    best_idx = np.nanargmax(f1_scores)
    print(f"Calibrated threshold = {thresholds[best_idx]:.2f}, F1 = {f1_scores[best_idx]:.3f}")
    return thresholds[best_idx]


def backtest(df, features, model, threshold, start=2500, step=250):
    """Walk-forward backtest, returning a concatenated DataFrame of predictions."""
    all_preds = []
    for end_train in range(start, len(df), step):
        train = df.iloc[:end_train]
        test  = df.iloc[end_train:end_train + step]

        model.fit(train[features], train['Target'])
        proba = model.predict_proba(test[features])[:, 1]
        preds = (proba >= threshold).astype(int)

        result = pd.DataFrame({
            'Target':     test['Target'],
            'Prediction': preds
        }, index=test.index)
        all_preds.append(result)

    return pd.concat(all_preds)


def main():
    # 1) Fetch & assemble
    df = fetch_assets()
    df = add_basic_target(df, horizon=5)
    df = add_technical_features(df)

    # define feature list after df is built
    global features
    features = [c for c in df.columns if c not in ('FutureRet', 'Target')]

    # 2) Split off a small hold-out for threshold calibration
    calib_slice = slice(-500, -250)
    X_cal = df.iloc[calib_slice][features]
    y_cal = df.iloc[calib_slice]['Target']

    # 3) Hyperparameter tuning on the rest
    train_slice = slice(0, -500)
    X_train = df.iloc[train_slice][features]
    y_train = df.iloc[train_slice]['Target']
    best_rf = tune_model(X_train, y_train)

    # 4) Calibrate threshold
    thresh = calibrate_threshold(best_rf, X_cal, y_cal)

    # 5) Backtest
    preds = backtest(df, features, best_rf, threshold=thresh)
    print("Backtest precision:", precision_score(preds['Target'], preds['Prediction']))

    # 6) Plot results
    preds[['Target', 'Prediction']].plot(title="NVDA Backtest (5-day horizon)")
    plt.show()

    # 7) BONUS / FUTURE:
    #    - Swap in XGBClassifier, LGBMClassifier or a stacked ensemble.
    #    - Pull in daily news headlines + apply VADER/FinBERT sentiment.
    #    - Fetch NVDA.options via yfinance for open-interest features.
    #    - Try ternary classification (up / flat / down).
    #    - Re-run tuning/calibration for each variant.


if __name__ == "__main__":
    main()
