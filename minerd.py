from flask import Flask, Response
import requests
import threading
import time
from termcolor import colored
import config

app = Flask(__name__)

bot = colored("[BOT] ", "green")
botr = colored("[BOT] ", "red")
api = colored("[API] ", "yellow")
apir = colored("[API] ", "red")


class Data():
    orderID = ""
    history = []
    slidingTarget = []
    currentSum = 0.001
    maximumSum = 0.001

data = Data()


def log(a):
    print a
    data.history.append((str(time.strftime('%D  %H:%M:%S')+"   "+a[5:10]+" "+a[15:])))


def avg(a):
    summ=0
    count=0
    for i in a:
        summ+=i
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
            target=float(prices[int((float(config.aggr)/100)*num) ])
            data.slidingTarget.append(target)
            while (len(data.slidingTarget) >= config.smooth):
                data.slidingTarget.remove(data.slidingTarget[0])
            average=avg(data.slidingTarget)
            if target>average:
                log(bot+"Price is rising, targeting average.")
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
                return(0.96*576*(1/mHashR)*10*xRate)
            except:
                log(apir+"Failed to get Max Price. Trying again")
                time.sleep(5)


def currentPrice():
    while True:
        try:
            myApi = requests.get("https://api.nicehash.com/api?method=orders.get&my&id="+config.apiID+"&key="+config.apiKey+"&location=0&algo=24")
            data.orderID = myApi.json()["result"]["orders"][0]["id"]
            return(myApi.json()["result"]["orders"][0]["price"])
        except:
            log(apir+"Failed to get Current Price. Trying again")
            time.sleep(5)


def lowerPrice():
    while True:
        try:
            decrease = requests.get("https://api.nicehash.com/api?method=orders.set.price.decrease&id="+config.apiID+"&key="+config.apiKey+"&location=0&algo=24&order="+str(data.orderID))
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
            setPrice = requests.get("https://api.nicehash.com/api?method=orders.set.price&id="+config.apiID+"&key="+config.apiKey+"&location=0&algo=24&order="+str(data.orderID)+"&price="+str(inp)).json()
            try:
                lamp = setPrice["result"]
                ret = "Sucess"
            except:
                ret = setPrice["result"]["error"]
            return ret
        except:
            log(apir+"Failed to Set Price. Trying again")
            time.sleep(5)


def currentSpeed():
    while True:
        try:
            myApi = requests.get("https://api.nicehash.com/api?method=orders.get&my&id="+config.apiID+"&key="+config.apiKey+"&location=0&algo=24")
            return(myApi.json()["result"]["orders"][0]["accepted_speed"])
        except:
            log(apir+"Failed to get Current Speed. Trying again")
            time.sleep(5)


def rund(inp):
    return float(str(inp)[:6])


def connected():
    try:
        requests.get("http://www.google.ee/")
        return True
    except:
        try:
            requests.get("http://www.neti.ee")
            return True
        except:
            return False


def main():
    while True:
        if connected():
            reload(config)
            log(bot+"Config reloaded")
            speed=float(currentSpeed())*10000000
            target = rund(float(targetPrice()))
            current = float(currentPrice())
            maxp = float(rund(maxPrice()))
            data.currentSum += speed*current
            data.maximumSum += speed*maxp
            ratio = rund(data.currentSum/data.maximumSum)
            con = "Current: "+str(current)+" Target: "+str(target)+" Max: "+str(maxp)+" Speed "+str(speed)+" Ratio: "+str(ratio)
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

def getLast():
    return (len(data.history)/100)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route("/0", methods=["GET"])
@app.route("/", methods=["GET"])
def hello():
    page=0
    last =getLast()
    ret = ""
    if botThread.isAlive():
        ret += "Olen elus :D"
    else:
        ret += "Olen surnud D:"
    ret+="</br>"
    if(page!=last):
        ret+="<a href=\"/1\"> Jargmine </a>"
    ret+="<a href=\"/"+str(last)+"\">Viimane</a>"
    ret += "<ul>"
    for i in range(100):
        try:
            ret += "<li>"+data.history[i]+"</li>"
        except:
            pass
    ret += "</ul>"
    if(page!=last):
        ret+="<a href=\"/1\"> Jargmine </a>"
    ret+="<a href=\"/"+str(last)+"\">Viimane</a>"
    
    
    return ret
   

@app.route("/<int:page>", methods=["GET"])
def page(page):
    last=getLast()
    ret = ""
    if botThread.isAlive():
        ret += "Olen elus :D"
    else:
        ret += "Olen surnud D:"
    ret+="</br>"
    ret+="<a href=\"/\">Esimene </a>"
    ret+="<a href=\"/"+str(page-1)+"\">Eelmine</a>"
    if(page!=last):
        ret+="<a href=\"/"+str(page+1)+"\"> Jargmine </a>"
    ret+="<a href=\"/"+str(last)+"\">Viimane</a>"
    ret += "<ul>"
    for i in range(100):
        try:
            ret += "<li>"+data.history[page*100+i]+"</li>"
        except:
            pass
    ret += "</ul>"
    ret+="<a href=\"/\">Esimene </a>"
    ret+="<a href=\"/"+str(page-1)+"\">Eelmine</a>"
    if(page!=last):
        ret+="<a href=\"/"+str(page+1)+"\"> Jargmine </a>"
    ret+="<a href=\"/"+str(last)+"\">Viimane</a>"
    return ret




if __name__ == "__main__":
    print("Starting bot")
    botThread = threading.Thread(target=main)
    botThread.start()
    print("Bot started")
    print("Starting web server")
    webThread=threading.Thread(target=app.run, args=("0.0.0.0", 4000))
    webThread.start()
    print("Web server started")
