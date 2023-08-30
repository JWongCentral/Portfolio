from django.shortcuts import render
from django.http import HttpResponse,JsonResponse

from .scripts.Scripts.mongodb_connect import *
# Create your views here.
def main(request):
    return render(request,'financial_main.html')

def search(request):
    return

#Simply used for API-Get Request
def request_ticker(request,company_name = ''):
    company_name = company_name.lower()
    payload = get_ticker(company_name)
    if (payload == None):
        return JsonResponse({
        'status_code': 404,
        'error': 'No Data Found'
    })

    return JsonResponse(payload)

#Simply used for API-get Request
def request_financial_yearly(request,company_name = ''):
    payload = get_yearly_financial(company_name)
    if (payload == {}):
        return JsonResponse({
        'status_code': 404,
        'error': 'No Data Found'
    })

    return JsonResponse(payload)


#This will return a dictionary of the company's ticker information
#Returns data as a dict
def get_ticker(company_name):
    
    #Check Value
    if company_name == '':
        return None
    
    #Open and test if we are connected
    open_connection()
    
    #Checks if it needs to be updated
    update_ticker(company_name)

    if not (test_mongodb_server()):
        print('failed mongo db test')
        return None
    ret = get_ticker_from_db(company_name)
    close_connection()

    return ret
    

#Returns data as a dict
def get_yearly_financial(company_name):
    #Check Value
    if company_name == '':
        return None
    
    #Open and test if we are connected
    open_connection()
    if not (test_mongodb_server()):
        print('failed mongo db test')
        return None
    ret = {}
    db = get_client()['SEC']
    for year in db.list_collection_names():
        collection = db[year]
        result = list(collection.find(
            {'ticker':company_name}
            ))
        
        #checks if empty
        if not (result):
            continue
        ret[year] = result[0]

    close_connection()
    return ret


