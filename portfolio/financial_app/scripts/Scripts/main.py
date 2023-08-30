from .ticker.ticker_downloader import *
from .ticker.ticker_file import *
from .SEC import *
import os
import pandas as pd
import time

UPDATE_LIMIT = 500
class ticker_file_manager():

    def __init__(self,src = './financial_app/scripts/ticker', dest_data = './financial_app/scripts/ticker/data/ticker'):
        
        self.dest_data = dest_data          #data dest (should be folder containing data files)
        self.src = src                      #src (should be folder containing ticker_base)
        
        self.ticker_file = ticker_info(src)
        self.ticker_file.open_file()
        self.ticker_downloader = ticker_downloader(dest_data)

    def getWatchList(self):
        return self.ticker_file.getTickers()

    #adds items to watchlist
    def addToWatchList(self,ticker=''):
        if(ticker == ''): return False
        return self.ticker_file.add_ticker(ticker)
    
    #removes ticker from watchlist
    def removeFromWatchList(self,ticker=''):
        if(ticker == ''): return False
        return self.ticker_file.remove_ticker(ticker)
    
    #will update the ticker in question, otherwise return false
    def update(self,ticker=''):
        try:
            if not self.ticker_file.ticker_exists(ticker):
                if (self.ticker_file.add_ticker(ticker) == False):return False
            return self.ticker_downloader.save_as_csv(ticker=ticker)
        except Exception as e:
            print (e)
            return False
    
    #updates all ticker in the watchlist
    def update_all(self):
        try:
            temp = self.ticker_file.getTickers()
            for i in temp:
                self.update(i)
            return True
        
        except Exception  as e:
            return False
    
    #return DF of ticker in question
    #otherwise None if error
    def get_info_as_df(self,ticker=''):
        try:
            #csv exists for it so we return that otherwise we update
            if(os.path.exists(self.dest_data+'/'+ticker+'.csv')):
                df = pd.read_csv (self.dest_data+'/'+ticker+'.csv')
                return df
            else:
                print(self.ticker_downloader.export_as_df(ticker=ticker))
                return self.ticker_downloader.export_as_df(ticker=ticker)

        except Exception as e:
            print(e)
            return None
        

#Updating/downloading necessary data
def download_all_financials(src='./SEC_files/CIK_lookup_unique.csv'):
    try:
        temp = financial_lookup()
        file = pd.read_csv(src)
        for ind,cik in enumerate(file['CIK']):
            temp.download_financials(cik)
            print(file['ticker'][ind],'\tCompleted')
        return True
    except Exception as e:
        print(e)
        return False

def download_all_ticker(src = './SEC_files/CIK_lookup_unique.csv'):
    try:
        #first we got to get the name of all possible tickers
        file = pd.read_csv(src)
        counter = 0
        for ticker in file['ticker']:
            if(counter<UPDATE_LIMIT):
                temp = ticker_file_manager()
                print(ticker,temp.update(ticker=ticker))
                time.sleep(1)
                counter+=1
            else:
                break
    except Exception as e:
        print(e)
        return False
    

def download_ticker(ticker):
    print("Starting Download Ticker")
    try:
        temp = ticker_file_manager()
        print(ticker,temp.update(ticker=ticker))
    except Exception as e:
        print(e)
        return False
    






#for testing purposes
if __name__ == '__main__':
    download_all_financials()