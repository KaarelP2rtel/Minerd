from flask import Flask, render_template, request, Response
import requests
import threading
import time
from termcolor import colored



app = Flask(__name__)
file = open("conf", "r")
apiID = file.readline()[:-1]
apiKey = file.readline()[:-1]
file.close()
orderID=""
bot=colored("[BOT] ","green")
botr=colored("[BOT] ","red")
api=colored("[API] ","yellow")
class Data():
    orderID=""
data=Data()
def targetPrice():
	ordersApi=requests.get("https://api.nicehash.com/api?method=orders.get&location=0&algo=24")
	orders=ordersApi.json()["result"]["orders"]
	prices=[]
	num=0
	for order in orders:
		if order["alive"] and order["workers"]!=0:	
			prices.append(order["price"])
			num+=1
	return(prices[int(0.95*num)])
def maxPrice():
    api = requests.get("http://whattomine.com/coins.json")
    priceData = api.json()
    mHashR = float(priceData['coins']["Zcash"]["nethash"])/1000000
    xRate = float(priceData['coins']["Zcash"]["exchange_rate"])
    return(576*(1/mHashR)*10*xRate)
def currentPrice():
    myApi=requests.get("https://api.nicehash.com/api?method=orders.get&my&id="+apiID+"&key="+apiKey+"&location=0&algo=24")
    data.orderID=myApi.json()["result"]["orders"][0]["id"]
    return(myApi.json()["result"]["orders"][0]["price"])	
def lowerPrice():
    decrease=requests.get("https://api.nicehash.com/api?method=orders.set.price.decrease&id="+apiID+"&key="+apiKey+"&location=0&algo=24&order="+str(data.orderID))
    try:
        lamp=decrease.json()["result"]["success"]
        ret="success"
    except:
        ret=decrease.json()["result"]["error"]
	return ret
def setPrice(inp):
    setPrice=requests.get("https://api.nicehash.com/api?method=orders.set.price&id="+apiID+"&key="+apiKey+"&location=0&algo=24&order="+str(data.orderID)+"&price="+str(inp)).json()
    try:
        lamp=setPrice["result"]
        ret="Sucess"
    except:
        ret=setPrice["result"]["error"]
	return ret

def rund(inp):
    return float(str(inp)[:6])
def connected():
    try:
        requests.get("http://www.neti.ee/")
        return True
    except:
        return False        

def main():    
    while True:
        if connected():
            target=float(targetPrice())
            current=float(currentPrice())
            maxp=float(rund(maxPrice()))
            con="Current: "+str(current)+" Target: "+str(target)+" Max: "+str(maxp)
            print(bot+con)
            if maxp<target:
                print(bot+"Setting target to "+str(maxp))
                target=maxp
            if target>current:
                print(bot+"Setting price to "+str(target))
                print(api+str(setPrice(target)))
            elif target < current:
                print(bot+"Lowering Price")
                print(api+str(lowerPrice()))
            else:
                print(bot+"Getting tea")
            time.sleep(60)
        else:
            print(botr+"No connection trying again in 30 seconds")
            time.sleep(30)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'    

@app.route("/", methods=["GET"])
def hello():
    return "Hello"
	
	
	
if __name__ == "__main__":
    print("Starting web server")
    #threading.Thread(target=app.run, args=("0.0.0.0",80)).start()
    print("Web server started")
    print("Starting bot")
    threading.Thread(target=main).start()
    print("Bot started")
