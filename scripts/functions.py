import datetime,cbpro,yaml,os.path,os,pytz
import pandas as pd
from datetime import date, datetime,timedelta,timezone
from math import ceil


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
GENERAL_PATH=os.getcwd()
config_dict=read_yaml(GENERAL_PATH+"/config.yaml")
DATA_PATH= config_dict["PATH"]["DATA_PATH"]
DATETIME_FORMAT=config_dict["CONFIG"]["datetime"]

#function that make some checks about the sense of the dates inserted
def checkDate(firstDate,secondDate):
    if firstDate>=secondDate:
        return"Error: dates not in the right order!"
    if secondDate>datetime.now().timestamp():
        return "Error: date must be before "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return True
def new_get_last_update(currency,DATA_PATH):
    currency_path=DATA_PATH+"coinbase/"+currency
    sorted_files=sorted(os.listdir(currency_path),reverse=True) #sorting files from the newer to older
    if len(os.listdir(currency_path))!=0: #checks if there is some data by checking if the dir is empty or not,
        last_date_file=DATA_PATH+"coinbase/"+currency+"/"+sorted_files[0]
        f=open (last_date_file,"r")
        last_line=f.readlines()[-1] # pick the last line
        f.close()
        last_datetime=last_line.split(",")[0]#here i split the last line and pick the first element
        last_datetime_string=datetime.fromtimestamp(float(last_datetime)).strftime('%Y-%m-%dT%H:%M:%S')
    else:
        last_datetime_string="2021-09-01T00:00:00"

    #last_datetime_string=datetime.fromtimestamp(float(last_datetime)).strftime('%Y-%m-%dT%H:%M:%S')
    print("last update on",last_datetime_string)
    return last_datetime_string
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
    lastdate=new_get_last_update(currency,DATA_PATH)
    #new_get_last_update(currency,DATA_PATH)
    timezone_offset = 0  # GMT (UTC08:00)
    tzinfo = timezone(timedelta(hours=timezone_offset))
    get_historical_data_coinbase("BTC-USD",start_date=lastdate,end_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),cbproClient=cbproClient)

def new_write_currency_data(date,filename,data,DATA_PATH):
    """[summary] function that records data obtained in a csv in order to analyse them later.

    Args:
        filename (string): [string containing the name of the file will be opened]
        data (list of dict): [list of dict containing the following keyword: unix_time,low,high,open,close,volume]
    """
    tmp_path=DATA_PATH+'coinbase/'+filename+"/"+date+'.csv'
    #print("PATH",tmp_path)
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

def write_currency_data(filename,data,DATA_PATH):
    """[summary] function that records data obtained in a csv in order to analyse them later.

    Args:
        filename (string): [string containing the name of the file will be opened]
        data (list of dict): [list of dict containing the following keyword: unix_time,low,high,open,close,volume]
    """
    tmp_path=DATA_PATH+'coinbase/'+filename+'.csv'
    #print("PATH",tmp_path)
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
        success=False
        try: #check if data is correct or if we have something odd.
            float(c[0])
            success=True
        except:
            print("ERROR: you passed this instead of a set of values!",c)
        candle={} # creation of a dict to store data efficiently
        candle["unix_time"]=str(c[0])# time is in unix format
        if success==True and (last_unix==None or (float(candle["unix_time"])>last_unix)) : #check made in order to be sure about recording data only once.
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
def unpack_data(data):
    """[summary]
    This function takes the cleaned data and organised them in pocket. Each pocket represent a day. In this way, accessing data is faster.
    strategy:
    1 check the date for each element
    2 if date doens't change, we add the element to the same dict['date']=values
    3 else, we create another dict and append the last one.
    
    Args:
        data (list): data cleaned by 'get_clean_cb_request_data' function

    Returns:
        unpacked_data (list of dict) : [description]
    """    
    #print("this is our data",data)
    unpacked_data=[]
    first_day=data[0]
    curr_day=datetime.fromtimestamp(float(first_day['unix_time'])).strftime('%Y-%m-%d')
    dict_el={}
    data_about_day=[]
    for element in data:
        day=datetime.fromtimestamp(float(element['unix_time'])).strftime('%Y-%m-%d')
        if day==curr_day:
            data_about_day.append(element)
        else:
            #print("date changed")
            dict_el[curr_day]=data_about_day #add to dict the last element of previous day
            unpacked_data.append(dict_el)
            dict_el={} # reset dict
            curr_day=day
            data_about_day=[] # reset data about new day with the first element
            data_about_day.append(element)
    dict_el[curr_day]=data_about_day
    unpacked_data.append(dict_el)# adding the last date, since the last cycle can't be added due to the logic of the above 'for' cycle
    #print("unpacked",unpacked_data)
        
    return unpacked_data

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
    utc_dt_start = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
    utc_dt_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
    print("start",start_date,"end",end_date)
    timestamp_start = (utc_dt_start - datetime(1970, 1, 1)).total_seconds()
    timestamp_end = (utc_dt_end - datetime(1970, 1, 1)).total_seconds()

    #since sometimes it doesn't retreive all data, I chose to make a request with some extra data that i won't consider, just to get what I need.
    start_date_with_offset=datetime.strptime(start_date,'%Y-%m-%dT%H:%M:%S') -timedelta(hours=2)
    end_date_with_offset=datetime.strptime(end_date,'%Y-%m-%dT%H:%M:%S') -timedelta(hours=2)
    #end_date_with_offset_string=end_date_with_offset.strftime('%Y-%m-%dT%H:%M:%S')
    #osservazione: con il 'timedelta(hours=2)' non ti funziona su lunghi periodi, senza non ti funziona sui corti
    start_date_unix= (start_date_with_offset-timedelta(hours=2) - datetime(1970, 1, 1)).total_seconds() # here i remove the timezone offset
    start_date_with_offset_unix=(start_date_with_offset- datetime(1970, 1, 1)).total_seconds() # here i convert the new start date in unix
    
    #first, calculation of the period to be analysed 
    period=timestamp_end-timestamp_start
    #then, I divide it in subperiods of about 4 hours, so that i can get historical data of 1 day in 6 requests
    #since i can get only 300 candles for request, i can get 300 minutes of records, that means i get 5 hours of data per request
    n_cycle=period/60 # this variable tells me how many candles i need to do in order to cover all the period
    if n_cycle<=300: # i don't need to do multiple requests (maximum is 300 candles for request)
        #print("timestamps:",timestamp_end,timestamp_start)
        print("start",start_date,"end",end_date, "<300 candles","n cycle",n_cycle,period)
        start_date_string=start_date_with_offset.strftime('%Y-%m-%dT%H:%M:%S')
        end_date_with_offset_string=end_date_with_offset.strftime('%Y-%m-%dT%H:%M:%S')
        raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=start_date_string,end=end_date_with_offset_string,granularity=60)
        #print("raw",raw_data)
        cb_request=get_clean_cb_request_data(raw_data,start_date_unix)
        print("result of my request",cb_request,"lastdate",start_date_string,"len request",len(cb_request))
        first_date=datetime.fromtimestamp(float(cb_request[-1]["unix_time"])).strftime('%Y-%m-%dT%H:%M:%S')
        print(first_date==start_date,first_date)
        if first_date==start_date:
            print("already up to date!")
        else:
            cb_request.pop(0)# here i remove the first element to prevent on duplicates during recording
            div_data=unpack_data(cb_request)
            for _dict in div_data:
                keys=list(_dict.keys())
                new_write_currency_data(keys[0],currency,_dict[keys[0]],os.getcwd()+"/data/")
        print("#######################")
    else:
        print("number of requests in order to cover all the period:",n_cycle/300)# in this way i discover how many requests I have to do
        for i in range(ceil(n_cycle/300)):
            temp_start=(start_date_with_offset+timedelta(hours=i*5)).strftime('%Y-%m-%d %H:%M:%S')
            temp_end=(utc_dt_start+timedelta(hours=(i+1)*5)-timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

            print("cycle n.",i)
            #TODO: correct this if statement( you need to convert to float number or find a way to compare date in utc form)
            if (utc_dt_start+timedelta(hours=(i+1)*5)) > utc_dt_end: # essentially, the right limit of the last subperiod can exceed our 'end date', recording useless data
                print("from:",temp_start,"to:",end_date)
                raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=temp_start,end=end_date_with_offset,granularity=60)
              #  print("raw1",raw_data)
                cb_request=get_clean_cb_request_data(raw_data)
                div_data=unpack_data(cb_request)
                for _dict in div_data:
                    keys=list(_dict.keys())
                   # print(keys[0])
                    new_write_currency_data(keys[0],currency,_dict[keys[0]],os.getcwd()+"/data/")
                #write_currency_data(currency,cb_request,os.getcwd()+"/data/")
            else:
                print("from:",temp_start,"to:",temp_end)
                #print(cbpro_client_sand.get_product_historic_rates('BTC-USD',start=temp_start,end=temp_end,granularity=60))
                raw_data=cbproClient.get_product_historic_rates('BTC-USD',start=temp_start,end=temp_end,granularity=60) #creation of a temp variable where data is stored before being cleaned and organised
               # print("raw2",raw_data)
                cb_request=get_clean_cb_request_data(raw_data)
                div_data=unpack_data(cb_request)
                for _dict in div_data:
                    keys=list(_dict.keys())
                   # print(keys[0])
                    new_write_currency_data(keys[0],currency,_dict[keys[0]],os.getcwd()+"/data/")
                #write_currency_data(currency,cb_request,os.getcwd()+"/data/")
            print()

def get_data_graph(start_date,end_date,marketplace=None,coin=None):
    print("parameters used for backtesting analysis:")
    print("from:",start_date,"to:",end_date)
    print("marketplace:",marketplace,"coin:",coin)
    unix_time_start=float(start_date.timestamp())
    unix_time_end=float(end_date.timestamp())
    #print("dates in unix format",unix_time_start,unix_time_end)
    filename=DATA_PATH+marketplace+"/"+coin+".csv"
    if  not os.path.isfile(filename):
        print( "il file non esiste!")
        return " "
    f=open(filename,"r")
    data=[]
    f.readline() # skip the first line with titles
    raw=f.read().split("\n")
    f.close()
    for line in raw:
        if line!="":
            stick={} # dict containing all data about one particular moment
            parameters=line.split(",")
            stick["unix_time"]=parameters[0]
            if unix_time_start<=float(stick["unix_time"])<=unix_time_end: #passing only stick in the period required
                stick["string_time"]=datetime.fromtimestamp(float(parameters[0])).strftime('%Y-%m-%dT%H:%M:%S')
                stick["low"]=float(parameters[1])
                stick["high"]=float(parameters[2])
                stick["open"]=float(parameters[3])
                stick["close"]=float(parameters[4])
                stick["volume"]=float(parameters[5])
                data.append(stick)
            elif float(stick["unix_time"])>unix_time_end:
                break
            #print(datetime.fromtimestamp(float(unix_time)).strftime('%Y-%m-%dT%H:%M:%S'))
            data_dt=pd.DataFrame(data)
    return data_dt
def new_get_data_graph(start_date,end_date,marketplace=None,coin=None):
    #strategy
    #get the day of the first date
    #get the date of the last date
    #for cycle that opens all the file between them (check also if it's within the same one)
    #read and save all the date between them
    start_date_string=start_date.strftime('%Y-%m-%d')+".csv"
    end_date_string=end_date.strftime('%Y-%m-%d')+".csv"
    unix_time_start=float(start_date.timestamp())
    unix_time_end=float(end_date.timestamp())
    currency_path=DATA_PATH+marketplace+"/"+coin
    sorted_files=sorted(os.listdir(currency_path))
    filtered_files=[]
    for date_file in sorted_files:
        if start_date_string<=date_file<=end_date_string: # check which files belong to the range that will be analysed.
            filtered_files.append(date_file)
    print("to be checked:",filtered_files) #these are the files that you will read (see how in the old function)
    data=[]
    for file in filtered_files: # now I take all the data between the two limit, checking all the filtered file
        complete_file_path=DATA_PATH+marketplace+"/"+coin+"/"+file
        f=open(complete_file_path,"r")
        f.readline() # skip the first line with titles
        raw=f.read().split("\n")
        f.close()
        for line in raw:
            if line!="":
                stick={} # dict containing all data about one particular moment
                parameters=line.split(",")
                stick["unix_time"]=parameters[0]
                if unix_time_start<=float(stick["unix_time"])<=unix_time_end: #passing only stick in the period required
                    stick["string_time"]=datetime.fromtimestamp(float(parameters[0])).strftime('%Y/%m/%d %H:%M')
                    stick["low"]=float(parameters[1])
                    stick["high"]=float(parameters[2])
                    stick["open"]=float(parameters[3])
                    stick["close"]=float(parameters[4])
                    stick["volume"]=float(parameters[5])
                    data.append(stick)
                elif float(stick["unix_time"])>unix_time_end: # if I overlap the upper limit, break the loop and go on.
                    break
    #print("all data needed:",data)
    #print("number of stick:",len(data))
    data_dt=pd.DataFrame(data)
    #print(data_dt)
    return data_dt
