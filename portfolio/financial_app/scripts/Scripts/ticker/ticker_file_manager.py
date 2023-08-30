from .ticker_file import ticker_info
from .ticker_downloader import ticker_downloader
import os
import pandas as pd

class ticker_file_manager():

    def __init__(self,src = './ticker', dest_data = './ticker/data/ticker'):
        
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
        
    
    



    



if __name__ == '__main__':
    test = ticker_file_manager()
    print ("")
