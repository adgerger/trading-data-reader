import urllib
import urllib.request
from urllib.error import HTTPError

from bs4 import BeautifulSoup
import datetime



class EventReader:

    def __init__(self):
        url = "https://www.investing.com/economic-calendar/"
        self.req = urllib.request.Request(url)
        self.req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        self.result = []


    def fetchMacroEvents(self):
        try:
            response = urllib.request.urlopen(self.req)

            html = response.read()

            soup = BeautifulSoup(html, "html.parser")

            table = soup.find('table', {"id": "economicCalendarData"})
            tbody = table.find('tbody')
            rows = tbody.findAll('tr', {"class": "js-event-item"})

            allEvents = []

            for row in rows:
                if len(row.find('td', {"class": "left textNum sentiment noWrap"}).findAll('i', {"class": "grayFullBullishIcon"})) == 3:

                    event = {'timestamp': None,
                    'country': None,
                    'url': None,
                    'name': None,
                    'actual': None,
                    'forecast': None,
                    'color': None,
                    'prev': None
                    }

                    date = row.attrs['data-event-datetime']
                    event["timestamp"] = date

                    country = row.find('td', {"class": "left flagCur noWrap"}).find('span').get('title')
                    event["country"] = country

                    eventName = row.find('td', {"class": "left event"}).find('a')

                    url = "https://www.investing.com" + eventName.get('href')
                    event["url"] = url

                    eventName = eventName.text.strip()
                    event["name"] = eventName

                    actual = row.find('td', {"class": "bold"})

                    if actual.get('title') == "Worse Than Expected":
                        event['color'] = "red"
                    else:
                        event['color'] = "green"

                    actual = actual.text
                    event["actual"] = actual

                    forecast =  row.find('td', {"class": "fore"})
                    forecast = forecast.text
                    event["forecast"] = forecast

                    prev =  row.find('td', {"class": "prev"})
                    prev = prev.text
                    event["prev"] = prev
                    allEvents.append(event)

            return allEvents

        except HTTPError as error:
            print ("Oops... Get error HTTP {}".format(error.code))


