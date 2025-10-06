# Collect Stock Data
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
import requests
import os

# === NEW ML & ENV IMPORTS ===
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv

# Load API keys from .env if available
load_dotenv()
api_key = os.getenv("NEWS_API_KEY", "5ca6d0ffe59c40849fc610215bf0a146")  # fallback to hardcoded

# ===== Params =====
start_date = "2025-02-05"
end_date = datetime.now().strftime('%Y-%m-%d')

# ===== Stock =====
nvidia_stock = yf.Ticker("NVDA")
stock_data = nvidia_stock.history(start=start_date, end=end_date)
stock_data.reset_index(inplace=True)

# ===== NewsAPI =====
url = 'https://newsapi.org/v2/everything'
params = {
    'q': 'Nvidia',
    'from': (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'),
    'sortBy': 'relevancy',
    'apiKey': api_key,
    'pageSize': 100,
    'language': 'en'
}

resp = requests.get(url, params=params)
data = resp.json()
if data.get('status') != 'ok':
    raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")

news_data = pd.DataFrame(data['articles'])[['publishedAt', 'title']]
news_data.columns = ['date', 'headline']

# ===== NLP =====
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if not isinstance(text, str): return ""
    words = word_tokenize(text)
    words = [w for w in words if w.isalpha()]
    words = [w for w in words if w.lower() not in stop_words]
    return ' '.join(words)

news_data['cleaned_headline'] = news_data['headline'].apply(preprocess_text)

# ===== Sentiment =====
analyzer = SentimentIntensityAnalyzer()
def get_sentiment_score(text):
    return analyzer.polarity_scores(text or "")['compound']

news_data['sentiment_score'] = news_data['cleaned_headline'].apply(get_sentiment_score)

# ===== Dates/Aggregation =====
news_data['date'] = pd.to_datetime(news_data['date']).dt.date
stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date

aggregated_sentiment = news_data.groupby('date', as_index=False)['sentiment_score'].sum()

# ===== Merge (left join keeps all trading days) =====
combined_data = (
    stock_data[['Date', 'Close']]
    .merge(aggregated_sentiment, left_on='Date', right_on='date', how='left')
    .drop(columns=['date'])
)
combined_data['sentiment_score'] = combined_data['sentiment_score'].fillna(0.0)

# === Auto-limit plot to the news window ===
if not aggregated_sentiment.empty:
    news_start = aggregated_sentiment['date'].min()
    news_end   = aggregated_sentiment['date'].max()
    plot_mask  = (combined_data['Date'] >= news_start) & (combined_data['Date'] <= news_end)
    plot_data  = combined_data.loc[plot_mask].copy()
    if plot_data.empty:
        plot_data = combined_data.copy()
else:
    plot_data = combined_data.copy()

# --- sanity check ---
if plot_data['Close'].isna().all():
    raise RuntimeError("All Close values are NaN after merge. Check ticker data/column names.")

# ====== ML PART: Predict next-day return from sentiment ======
# Create target: next-day price change (% return)
plot_data['Return'] = plot_data['Close'].pct_change().shift(-1)  # predict tomorrow's return

# Drop last row (NaN target) and align features/target
ml_data = plot_data.dropna().copy()
X = ml_data[['sentiment_score']]   # features (can add more later)
y = ml_data['Return']

# Build pipeline: scaling + RidgeCV regression
model = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge', RidgeCV(alphas=[0.1, 1.0, 10.0]))
])

# Use TimeSeriesSplit for proper CV
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv, scoring='r2')

print("R^2 scores across folds:", scores)
print("Mean R^2:", scores.mean())

# Fit final model on all data
model.fit(X, y)
ml_data['Predicted_Return'] = model.predict(X)

# ===== Plot actual vs predicted =====
fig, ax = plt.subplots(figsize=(14,6))
ax.plot(ml_data['Date'], ml_data['Return'], label="Actual Return")
ax.plot(ml_data['Date'], ml_data['Predicted_Return'], label="Predicted Return")
ax.set_title("Nvidia: Actual vs Predicted Next-Day Return (from sentiment)")
ax.legend()
plt.show()

# ===== Plot Stock + Sentiment as before =====
fig, ax1 = plt.subplots(figsize=(14, 7))
ax1.set_xlabel('Date')
ax1.set_ylabel('Nvidia Stock Price')
line1 = ax1.plot(
    plot_data['Date'], plot_data['Close'],
    label='Nvidia Stock Price', linewidth=2.2, zorder=3
)
ymin, ymax = plot_data['Close'].min(), plot_data['Close'].max()
pad = (ymax - ymin) * 0.05 if ymax > ymin else 1
ax1.set_ylim(ymin - pad, ymax + pad)

locator = AutoDateLocator()
ax1.xaxis.set_major_locator(locator)
ax1.xaxis.set_major_formatter(ConciseDateFormatter(locator))

ax2 = ax1.twinx()
ax2.set_ylabel('Aggregated Sentiment Score')
colors = ['green' if v >= 0 else 'red' for v in plot_data['sentiment_score']]
bars = ax2.bar(
    plot_data['Date'], plot_data['sentiment_score'],
    color=colors, alpha=0.6, zorder=1, width=1.0
)

ax1.set_zorder(2)
ax1.patch.set_alpha(0)

plt.title('Nvidia Stock Price vs Aggregated Sentiment Score')
fig.legend([line1[0], bars], ['Nvidia Stock Price', 'Aggregated Sentiment Score'],
           loc='upper left', bbox_to_anchor=(0.1, 0.9))
fig.tight_layout()
plt.show()
