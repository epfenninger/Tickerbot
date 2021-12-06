import pandas as pd
import numpy as np
import yfinance as yf
import datetime

def options_chain(symbol):
    
    tk = yf.Ticker(symbol)
    # Expiration dates
    exps = tk.options
    # Get options for each expiration
    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt = pd.DataFrame().append(opt.calls).append(opt.puts)
        opt['expirationDate'] = e
        options = options.append(opt, ignore_index=True)

    # Bizarre error in yfinance that gives the wrong expiration date
    # Add 1 day to get the correct expiration date
    #options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days = 1)
    #options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    
    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(
        lambda x: "C" in x)
    
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options['mark'] = (options['bid'] + options['ask']) / 2 # Calculate the midpoint of the bid-ask
    
    # Drop unnecessary and meaningless columns
    options = options.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options

def pc_ratio_oi(symbol):
  chain = options_chain(symbol)
  call = 0
  put = 0

  calls = chain.loc[chain['CALL'] == True, 'openInterest']
  puts = chain.loc[chain['CALL'] == False, 'openInterest']
  calls = calls.dropna()
  puts = puts.dropna()
  for callVol in calls:
    call = call + callVol

  for putVol in puts:
    put = put + putVol

  return round(put/call,3) 


def getTicker(symbol):
  tk = yf.Ticker(symbol)
  hist = tk.history(period='1d')
  last_quote = hist['Close'][0]
  return "Last quote for " + symbol + " is : " + str(round(last_quote,5))

def majorHolders(symbol):
  tk = yf.Ticker(symbol)
  return tk.major_holders

def tuteHolders(symbol):
  tk = yf.Ticker(symbol)
  return tk.institutional_holders

def analysts(symbol):
  tk = yf.Ticker(symbol)
  return tk.recommendations


def get_IV(symbol):
  chain = options_chain(symbol)
  numRows = len(chain.index) -1  
  totalIV = 0
  totalOI = 0  
  openInterest = chain['openInterest']
  weightedIVList = (chain['impliedVolatility'] * chain['openInterest'])
  weightedIVList = weightedIVList.dropna()
  
  for iv in weightedIVList:
    totalIV = totalIV + iv

  for oi in openInterest:
    totalOI = totalOI + oi

  return totalIV/totalOI

def callInfo(symbol,num):
  tk = yf.Ticker(symbol)
  exps = tk.options
  calls = pd.DataFrame()
  chain = pd.DataFrame()

  if num == None:
    num = 1
  elif num == 'all':
    num = len(exps)  
  
  for e in range(0,num):
    opt = tk.option_chain(exps[e])
    opt = pd.DataFrame().append(opt.calls)
    opt['expirationDate'] = exps[e]
    calls = calls.append(opt, ignore_index=True)
  

  calls = calls.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice','contractSymbol','inTheMoney','bid','ask','impliedVolatility'])
  calls = calls.rename(columns = {"openInterest":"Call OI", "volume":"Call Volume"})
  calls = calls[['expirationDate','Call OI','Call Volume','strike']]
  
  return calls

def putInfo(symbol,num):
  tk = yf.Ticker(symbol)   
  exps = tk.options
  puts = pd.DataFrame()
  chain = pd.DataFrame()

  if num == None:
    num = 1        
  elif num == 'all':
    num = len(exps)

  for e in range(0,num):
    opt = tk.option_chain(exps[e])
    opt = pd.DataFrame().append(opt.puts)
    opt['expirationDate'] = exps[e]
    puts = puts.append(opt, ignore_index=True)
  
  puts = puts.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice','contractSymbol','inTheMoney','bid','ask','impliedVolatility'])
  puts = puts.rename(columns = {"openInterest":"Put OI", "volume":"Put Volume"})
  puts = puts[['expirationDate','Put OI','Put Volume','strike']]

  return puts

def getChain(symbol,num):
  calls = callInfo(symbol,num)
  puts = putInfo(symbol,num)

  chain = pd.concat([calls,puts],axis=1)
  chain = chain.loc[:,~chain.columns.duplicated()]
  chain.style.set_properties(**{'text-align': 'right'})
  chain = chain[['expirationDate','Call OI','Call Volume','strike','Put Volume','Put OI']]
  return chain


def pc_ratio_volume(symbol):
  chain = options_chain(symbol)
  calls = chain.loc[chain['CALL'] == True, 'volume']
  puts = chain.loc[chain['CALL'] == False, 'volume']

  calls = calls.dropna()
  puts = puts.dropna()

  callVol = 0
  putVol = 0

  for call in calls:
    callVol = callVol + call
    
  for put in puts:
    putVol = putVol + put

  return round(putVol/callVol,3)

def movers(symbol):
  calls = callInfo(symbol,'all')
  puts = putInfo(symbol,'all')

  calls = calls.sort_values(by='Call Volume', ascending=False)
  calls = calls[:10]
  puts = puts.sort_values(by='Put Volume', ascending=False)
  puts = puts[:10]
  movers = pd.DataFrame()
  movers = movers.append([calls,puts])

  return calls

print(movers('goev'))
