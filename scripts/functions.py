import datetime,cbpro,yaml,os.path,os
from datetime import datetime,timedelta,timezone
from math import ceil
#function that make some checks about the sense of the dates inserted
def checkDate(firstDate,secondDate):
    if firstDate>=secondDate:
        return"Error: dates not in the right order!"
    if secondDate>datetime.now().timestamp():
        return "Error: date must be before "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return True

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def get_last_update(currency,DATA_PATH):
    currency_filename=currency+".csv"
    currency_path=DATA_PATH+"coinbase/"+currency_filename
    if os.path.isfile(currency_path): 
        f=open(currency_path,"r") #the currency file is opened
        data=f.read()
        f.close()
        for line in data.split("\n"):
            if line!="":
                lastline=line # i overwrite the same variable so that i got only the last line
        #Now that i know the last line ,I can get the last date recorded and start multiple request to fit the hole 
        data_lastline=lastline.split(",")
        lastdate=datetime.fromtimestamp(float(data_lastline[0])).strftime('%Y-%m-%dT%H:%M:%S') # this is the last date recorded in iso 8601
        #print("last recorded was:",lastdate)
    else:
        lastdate="2021-09-01T00:00:00"
    print("last update on:",lastdate)
    return lastdate
def update_currencies_data(DATA_PATH,cbproClient,currencies_string):
    """[summary] each time the program is opened, it loads the new unrecorded data.

    Args:
        DATA_PATH (string): [path to the data recording dir]
    """

    print("updating data to today's values...")
    listOfCurrencies=currencies_string.split(",")
    #for (dirpath, dirnames, filenames) in os.walk("data"):
        #listOfCurrencies += [os.path.join(dirpath, file) for file in filenames] #This is the list of all the currencies you have to update
    for currency in listOfCurrencies:
        print(currency)
        update_currency(currency,DATA_PATH,cbproClient)
def update_currency(currency,DATA_PATH,cbproClient):
    """[summary] function that checks the last record written and starts to make multiple requests 
                 to cover the time passed from that day to the present

    Args:
        currency_filename (string): filename of the currency you have to update
    """
    lastdate=get_last_update(currency,DATA_PATH)
    timezone_offset = 0  # GMT (UTC08:00)
    tzinfo = timezone(timedelta(hours=timezone_offset))
    get_historical_data_coinbase("BTC-USD",start_date=lastdate,end_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),cbproClient=cbproClient)

def write_currency_data(filename,data,DATA_PATH):
    """[summary] function that records data obtained in a csv in order to analyse them later.

    Args:
        filename (string): [string containing the name of the file will be opened]
        data (list of dict): [list of dict containing the following keyword: unix_time,low,high,open,close,volume]
    """
    tmp_path=DATA_PATH+'coinbase/'+filename+'.csv'
    print("PATH",tmp_path)
    if os.path.isfile(tmp_path):
        print("file exists")
        f=open(tmp_path,"a")     
        for candle in data:
            string_data=candle["unix_time"]+","+candle["low"]+","+candle["high"]+","+candle["open"]+","+candle["close"]+","+candle["volume"]+"\n"
            f.write(string_data)
        f.close()   
    else:
        print(filename+".csv not found. Creating it for the first time")
        
        f=open(tmp_path,"w")
        title="Unix time,low,high,open,close,volume"
        f.write(title)
        for candle in data:
            string_data="\n"+candle["unix_time"]+","+candle["low"]+","+candle["high"]+","+candle["open"]+","+candle["close"]+","+candle["volume"]
            f.write(string_data)
        f.close()
    print("Recording data on "+filename+".csv")

def get_clean_cb_request_data(raw,last_unix=None):
    """[summary]
function that organises cb request in a clean dict.
    Args:
        raw (list of candles): [function takes a list of candles generated by
                                'get_product_historic_rates' function]

    Returns:
        [list of dict]: [it returns the same data but organised in a more comprehensive manner]
    """
    candles_list=[]
    for c in raw: #request is made up of candles
        candle={} # creation of a dict to store data efficiently
        candle["unix_time"]=str(c[0])# time is in unix format
        if last_unix==None or (float(candle["unix_time"])>last_unix)  : #check made in order to be sure about recording data only once.
            candle["low"]=str(c[1])
            candle["high"]=str(c[2])
            candle["open"]=str(c[3])
            candle["close"]=str(c[4])
            candle["volume"]=str(c[5])
            #candles_list.append(candle) #incorrect, since this method collect data in the opposite order, creating issues in gathering data in a chronological way.
            candles_list.insert(0,candle)
    return candles_list

def buy_crypto(_amount,cbproClient):
    print(cbproClient.place_market_order(product_id='BTC-USD', side='buy',funds='00.00'))  # place market order (for some reason, the first doesn't work, so you'll better making a fake order with 0 euros
    print(cbproClient.place_market_order(product_id='BTC-USD', side='buy', funds='400.00'))  # place market order

def sell_crypto(_amount,cbproClient):
    print(cbproClient.place_market_order(product_id='BTC-USD', side='sell',funds='00.00'))  # place market order (for some reason, the first doesn't work, so you'll better making a fake order with 0 euros
    print(cbproClient.place_market_order(product_id='BTC-USD', side='sell', funds='400.00'))  # place market order

def get_historical_data_coinbase(currency,start_date,end_date,cbproClient):
    """[summary] function that makes multiple requests in order to fetch all the necessary data
    I choose a granularity of 1 min in order to get the most precise analisys
    start and end time in iso 8601 format

    Args:
        currency (string): [string containing currency to be evalued]
        start_date (string): [start date in iso8601 format]
        end_date (string): [end date in iso8601 format]
    """
    

    #conversion of dates from iso8601 to unix
    hours_offset=2 # indicated in hours
    my_timezone_offset=timedelta(hours=hours_offset)
    utc_dt_start = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
    utc_dt_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
    timestamp_start = (utc_dt_start - datetime(1970, 1, 1)).total_seconds()
    timestamp_end = (utc_dt_end - datetime(1970, 1, 1)).total_seconds()

    #first, calculation of the period to be analysed 
    period=timestamp_end-timestamp_start
    #then, I divide it in subperiods of about 4 hours, so that i can get historical data of 1 day in 6 requests
    #since i can get only 300 candles for request, i can get 300 minutes of records, that means i get 5 hours of data per request
    n_cycle=period/60 # this variable tells me how many candles i need to do in order to cover all the period
    if n_cycle<=300: # i don't need to do multiple requests (maximum is 300 candles for request)
        print("start",start_date,"end",end_date, "<300 candles","n cycle",n_cycle)
        start_date_datetime_obj=datetime.strptime(start_date,'%Y-%m-%dT%H:%M:%S')
        start_date_unix= (start_date_datetime_obj-timedelta(hours=2) - datetime(1970, 1, 1)).total_seconds()
        start_date_with_offset=start_date_datetime_obj-timedelta(hours=2)
        start_date_string=start_date_with_offset.strftime('%Y-%m-%dT%H:%M:%S')
        raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=start_date_string,end=end_date,granularity=60)
        print("raw",raw_data)
        cb_request=get_clean_cb_request_data(raw_data,start_date_unix)
        write_currency_data(currency,cb_request,os.getcwd()+"/data/")
        print("#######################")
    else:
        print("number of requests in order to cover all the period:",n_cycle/300)# in this way i discover how many requests I have to do
        for i in range(ceil(n_cycle/300)):
            temp_start=(utc_dt_start+timedelta(hours=i*5)-timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            temp_end=(utc_dt_start+timedelta(hours=(i+1)*5)-timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

            print("cycle n.",i)
            #TODO: correct this if statement( you need to convert to float number or find a way to compare date in utc form)
            if (utc_dt_start+timedelta(hours=(i+1)*5)) > utc_dt_end: # essentially, the right limit of the last subperiod can exceed our 'end date', recording useless data
                print("from:",temp_start,"to:",end_date)
                raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=temp_start,end=end_date,granularity=60)
                print("raw1",raw_data)
                cb_request=get_clean_cb_request_data(raw_data)
                write_currency_data(currency,cb_request,os.getcwd()+"/data/")
            else:
                print("from:",temp_start,"to:",temp_end)
                #print(cbpro_client_sand.get_product_historic_rates('BTC-USD',start=temp_start,end=temp_end,granularity=60))
                raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=temp_start,end=temp_end,granularity=60) #creation of a temp variable where data is stored before being cleaned and organised
                print("raw2",raw_data)
                cb_request=get_clean_cb_request_data(raw_data)
                write_currency_data(currency,cb_request,os.getcwd()+"/data/")
            print()
