from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


def get_data(company_name='AAPL', period='5y', start=None, end=None):

  company = yf.Ticker(company_name)

  if start:
    hist = company.history(start=start, end=end)

  else:
    hist = company.history(period=period)

  hist = hist.asfreq('D')
  hist.bfill(inplace=True)

  return hist


def get_company_info(company_name='AAPL', param_info='website'):
  company = yf.Ticker(company_name)

  params = {
    'major_holders': company.major_holders,
    'recommendations_summary': company.recommendations_summary,
    'isin': company.isin,
    'news': company.news,
    'total': company.info
  }

  return params[param_info]


def plot_total_data(data, column='Close', path='./handlers/pics/total_data.png'):

  plt.figure(figsize=(15, 5))

  columns=['Open', 'High', 'Low', 'Close']

  if column == 'Total':
    fig = plt.plot(data[columns])
    plt.legend(columns)
  else:
    fig = plt.plot(data[column])
    plt.legend(column)

  plt.grid(True)
  plt.title('Общая динамика изменения стоимости акций компании')
  plt.xlabel('Дата')
  plt.ylabel('Цена')
  plt.savefig(path)


def plot_candelstick_chart(data, path='./handlers/pics/candelstick_data.png'):

  matplotlib_date = mdates.date2num(data.reset_index()['Date'])

  ohlc = np.vstack((matplotlib_date,
                    data['Open'],
                    data['High'],
                    data['Low'],
                    data['Close'])).T

  plt.figure(figsize=(15, 5))
  ax = plt.subplot()
  candlestick_ohlc(ax, ohlc, width=0.6, colorup='g', colordown='r')
  ax.xaxis_date()
  plt.title('Японские свечи')
  plt.xlabel('Дата')
  plt.ylabel('Цена')
  plt.xticks(rotation=45)
  plt.grid(True)
  plt.savefig(path)

