#For MongoDB Purposes
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import date, timedelta
from .main import *
import pandas as pd
import os

uri = open('../secret.txt').read()
client = None
DB_STOCK_SIZE = 4

def open_connection():
    global client
    client = MongoClient(uri, server_api=ServerApi('1'))
    test_mongodb_server()

def close_connection():
    global client
    print('Client Closed:',client.close()==None)


def test_mongodb_server():
    # Create a new client and connect to the server
    global client
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(e)
        return False

def get_client():
    global client
    return client

#this will perform the create/update functionality
#The entry will be a dict containing the name of the company AND the year amongst the financial data
#it will then add
def add_entry(entry):
    global client
    db = client['SEC']
    #creating collection if it does not exist
    if not (entry['year'] in db.list_collection_names()):
        db.create_collection(entry['year'])
    
    collection = db[entry['year']]

    #query and check if it exists if not we will add
    query = {'ticker':entry['ticker'], 'year':entry['year']}
    document = collection.find_one(query)

    #exists so we will check if we need to update
    if document:
        for field in entry.keys():
            if (document[field]!=entry[field]):
                collection.update_one(query, {'$set':entry})
                return True
        
    #does not exist so we will add
    else:
        collection.insert_one(entry)
        return True
    


#This will look into the SEC_Financials to look for the ticker.csv
#then it will add each individual entry to the collection
def add_ticker(ticker='',src='./SEC_files/Ticker'):
    
    if not os.path.exists(src+'/'+ticker+'.csv') or ticker=='':
        return False
    
    file = pd.read_csv(src+'/'+ticker.capitalize()+'.csv', index_col=0).to_dict()
    for i in file:
        file[i]['year']=i
        file[i]['ticker']=ticker
        file[i]['_id']= ticker+'-'+i
        add_entry(file[i])
        
    return True

#To delete data
def delete_from_sec_db():
    global client
    db = client['SEC']
    return True

#To update what is currently in our repository
def update_all_financials(src='./SEC_files/Ticker'):
    for i in os.listdir(src):
        add_ticker(ticker=i.replace('.csv',''))
    return True

#This will update the ticker information, if applicable
def update_ticker(ticker):
    ticker = ticker.lower()
    
    found,db = get_db_from_ticker(ticker)

    #Check if its found, if it is updated we exit out since no actions need to be done
    if(found and check_ticker(ticker)==True): return False

    #Not found so we need to create the entry
    download_ticker(ticker)

    if(os.path.exists('./financial_app/scripts/ticker/data/ticker/'+ticker+'.csv')):
        data = pd.read_csv('./financial_app/scripts/ticker/data/ticker/'+ticker+'.csv').to_dict(orient='records')
        if not found:
            db.create_collection(ticker)
        collection = db[ticker]
        collection.insert_many(data)
        return True
    
    else:
        return False
    

#This will return the database with the ticker information
#If there is none then it will return the next available slot
#Returns True/False , DB
#True/False if it is found
#DB = database
def get_db_from_ticker(ticker):
    for i in range(0, DB_STOCK_SIZE):
        db = client['daily_stocks_'+str(i)]
        collect = db.list_collection_names()

        #we have found it
        if ticker in collect:
            return True, db
        
        #we reached end and we need to add more
        elif len(collect) < 500:
            return False, db
        
    return None, None

#Returns ticker information
def get_ticker_from_db(ticker):
    found, db = get_db_from_ticker(ticker)
    ret = None
    if(found):
        collection = db[ticker]
        # Retrieve all ticker data from the collection
        ticker_data = {}
        for document in collection.find():
            date = document['Date']
            open_price = document['Open']
            close_price = document['Close']
            high_price = document['High']
            low_price = document['Low']

            ticker_data[date] = {
                'Open': open_price,
                'Close': close_price,
                'High': high_price,
                'Low': low_price
            }
        ret = ticker_data
    return ret

#This will check if the ticker data is up to date for this particular company
def check_ticker(ticker):
    found,db = get_db_from_ticker(ticker)
    if not found: 
        return None
    today = date.today()-timedelta(days=1)
    collection = db[ticker]
    entries = list(collection.find({'Date':today.strftime('%Y-%m-%d')}))
    if(len(entries) == 0): return False
    return True



#for testing purposes
if __name__ == "__main__":
    print()
    open_connection()
    update_ticker('aapl')
    print(check_ticker('aapl'))
    close_connection()