

import pandas as pd
import os,requests
import time
from datetime import datetime


time_of_last_request = datetime(2000,1,1)
header = {
            'User-agent':'Jack Wong jackbwong1998@gmail.com',
            }
#to update CIK_List file at
#https://www.sec.gov/Archives/edgar/cik-lookup-data.txt
class CIKLookup():
    def __init__(self,src='./SEC_files'):
        self.src = src


    #to be within the standards of SEC requests we can only request information
    #10 times per second
    def throttle_request(self,link):
        global time_of_last_request
        if(datetime.now().microsecond-time_of_last_request.microsecond<100):
            time.sleep(.1)
        time_of_last_request = datetime.now()

        return requests.get(link,headers=header)
    
    #returns raw data as DF
    def get_data(self):
        try:
            response = self.throttle_request('https://www.sec.gov/files/company_tickers.json')
            data = response.json()
            df = pd.DataFrame(data)
            df = df.T
            df['ticker'] = df['ticker'].str.upper()
            df['title'] = df['title'].str.upper()
            return df
        except Exception as e:
            return False
    
    #downloads the updated CIK numbers
    def download(self):
        try:
            df = self.get_data()
            df.to_csv(self.src+'/CIK_lookup.csv')
            return True
        except Exception as e:
            return False

    #returns CIK number for the specific company
    def CIK_lookup(self,company_name = '',ticker=''):
        if len(company_name)+len(ticker) == 0: return None
        try:
            df = pd.read_csv(self.src+'/CIK_lookup.csv',index_col = 0)
            #searching for company name
            if(company_name != ''):
                company_name = company_name.upper()
                val = df.loc[df['title'].str.contains(company_name)==True]
                
                if len(val)==0: return None
                val = val['cik_str'].values[0]
                return val
            #searching via ticker
            elif(ticker!=''):
                ticker = ticker.upper()
                val = df.loc[df['ticker'].str.contains(ticker)==True]
                if len(val)==0: return None
                val = val['cik_str'].values[0]
                return val
            else:
                print("Company name/Ticker needs to have a value")
            return None
            
        except Exception as e:
            print(e)
            return None
        

    #will return a dict of all CIK with associated ticker/company name
    #used for downloading all SEC data on all companies
    def get_all_CIK(self,update=False, saving=False):

        #updating data
        if(update):
            if not (self.download):
                return None

        try:
            ret = {'CIK':[],'ticker':[],'title':[]}
            #since there are duplicates we'll be iterating through it, (and also looking to see if unique file exists)
            df = None
            #path exists so we just return the dict conversion
            if(os.path.exists(self.src+'/CIK_lookup_unique.csv')):
                df = pd.read_csv(self.src+'/CIK_lookup_unique.csv',index_col = 0)
                return df.to_dict('list')
            else:
                df = pd.read_csv(self.src+'/CIK_lookup.csv',index_col = 0)
            counter = 0
            #getting unique entries
            for ind,row in df.iterrows():
                cik = row['cik_str']
                ticker = row['ticker']
                title = row['title']
                if not (cik in ret['CIK']):
                    ret['CIK'].append(cik)
                    ret['ticker'].append(ticker)
                    ret['title'].append(title)
                    
            
            #saving
            if(saving):
                df = pd.DataFrame(ret)
                df.to_csv(self.src+'/CIK_lookup_unique.csv')
            return ret
            
        except Exception as e:
            print(e)
            return None


        
class financial_lookup():
    def __init__(self,):
        self.submissions_link = 'https://data.sec.gov/submissions/CIK##########.json'
        self.company_facts_link = 'https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json'
        self.replace = '##########'
        return
    
    #to be within the standards of SEC requests we can only request information
    #10 times per second
    def throttle_request(self,link):
        global time_of_last_request
        if(datetime.now().microsecond-time_of_last_request.microsecond<100):
            time.sleep(.1)
        time_of_last_request = datetime.now()

        return requests.get(link,headers=header)
    

    #will return the submissions info
    def lookup_submissions(self,cik):
        if(len(str(cik))!=10):
           cik = str(cik).zfill(10)
        ret = self.throttle_request(self.submissions_link.replace(self.replace,cik))
        return ret.json()
    
    def lookup_company_facts(self,cik):
        if(len(str(cik))!=10):
           cik = str(cik).zfill(10)
        ret = self.throttle_request(self.company_facts_link.replace(self.replace,cik))
        return ret.json()['facts']
    
    
    def download_financials(self,cik):
        try:
            if(len(str(cik))!=10):
                cik = str(cik).zfill(10)
            name = self.lookup_submissions(cik)['name']
            ticker = self.lookup_submissions(cik)['tickers'][0]
            data = self.lookup_financials(cik,ticker)
            df = pd.DataFrame(data).fillna(0)
            if(df.empty==True): return None
            df.to_csv('./Sec_files/Ticker/'+ticker+'.csv')
            return df
        except Exception as e:
            print('Download Error')
            print(e)
            return None

    def lookup_financials(self,cik,ticker):
        facts = self.lookup_company_facts(cik)
        
        try:
            data = {}#with the key being the year of filing
            tag = 'us-gaap'
            specialCases = []
            ignore_cases = ['BRK-B','BRK-A','TSM']


            if ticker in ignore_cases: return None

            val = {}
            val['revenue'] = self.financials_revenue(facts[tag])
            val['net_income'] = self.financials_net_income(facts[tag])
            val['eps_diluted'] = self.financials_diluted_shares(facts[tag],(ticker in specialCases))
            val['cash_and_equiv'] = self.financials_cash_and_cash_equivalent(facts[tag])
            val['long_term_debt'] = self.Financials_current_and_long_term_debt(facts[tag])
            val['long_term_assets'] = self.Financials_long_term_assets(facts[tag])
            val['depreication'] = self.Financials_depreciation_and_amortization(facts[tag])
            
            #for i in facts['us-gaap'].keys():
            #    print(i)
            
            fail = 0
            for row in val.keys():
                #if it failed to obtain a VOI we keep track
                if(len(val[row]) == 0):
                    fail+=1
                    if fail >=2:
                        print("Too many failures, scrapping data collection")
                        return None
                
                #for adding the VOI to the dict
                for entry in val[row]:
                    if not (entry in data):
                        data[entry] = {}
                    data[entry][row] = val[row][entry]
                    
            

            #sorting dictionary
            keys = list(data.keys())
            keys.sort()
            ret = {i: data[i] for i in keys}

            return ret
        except Exception as e:
            print(e)
            return None
    
    def financials_revenue(self,data):
        try:
            ret = {}

            tags = ['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax',]
            for tag in tags:
                if(tag in data.keys()):
                    for i in data[tag]['units']['USD']:
                        
                        if i['fp'] != 'FY' :
                            continue
                        
                        val = i['val']
                        year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                        

                        ret[year]=val
                
                    
            return ret
        except Exception as e:
            print("Revenue error")
            print(e)
            return []

    def financials_net_income(self,data):
        try:
            ret = {}

            tags = ['NetIncomeLoss']
            for tag in tags:
                
                for i in data[tag]['units']['USD']:
                    if i['fp'] != 'FY':
                        continue
                    
                    val = i['val']
                    year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                    

                    ret[year]=val
            return ret
        except Exception as e:
            print("Net Income error")
            print(e)
            return []
    
    def financials_diluted_shares(self,data,same=False):
        try:
            ret = {}
            tags = []
            if same==True:
                tags = ['EarningsPerShareBasic']
            else:
                tags = ['EarningsPerShareDiluted']

            
            for tag in tags:
                if(tag in data.keys()):
                    for i in data[tag]['units']['USD/shares']:

                        if i['fp'] != 'FY':
                            continue
                        val = i['val']
                        year = datetime.strptime(str(i['end']),'%Y-%m-%d').year

                        ret[year]=val
            
            
            
            return ret
        except Exception as e:
            print("Diluted Shares error")
            print(e)
            return []
    
    def financials_cash_and_cash_equivalent(self,data):
        try:
            ret = {}

            tags = ['CashAndCashEquivalentsAtCarryingValue']
            for tag in tags:
                if(tag in data.keys()):
                    for i in data[tag]['units']['USD']:
                        if i['fp'] != 'FY':
                            continue
                        val = i['val']
                        year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                        ret[year]=val
            return ret
        except Exception as e:
            print("Cash and Cash equivalent error")
            print(e)
            return []
        
   
    
    def Financials_current_debt(self,data):
        ret = {}
        tags = ['LiabilitiesCurrent']
        for tag in tags:
            if(tag in data.keys()):
                for i in data[tag]['units']['USD']:
                    if i['fp'] != 'FY':
                        continue
                    val = i['val']
                    year = datetime.strptime(str(i['end']),'%Y-%m-%d').year


                    ret[year]=val
        return ret
    
    def Financials_long_term_debt(self,data):
        ret = {}
        tags = ['LongTermDebtNoncurrent', 'LongTermDebt']
        for tag in tags:
            for i in data[tag]['units']['USD']:
                
                if i['fp'] != 'FY':
                    continue
                val = i['val']
                year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                
        
                ret[year]=val

        return ret
    def Financials_current_and_long_term_debt(self,data):
        try:
            temp1 = self.Financials_current_debt(data)
            temp2 = self.Financials_long_term_debt(data)
            ret = {}
            for i in temp1:
                ret[i] = temp1[i]
            for i in temp2:
                ret[i]+=temp2[i]
            
            return ret
        except Exception as e:
            print("Current and long term assets error")
            print(e)
            return []
        
    def Financials_current_assets(self,data):
        ret = {}

        tags = ['AssetsCurrent']
        for tag in tags:
            for i in data[tag]['units']['USD']:
                if i['fp'] != 'FY':
                    continue
                val = i['val']
                year = datetime.strptime(str(i['end']),'%Y-%m-%d').year

                ret[year]=val

        return ret
    
    def Financials_total_assets(self,data):
        ret = {}

        tags = ['Assets']
        for tag in tags:
            for i in data[tag]['units']['USD']:
                if i['fp'] != 'FY':
                    continue
                val = i['val']
                year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                ret[year]=val

        return ret
    
    def Financials_long_term_assets(self,data):
        try:
            current = self.Financials_current_assets(data)
            total = self.Financials_total_assets(data)
            ret = {}
            for i in current:
                ret[i] = total[i]-current[i]
            return ret
        except Exception as e:
            print("Long term ASSETS error")
            print(e)
            return []
            
    
    def Financials_depreciation_and_amortization(self,data):
        try:
            ret = {}

            tags = ['DepreciationDepletionAndAmortization','DepreciationAndAmortization']
            for tag in tags:
                try:
                    for i in data[tag]['units']['USD']:
                        if i['fp'] != 'FY':
                            continue
                        val = i['val']
                        year = datetime.strptime(str(i['end']),'%Y-%m-%d').year
                        
                        ret[year]=val
                except Exception as e:
                    print(e)
                    continue
            return ret
        except Exception as e:
            print("Depreciation error")
            print(e)
        return []

        
    
    


    


#For testing purposes
if __name__ == '__main__':
    test = CIKLookup()
    df = test.get_all_CIK()
    test2 = financial_lookup()
    
    for i in range(len(df['CIK'])):
        cik = df['CIK'][i]
        ticker = df['ticker'][i]
        title = df['title'][i]
        print(cik)
        print(ticker)
        print(title)
        print(test2.download_financials(cik))
        print('-'*20)
        time.sleep(0.1)
        
        

    
    



