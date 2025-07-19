stock_ret = 0.1
rf = 0.03
stock_weight = 0.5
portfolio_ret = rf * (1 - stock_weight) + stock_ret * stock_weight
portfolio_ret

portfolio_initial_value = 1000
portfolio_end_value = portfolio_initial_value * (1 + portfolio_ret)
portfolio_end_value


def port_end_value(stock_ret=0.1, rf=0.03, stock_weight=0.5, portfolio_initial_value=1000):
    portfolio_ret = rf * (1 - stock_weight) + stock_ret * stock_weight
    portfolio_end_value = portfolio_initial_value * (1 + portfolio_ret)
    return portfolio_end_value


port_end_value()

port_end_value(0.05, 0.03, 0.7)

import random

stock_mean = 0.1
stock_std = 0.2
random.normalvariate(stock_mean, stock_std)

stock_ret = random.normalvariate(stock_mean, stock_std)
print(f'running with stock return {stock_ret:.1%}')
port_end_value(stock_ret)

n_iter = 3
outputs = []
for i in range(n_iter):
    stock_ret = random.normalvariate(stock_mean, stock_std)
    result = port_end_value(stock_ret)
    outputs.append(result)
outputs


def port_end_value_simulations(stock_mean=0.1, stock_std=0.2, stock_weight=0.5, n_iter=1000):
    outputs = []
    for i in range(n_iter):
        stock_ret = random.normalvariate(stock_mean, stock_std)
        result = port_end_value(stock_ret, stock_weight=stock_weight)
        outputs.append(result)
    return outputs


results = port_end_value_simulations()
print(f'There are {len(results)} results. First five:')
results[:5]

import pandas as pd

df = pd.DataFrame()
df['Portfolio End Values'] = results
df.plot.hist(bins=100)

df.plot.kde()

percentiles = [i / 20 for i in range(1, 20)]
percentiles

df['Portfolio End Values'].quantile(percentiles)

(df['Portfolio End Values'] >= 1050).astype(int).mean()

df['Portfolio End Values'] >= 1050

(df['Portfolio End Values'] >= 1050).astype(int)

import matplotlib.pyplot as plt


def create_dataframe_from_results(results):
    df = pd.DataFrame()
    df['Portfolio End Values'] = results
    return df


def visualize_results(df):
    df.plot.hist(bins=100)
    plt.show()  # makes plot show right now, which we will need when running this multiple times


def probability_table(df):
    percentiles = [i / 20 for i in range(1, 20)]
    return df['Portfolio End Values'].quantile(percentiles)


def probability_of_objective(df, desired_cash=1050):
    return (df['Portfolio End Values'] >= desired_cash).astype(int).mean()


def model_outputs(results, desired_cash=1050):
    df = create_dataframe_from_results(results)
    visualize_results(df)
    prob_table = probability_table(df)
    prob_objective = probability_of_objective(df, desired_cash=desired_cash)
    return prob_table, prob_objective


def display_model_summary(results, desired_cash=1050):
    prob_table, prob_objective = model_outputs(results, desired_cash=desired_cash)
    print('Probability Table')
    print(prob_table.apply(lambda x: f'${x:.2f}'))  # a way of formatting a pandas series
    print('')
    print(f'Probability of getting ${desired_cash:,.0f} in cash: {prob_objective:.1%}')
    print('')


display_model_summary(results)

from IPython.display import HTML, display

display(HTML('<h2>My Title</h2>'))


def display_header(header):
    return display(HTML(f'<h2>{header}</h2>'))


display_header('Another Title')

weights = [i / 10 for i in range(1, 10)]
weights

for weight in weights:
    display_header(f'Results with {weight:.0%} in the Stock')
    results = port_end_value_simulations(stock_weight=weight)
    display_model_summary(results)