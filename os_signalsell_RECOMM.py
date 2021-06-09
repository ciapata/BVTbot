# Based off Firewatch custsignalmod.py

from tradingview_ta import TA_Handler, Interval, Exchange
# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob

import time

MY_EXCHANGE = 'BINANCE'
MY_SCREENER = 'CRYPTO'
MY_FIRST_INTERVAL = Interval.INTERVAL_1_MINUTE
MY_SECOND_INTERVAL = Interval.INTERVAL_5_MINUTES
MY_THIRD_INTERVAL = Interval.INTERVAL_15_MINUTES
PAIR_WITH = 'USDT'
DEBUG = True

TIME_TO_WAIT = 1 # Minutes to wait between analysis
SIGNAL_NAME = 'os_signalsell_RECOMM'
SIGNAL_FILE = 'signals/' + SIGNAL_NAME + '.sell'
TICKERS = 'signalsell_tickers.txt'

# if DEBUG: TICKERS = 'test_' + TICKERS

def analyze(pairs):
    taMax = 0
    taMaxCoin = 'none'
    signal_coins = {}
    first_analysis = {}
    second_analysis = {}
    third_analysis = {}
    first_handler = {}
    second_handler = {}
    third_handler = {}
    
    if os.path.exists(SIGNAL_FILE):
        os.remove(SIGNAL_FILE)

    for pair in pairs:
        first_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_FIRST_INTERVAL,
            timeout= 10
        )
        second_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_SECOND_INTERVAL,
            timeout= 10
        )
        third_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_THIRD_INTERVAL,
            timeout= 10
        )

    for pair in pairs:
       
        try:
            first_analysis = first_handler[pair].get_analysis()
            second_analysis = second_handler[pair].get_analysis()
            third_analysis = third_handler[pair].get_analysis()
        except Exception as e:
            print(f'{SIGNAL_NAME}')
            print("Exception:")
            print(e)
            print (f'Coin: {pair}')
            print (f'First handler: {first_handler[pair]}')
            print (f'Second handler: {second_handler[pair]}')
            print (f'Second handler: {third_handler[pair]}')
            return
               
        first_recommendation = first_analysis.summary['RECOMMENDATION']
        second_recommendation = second_analysis.summary['RECOMMENDATION']
        third_recommendation = third_analysis.summary['RECOMMENDATION']
        
        if DEBUG:
            print(f'{SIGNAL_NAME}: {pair} First {first_recommendation} Second {second_recommendation} Third {third_recommendation}')
                
        if  (first_recommendation == "SELL" or first_recommendation == "STRONG_SELL") and \
            (second_recommendation == "SELL" or second_recommendation == "STRONG_SELL") and \
            (third_recommendation == "SELL" or third_recommendation == "STRONG_SELL"):

            print(f'{SIGNAL_NAME}: sell signal detected on {pair}')

            signal_coins[pair] = pair
            
            with open(SIGNAL_FILE,'a+') as f:
                f.write(pair + '\n')

    return signal_coins

def do_work():
    try:
        while True:
            if not os.path.exists(TICKERS):
                time.sleep((TIME_TO_WAIT*60))
                continue

            signal_coins = {}
            pairs = {}

            pairs=[line.strip() for line in open(TICKERS)]
            for line in open(TICKERS):
                pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
            
            print(f'{SIGNAL_NAME}: Analyzing {len(pairs)} coins')
            signal_coins = analyze(pairs)
            if len(signal_coins) == 0:
                print(f'{SIGNAL_NAME}: No coins above sell threshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis')
            else:
                print(f'{SIGNAL_NAME}: {len(signal_coins)} coins above sell treshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis')

            time.sleep((TIME_TO_WAIT*60))
    except Exception as e:
            print(f'{SIGNAL_NAME}: Exception: {e}')