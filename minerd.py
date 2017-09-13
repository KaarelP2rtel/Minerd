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
bot = colored("[BOT] ", "green")
botr = colored("[BOT] ", "red")
botl = "[BOT]"
api = colored("[API] ", "yellow")
apir = colored("[API] ", "red")
apil = "[API]"


class Data():
    orderID = ""
    history = []
    slidingTarget = []
    currentSum = 0
    maximumSum = 0

data = Data()


def log(a):
    print a
    data.history.append((str(time.strftime('%D  %H:%M:%S')+"   "+a[5:10]+" "+a[15:])))


def avg(a):
    summ=0
    count=0
    for i in a:
        summ+=float(i)
        count+=1
    return summ/count

    
def targetPrice():
    while True:
        try:
            ordersApi = requests.get("https://api.nicehash.com/api?method=orders.get&location=0&algo=24")
            orders = ordersApi.json()["result"]["orders"]
            prices = []
            num = 0
            for order in orders:
                if order["alive"] and order["workers"] != 0:
                    prices.append(order["price"])
                    num += 1
            target=prices[int(0.95*num)]
            data.slidingTarget.append(target)
            if (len(data.slidingTarget) >= 60):
                data.slidingTarget.remove(data.slidingTarget[0])
            average=avg(data.slidingTarget)
            if target>average:
                return average
            else:
                return target
                
            
        except:
            log(apir+"Failed to get Target Price. Trying again")
            time.sleep(5)


def maxPrice():
        while True:
            try:
                api = requests.get("http://whattomine.com/coins.json")
                priceData = api.json()
                mHashR = float(priceData['coins']["Zcash"]["nethash"])/1000000
                xRate = float(priceData['coins']["Zcash"]["exchange_rate"])
                return(576*(1/mHashR)*10*xRate)
            except:
                log(apir+"Failed to get Max Price. Trying again")
                time.sleep(5)


def currentPrice():
    while True:
        try:
            myApi = requests.get("https://api.nicehash.com/api?method=orders.get&my&id="+apiID+"&key="+apiKey+"&location=0&algo=24")
            data.orderID = myApi.json()["result"]["orders"][0]["id"]
            return(myApi.json()["result"]["orders"][0]["price"])
        except:
            log(apir+"Failed to get Current Price. Trying again")
            time.sleep(5)


def lowerPrice():
    while True:
        try:
            decrease = requests.get("https://api.nicehash.com/api?method=orders.set.price.decrease&id="+apiID+"&key="+apiKey+"&location=0&algo=24&order="+str(data.orderID))
            try:
                lamp = decrease.json()["result"]["success"]
                ret = "success"
            except:
                ret = decrease.json()["result"]["error"]
            return ret
        except:
            log(apir+"Failed to Lower Price. Trying again")
            time.sleep(5)


def setPrice(inp):
    while True:
        try:
            setPrice = requests.get("https://api.nicehash.com/api?method=orders.set.price&id="+apiID+"&key="+apiKey+"&location=0&algo=24&order="+str(data.orderID)+"&price="+str(inp)).json()
            try:
                lamp = setPrice["result"]
                ret = "Sucess"
            except:
                ret = setPrice["result"]["error"]
            return ret
        except:
            log(apir+"Failed to Set Price. Trying again")
            time.sleep(5)


def rund(inp):
    return float(str(inp)[:6])


def connected():
    try:
        requests.get("http://www.google.ee/")
        return True
    except:
        return False


def main():
    while True:
        if connected():
            target = float(targetPrice())
            current = float(currentPrice())
            maxp = float(rund(maxPrice()))
            data.currentSum += current
            data.maximumSum += maxp
            ratio = rund(data.currentSum/data.maximumSum)
            con = "Current: "+str(current)+" Target: "+str(target)+" Max: "+str(maxp)+" Ratio: "+str(ratio)
            log(bot+con)
            if maxp < target:
                log(bot+"Setting target to "+str(maxp))
                target = maxp
            if target > current:
                log(bot+"Setting price to "+str(target))
                a = str(api+str(setPrice(target)))
                log(a)
            elif target < current:
                log(bot+"Lowering Price")
                a = str(api+str(lowerPrice()))
                log(a)
            else:
                log(bot+"Getting tea")
            time.sleep(60)
        else:
            log(botr+"No connection trying again in 30 seconds")
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
    ret = ""
    if botThread.isAlive():
        ret += "Olen elus :D"
    else:
        ret += "Olen surnud D:"
    ret += "<ul>"
    for i in data.history:
        ret += "<li>"+i+"</li>"
    ret += "</ul>"
    return ret


if __name__ == "__main__":
    print("Starting bot")
    botThread = threading.Thread(target=main)
    botThread.start()
    print("Bot started")
    print("Starting web server")
    threading.Thread(target=app.run, args=("0.0.0.0", 80)).start()
    print("Web server started")
