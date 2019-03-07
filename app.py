from flask import Flask, request
import os
import requests
import json
from selenium import webdriver
import time
import datetime

app = Flask(__name__)
os.environ['PATH'] += ':'+os.path.dirname(os.path.realpath(__file__))+"/webdrivers/chromedriver.exe"

# Initialize the headless browser that is going to be used by the app.
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = True
chrome_driver = webdriver.Chrome(
    'webdrivers/chromedriver.exe',
    options = chrome_options
    )

# Dictionary to map city names to the correct code used by SNCF ( NOT COMPLETE )
_city_dict = {"Paris":"FRPAR", "Vannes":"FRVNE", "Lille":"FRLIL"}

def get_tgvmax_available(departure_city, arrival_city, date):

    date = date.strftime("%Y%m%d")
    # Generate the correct URL for the itinerary
    base_url = "https://www.oui.sncf/bons-plans/tgvmax#!"
    url_params_one = ("{}/{}/{}".format(_city_dict[departure_city],_city_dict[arrival_city],date))
    verbose = "ONE_WAY/2/12-HAPPY_CARD"
    last_part = "{}-{}-{}-{}".format(_city_dict[departure_city],_city_dict[arrival_city],date,date)

    url = '/'.join([base_url,url_params_one,verbose,last_part])

    print (url)

    response = []
    
    chrome_driver.get(url)
    time.sleep(5)
    
    elements_tgvmax = chrome_driver.find_elements_by_css_selector(".proposal.best-price-of-calendar.tgv-max-price")
    
    if(not elements_tgvmax):
        print("Pas de trajet tgvmax trouvés")
        return "Aucun trajet disponible"
    else:
        for element in elements_tgvmax:
            infos = element.text.split('\n')
            departure_time = infos[0]
            departure_station = infos[1]
            arrival_time   = infos[2]
            arrival_station = infos[3]
            duration = infos[4]
            response.append({'departure_time':departure_time,
                             'departure_station':departure_station,
                             'arrival_time':arrival_time,
                             'arrival_station':arrival_station,
                             'duration':duration})
        return (response)

@app.route('/setup_tgvmax_alert', methods=['POST'])
def setup_tgvmax_alert():
    data = request.get_json()

    departure_city  = data['departure_city']
    arrival_city    = data['arrival_city']
    # Transform the parsed date to the format necessary for the url
    date            = datetime.date.fromisoformat(data['date'])

    response    = get_tgvmax_available(departure_city, arrival_city, date)

    return json.dumps({"Itineraries": response})

# run Flask app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, threaded=True)