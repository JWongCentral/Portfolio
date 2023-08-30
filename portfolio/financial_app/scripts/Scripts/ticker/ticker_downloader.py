import yfinance as yf
from pandas_datareader import data as pdr
from datetime import date,datetime
from bs4 import BeautifulSoup as BSoup
import requests


#overrides yf to download data in pandas format
yf.pdr_override()


#this will handle downloading and saving files from yahoo finance
#it can be used to save a file in the appropriate folder/area
#as well as just getting it as a dataframe (using pandas) for further exportation
class ticker_downloader():


    def __init__(self,dest='./financial_app/scripts/ticker/data/ticker'):
        self.data = {}      #dict to hold all of the current data
        self.dest = dest
        #dict of dict with the following data
        #self.data = {
        #   ticker_name:{
        #      Data:{data will be stored as df}
        #      request_date:(whatever the last date on the data is)
        #      sector: Computer
        #   }
        # }
        #



    #this will simply download the data of the ticker in question
    #this will also OVERWRITE current ticker information in self.data
    #note:
    #   THIS IS THROTTLED, to only make 1 request per second to avoid
    #   yahoo finance rejecting our request
    def download_data(self,
                      ticker = [],      #should contain list of strings/ticker symbols
                      period = '',      #dates inbetween each entry, 1d, 5d, 1w, etc...
                      start='',         #starting date in format YYYY-MM-DD
                      end = '',         #ending date in format YYYY-MM-DD
                      override = False):#if we need to override the bottleneck

        if len(ticker) == 0 or period == '' or start == '':
            print("Missing information, please include ticker, period, and/or start date as \"2000-01-02\" for january 2nd 2000")
            return False
        
        if end == '':
            end = date.today()
        try:
            #requesting ticker information
            for tick in ticker:
                
                #retrieving info
                ticker_name = tick.lower()
                data = pdr.get_data_yahoo(ticker_name,start=start,end=end, period = period)
                temp =  self.scrape_sector(ticker_name)
                if(temp == None): return False
                sector = temp if temp is not None else "N/A"
                request_date = end

                self.data[ticker_name] = {'data':data,'sector':sector,'request_date':request_date}
                return True

        except Exception as e:
            print ('ticker_Downloader',e)
            return False
        
        return False
    



    #simply exports the file as a CSV
    #returns True if successful, False otherwise
    def save_as_csv(self,
                      ticker = '',        #should contain list of strings/ticker symbols
                      period = '1d',      #dates inbetween each entry, 1d, 5d, 1w, etc...
                      start='2000-01-01', #starting date in format YYYY-MM-DD
                      end = '',):         #ending date in format YYYY-MM-DD
        
        if(ticker == ''): return False

        #download if it does not exist in dataset yet
        tick = ticker.lower()
        if tick not in self.data:
            if self.download_data([ticker],period=period,start=start,end=end) == False:
                return False #error
        
        try:
            
            #creating csv
            df = self.data[tick]['data']
            df.to_csv(self.dest+"/"+tick+".csv", encoding = 'utf-8')

            #appending/updating nav
            file = open(self.dest+"/nav.data", 'r')
            lines = file.readlines()
            file.close()

            #go through each line and see if there is already an entry
            for i,j in enumerate(lines):

                #skip header
                if(i==0): continue

                #if we have found the line to update
                if(j.find(tick) == -1):
                    #add
                    file=open(self.dest+"/nav.data", 'a')
                    file.write(tick + "\t" + str(self.data[tick]['request_date'])+'\n')
                    file.close()
                    return True
                
            #not found therefore we overwrite    
            lines[i] = tick + self.data[tick]['request_date'] + "\n"
            file=open(self.dest+"/nav.data", 'w')
            for i in lines:
                file.write(i)
            file.close()
            
            return True
        
        except Exception as e:
            return False
        return False
    



    #simply exports the file as a dataframe (using pandas)
    def export_as_df(self,
                        ticker = '',        #should contain list of strings/ticker symbols
                        period = '1d',      #dates inbetween each entry, 1d, 5d, 1w, etc...
                        start='2000-01-01', #starting date in format YYYY-MM-DD
                        end = '',):         #ending date in format YYYY-MM-DD
        
        if(ticker==''): return None
        if(end == ''): end = date.today()

        tick = ticker.lower()
        
        #doesn't exist
        if tick not in self.data:
            if not self.download_data([ticker],period=period,start=start,end=end):
                return None #error
        
        #does exist but checking last updated
        else:
            date_temp= self.data[tick]['request_date']
            if(not date_temp == date.today() and
               date_temp < end ):
                self.download_data([ticker],period=period,start=start)
        

        
        return self.data[ticker]['data']

    





    #this is used to webscrape the sector tab in yf to be used in ML prediction later
    def scrape_sector(self,ticker = ""):
        try:

            #BS4 setup
            url = "https://finance.yahoo.com/quote/"+ticker+"/profile?p="+ticker
            headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                    "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
                        }
            result = requests.get(url, headers = headers).text
            soup = BSoup(result,'html.parser')
            
            #parsing thru
            return soup.find('div',class_='asset-profile-container').find('span', class_='Fw(600)').text
        
        except Exception as e:
            return None





    #just removes all current dataset. should be used when done downloading all relevant dataset
    def clear(self):
        self.data = {}
    def close(self):
        self.data = {}

if __name__ == '__main__':
    test = ticker_downloader()
    #test.download_data(ticker = ['NVDA'], period = '1d', start = '2000-01-01')
    test.save_as_csv(ticker = 'NVDA', period = '1d', start = '2000-01-01')