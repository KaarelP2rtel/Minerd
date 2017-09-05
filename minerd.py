from flask import Flask, render_template, request, Response
import requests

app = Flask(__name__)




@app.route("/", methods=["GET"])
def hello():
    api = requests.get("http://whattomine.com/coins.json")
    priceData = api.json()
    mHashR = float(priceData['coins']["Zcash"]["nethash"])/1000000
    xRate = float(priceData['coins']["Zcash"]["exchange_rate"])
    suggested=576*(1/mHashR)*10*xRate
    return "Suggested: "+str(suggested)
	
	
	
if __name__ == "__main__":
    app.run("0.0.0.0", 80)
