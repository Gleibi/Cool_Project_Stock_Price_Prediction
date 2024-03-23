from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from pickle import load, dump
import pandas as pd
from datetime import timedelta

from charts import get_data

def create_time_feature(df):

    df['dayofmonth'] = df['Date'].dt.day.apply(str)
    df['dayofweek'] = df['Date'].dt.dayofweek.apply(str)
    df['quarter'] = df['Date'].dt.quarter.apply(str)
    df['month'] = df['Date'].dt.month.apply(str)
    df['year'] = df['Date'].dt.year.apply(str)
    df['dayofyear'] = df['Date'].dt.dayofyear.apply(str)
    df['weekofyear'] = df['Date'].dt.isocalendar().week.apply(str)

    return df


def get_normalized_data(data):

  data['close_shift'] = data.Close.shift(1)
  data['target'] = data.Close - data.close_shift

  data = data[~data.close_shift.isna()]

  data.reset_index(inplace=True)

  data = create_time_feature(data)

  data['Date'] = data.Date.dt.date

  data.set_index('Date', inplace=True)

  return data


def generate_new_featrues(data):

  for w in [3, 5, 10, 30]:
    data[f'rolling_mean_{w}'] = data.target.rolling(window=w).mean().shift(1)
    data[f'rolling_std_{w}'] = data.target.rolling(window=w).std().shift(1)

  cols = ['Open', 'High', 'Low', 'Close']

  for col in cols:
    data[f'{col}_prev'] = data[col].shift(1)

  start_date = data.index.min() + timedelta(days=30) # чтобы не было пропусков в новых фичах

  data = data[data.index > start_date]


  final_cols = ['Open_prev', 'High_prev', 'Low_prev', 'Close_prev',
                'rolling_mean_3', 'rolling_mean_5', 'rolling_mean_10', 'rolling_mean_30',
                'rolling_std_3', 'rolling_std_5', 'rolling_std_10', 'rolling_std_30',
                'target'
                ]

  return data[final_cols]


def split_data(df: pd.DataFrame, test=True):
    X = df.copy()

    if test:
        y = X['target']
        X.drop('target', inplace=True, axis=1)

        return X, y

    return X


def preprocess_data(df: pd.DataFrame, test=True):

    if test:
        X_df, y_df = split_data(df)
    else:
        X_df = split_data(df, test=False)

    scaler = MinMaxScaler()
    X_df = scaler.fit_transform(X_df)

    if test:
        return X_df, y_df
    else:
        return X_df


def fit_and_save_model(X_df, y_df, path):

    model = GradientBoostingRegressor()
    model.fit(X_df, y_df)

    test_prediction = model.predict(X_df)
    mse = mean_squared_error(test_prediction, y_df) * -1

    with open(path, "wb") as file:
        dump(model, file)

    print(f"Model was saved to {path}")


def get_prediction(company_name, path):

  final_cols = ['Open_prev', 'High_prev', 'Low_prev', 'Close_prev',
              'rolling_mean_3', 'rolling_mean_5', 'rolling_mean_10', 'rolling_mean_30',
              'rolling_std_3', 'rolling_std_5', 'rolling_std_10', 'rolling_std_30'
              ]

  with open(path, "rb") as file:
    model = load(file)

  data = get_data(company_name=company_name, period='31d')

  data['close_shift'] = data.Close.shift(1)
  data['target'] = data.Close - data.close_shift

  cols = {'Open': 'Open_prev',
          'High': 'High_prev',
          'Low': 'Low_prev',
          'Close': 'Close_prev'}

  data.rename(columns=cols, inplace=True)


  for w in [3, 5, 10, 30]:
    data[f'rolling_mean_{w}'] = data.target.rolling(window=w).mean().shift(1)
    data[f'rolling_std_{w}'] = data.target.rolling(window=w).std().shift(1)


  test = data.tail(1)

  predict = model.predict(test[final_cols])

  return predict


def main_models(company_name='AAPL', path='model_weights/gbr.pkl'):

  data = get_data(company_name=company_name)

  normalized_data = get_normalized_data(data)
  new_features = generate_new_featrues(normalized_data)

  X, y = preprocess_data(new_features, test=True)

  fit_and_save_model(X, y, path)

  pred = get_prediction(company_name, path=path)

  return pred