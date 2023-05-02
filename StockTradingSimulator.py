#Originally designed to work in AWS Cloud9
#This program will obtain lifetime stock price data via apha vantage api for any selected stocks
#The data will then be written into csv files on local machine/environment
#Program will check for new data if ran after original gathering date
#3 Strategies; Mean reversion, Simple Moving Average, and Bollinger Bands will be performed on the data for each stock.
#Profit, returns, and best performing strategies are tracked. 
#Results are then output in json format. 
#NOTE: If wanting to analyze more than 10 different stocks, program will need modified to avoid rate limiting. 
#None of this is or should be considered financial advice. I am not a financial advisor and the program is simply an analysis/simulation tool. 


import json
import requests 
import time 

request_counter = 0 #used to count the number of requests so I dont get rate limited
append_counter = 0 #used to count requests for appending function to avoid rate limiting
def first_get_data():# Defines function to get data first
    request_counter = 0 #used to count the number of requests so I dont get rate limited
    tickers = ["AAPL" , "ADBE" , "ATVI" , "COIN" , "GM" , "GOOG" , "MSFT",  "PARA" , "PFE" , "TSLA"] #Replace with desired ticker(s)
    ticker = '' #sets ticker to an empty string value
    for ticker in tickers:
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+ticker+"&apikey=JRZEJSHUUVG1FPAH&outputsize=full&datatype=json&start_date=2022-04-11&end_date=2023-04-11" #api url
        
        time_key ="Time Series (Daily)" #used to tell what key to use
        close_key = "5. adjusted close" #same as above
        request = requests.get(url) #requests the api call
        
        stock_dct = json.loads(request.text) #creates a dictionary
        
        file = open("/home/ubuntu/environment/FinalProject/"+ticker+".csv", "w") #creates a file to store data
        
        lines = [] #creates a list
        
        for date_key in stock_dct[time_key]: #filters through prices
            #print(date_key)
            #print(stock_dct[time_key][date_key][close_key])
            #file.write(date_key + "," + stock_dct[time_key][date_key][close_key] + "\n")
            lines.append(date_key + "," + stock_dct[time_key][date_key][close_key] + "\n")
            
        
        lines.reverse() #reverses the list to make the timing right
        file.writelines(lines)
        request_counter += 1    #adds to requrst counter   
        file.close()
        
        if request_counter == 4: #sleeps program to avoid rate limiting
            time.sleep(62)
        
        elif request_counter == 8: #sleeps program again to avoid rate limiting
            time.sleep(62)
        
        else:
            pass
    
def append_data(): #defines function to append or add new data
    append_counter = 0 #used to count requests for appending function to avoid rate limiting
    tickers = ["AAPL" , "ADBE" , "ATVI" , "COIN" , "GM" , "GOOG" , "MSFT" , "PARA" , "PFE" , "TSLA"]
    ticker = "" #empty string ticker
    for ticker in tickers:
        last_date = open("/home/ubuntu/environment/FinalProject/"+ticker+".csv").readlines()[-1].split(",")[0] #sets the last date of data available
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+ticker+"&apikey=JRZEJSHUUVG1FPAH"
        
        time_key ="Time Series (Daily)" #time key for dictionary
        close_key = "5. adjusted close" #key for dictionary
        request = requests.get(url) #makes request
        
        stock_dct = json.loads(request.text) #requests json as dict

        file = open("/home/ubuntu/environment/FinalProject/"+ticker+".csv", "a") #opens file for appending
        
        lines = [] #Creates an empty list to store prices
      
        for date_key in stock_dct[time_key]: #evaluates if new data is available 
            if date_key > last_date: #adds new data if it is available
                lines.append(date_key + "," + stock_dct[time_key][date_key][close_key] + "\n") #Adds prices to list
          
        lines.reverse() #Reverses list to make analysis/appends work
        file.writelines(lines)  
        file.close()
        append_counter += 1 #adds to keep track of requests 
        
        if append_counter == 4: #sleeps program to avoid rate limiting
            time.sleep(62)
        
        elif append_counter == 8: #sleeps program to avoid rate limiting
            time.sleep(62)
        
        else:
            pass



def mean_reversion_strategy(prices): #Creates Mean reversion function
     #sets variables = to 0
    i = 0 # represents days/price on a day
    buy = 0 # sets to 0 to represent if holding stock
    bp = 0 # keeps track of profits
    short = 0 #represents short variable
    total_profit = 0.0
    for price in prices:
        if i >= 5: #Begins moving average calculations
            avg = ((prices[i-1] + prices[i-2] + prices[i-3] + prices[i-4] + prices[i-5]) / 5) #calculates average
            
            if price < avg * .96 and buy == 0: #evaluates if price is below moving average
                print("buy at: ", price) 
                buy = 1 # represents stock being held
                bp = price # used for profit calculation
                if short != 0 and buy != 0: #tests to see if we are shorting
                    total_profit += short - price #updates total profuit
                    short = 0 #Updates to no longer be shorting
                    
                if i == (len(prices) - 1): #Tells you to buy stock if buy signal is detected today.
                    print("Buy this today!")
                    
            elif price > avg * 1.04 and buy != 0: #Evaluates if stock is held and price is above moving avg
                print("sell at: ", price)
                total_profit+= price - bp # Performs profit tracking arithmetic
                buy = 0 # tells program stock is no longer held
                if short != 0 and buy != 0:
                    short = price
                if i == (len(prices) - 1): #Tells you to sell stock if sell signal is detected today.
                    print("Sell this today!")
                    
            else: #Passes if no previous conditions are met
                pass
        i += 1 #moves onto the next day/price
    mr_returns = total_profit / prices[0] #calculates returns
    
    return total_profit, mr_returns # tells function what to return




def simple_moving_average(prices): #Creates SMA function
    sma_profit = 0.0 #Sets variables = 0
    i = 0 # represents day/price on day
    buy = 0 # used to tell if stock is currently held
    bp = 0 # used for profit calculation arithmetic
    short = 0
    for price in prices:
        if i > 5: #Begins avg calculation
            avg = ((prices[i-1] + prices[i-2] + prices[i-3] + prices[i-4] + prices[i-5]) / 5) # calculates moving average
            
            if price > avg and buy == 0: #Evaluates if price is above avg
                print("buy at: ", price)
                buy = 1 # tells program stock is currently held
                bp = price # used for profit arithmetic
                if short != 0 and buy != 0:
                    sma_profit += short - price
                
                if i == (len(prices) - 1): #Tells you to buy signal if buy dignal is detected today
                    print("Buy this today!")
                
            elif price < avg and buy != 0: #Evaluates if price is below avg and stock is held
                print("sell at: ", price)
                sma_profit += price - bp # performs profit arithmetic
                buy = 0 # tells program stock is no longer held
                
                if buy != 0 and short != 0:
                    short = price
                    
                if i == (len(prices) - 1): #Tells you to sell stock if sell signal is detected on the last day
                    print("Sell this today!")
            else:
                pass
        
        i += 1 # moves onto the next price/day
        
    sma_returns = sma_profit / prices[0] #Calcualtes SMA returns
    
    return sma_profit, sma_returns # tells function what to return
    
def bollinger_bands(prices): #Creates SMA function
    bol_profit = 0.0 #Sets variables = 0
    i = 0 # represents day/price on day
    buy = 0 # used to tell if stock is currently held
    bp = 0 # used for profit calculation arithmetic
    for price in prices:
        if i > 5: #Begins avg calculation
            avg = ((prices[i-1] + prices[i-2] + prices[i-3] + prices[i-4] + prices[i-5]) / 5) # calculates moving average
            
            if price * 1.05 > avg and buy == 0: #Evaluates if price is above avg
                print("buy at: ", price)
                buy = 1 # tells program stock is currently held
                bp = price # used for profit arithmetic
                
                if i == (len(prices) - 1): #tells you to buy stock if buy signal is detected today
                    print("Buy this today!")
                
            elif price * 0.95 < avg and buy != 0: #Evaluates if price is below avg and stock is held
                print("sell at: ", price)
                bol_profit += price - bp # performs profit arithmetic
                buy = 0 # tells program stock is no longer held
               
                if i == (len(prices) - 1): #Tells you to sell stock if sell signal is detected today
                    print("Sell this today!")
               
            else:
                pass
        
        i += 1 # moves onto the next price/day
        
    bol_returns = bol_profit / prices[0] #Calcualtes SMA returns
    
    return bol_profit, bol_returns
    
def save_results(dictionary): # Creates a json sump function
    json.dump(results, open("/home/ubuntu/environment/FinalProject/results.json", "w"), indent=4) # dumps results to a json
    
    
    
    
tickers = ["AAPL" , "ADBE" , "ATVI" , "COIN" , "GM" , "GOOG" , "MSFT" , "PARA" , "PFE" , "TSLA"] # list of stock tickers
results = {} # Creates a list for the tickers and a resutlts ditctionary
highest_returns = 0 #sets variables to track best strategies and whatnot to 0
highest_ticker_num = 0
highest_ticker = ""
best_strategy = ""


first_get_data() #calls first get data
time.sleep(62) #Sleeps program after first get data in order to prevent rate limiting.
append_data() #calls append data function.

for ticker in tickers: # Loops through tickers and opens files
    f = open("/home/ubuntu/environment/FinalProject/" + ticker + ".csv" , "r") # opens file
    lines = f.readlines() # reads file

    prices = []
    for line in lines:
        data = line.strip().split(',') # split the line by comma and remove newline character
        price = float(data[1]) # turns price into a float for annalysis
        prices.append(price) #appends prices with the individual prices

    
    results[ticker + "_prices"] = prices #saves results to dictionary

    
        
    simple_moving_average(prices) # calls sma fnction
    sma_profit, sma_returns = simple_moving_average(prices) 
    results[ticker + "_sma_profit"] = sma_profit # adds results of function to dictionary for json output
    results[ticker + "_sma_returns"] = sma_returns # same as above
    if highest_returns < sma_returns: #used to determine most profitable ticker, strategy, and amount.
        highest_returns = sma_returns
        highest_ticker = ticker
        best_strategy = "sma"
        
    
       
    mean_reversion_strategy(prices) # calls mean reversion function
    total_profit, mr_returns = mean_reversion_strategy(prices)
    results[ticker + "_total_profit"] = total_profit # adds results of function to dictionary for json output
    results[ticker+ "_mr_returns"] = mr_returns # same as aobove
    if highest_returns < mr_returns: #used to determine most profitable ticker, strategy, and amount
        highest_returns = mr_returns
        highest_ticker = ticker
        best_strategy = "mr"
    
        
    bollinger_bands(prices) #calls bollinger bands function
    bol_profit, bol_returns = bollinger_bands(prices)
    results[ticker + "_bol_profit"] = bol_profit #adds results of strategy to dictionary
    results[ticker + "_bol_returns"] = bol_returns #same as above
    if highest_returns < bol_returns: #used to determine most profitable ticker, strategy, and amount
        highest_returns = bol_returns
        highest_ticker = ticker
        best_strategy = "bol"
    
    
  
save_results(results) # calls json save function 
print("Best Returns:", highest_returns)
print("Best Performing Ticker:", highest_ticker)
print("Best Perfomring Strategy:", best_strategy)

results["highest_returns"] = highest_returns #saves highest returns to returns dictionary
results["highest_ticker"] = highest_returns #saves best performing ticker to returns dictionary
results["best_strategy"] = best_strategy #saves best performing strategy to returns dictionary

input("pause") #Keeps program from encountering pain is dead error on AWS
