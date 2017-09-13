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
                
            
        except Exception as e:
            print(e)
            time.sleep(5)
print(targetPrice())
