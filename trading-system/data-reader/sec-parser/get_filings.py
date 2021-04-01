import requests
import os
import re

import urllib.request
from bs4 import BeautifulSoup
from urllib.error import HTTPError


# AAPL
# cik = "320193"
# "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-k&dateb=20190101&owner=exclude&output=xml&count=100".format(cik)

def main():

    #input_type = input("Enter the file type : ")
    input_type = "10-q"

    fp = open("../../../data/tickers.txt")
    ticker_list = fp.readlines()
    #ticker_list = ['AAPL']

    for ticker in ticker_list:
        ticker = ticker.strip('\n')


        cik_dict = getCIK(ticker)
        cik = cik_dict[ticker]

        url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={0}&type={1}&dateb=20210101&owner=exclude&output=xml&count=100".format(cik, input_type)

        r = requests.get(url)
        data = r.text # Write this to a XML file to analyze page response

        path_dict = get_path_list(data)

        for year, paths in path_dict.items():
            for path in paths:

                quarter = 'q' + str(3 - paths.index(path))

                if input_type is "10-q":
                    filename = "-".join([ticker, input_type.replace("-", ""), year, quarter])
                elif input_type is "10-k":
                    filename = "-".join([ticker, input_type.replace("-", ""), year])

                print("Downloading :: |" + year + "|" + " --> " + "|" + input_type + "|" + " -->  "+ path)

                if not os.path.exists('../../../data/' + ticker):
                    os.mkdir('../../../data/' + ticker)

                if not os.path.exists('../../data/' + ticker):
                    os.mkdir('../../../data/' + ticker)

                if not os.path.exists('../../../data/' + ticker + '/' + year):
                    os.mkdir('../../../data/' + ticker + '/' + year)
                    os.mkdir('../../../data/' + ticker + '/' + year + '/unprocessed')
                    os.mkdir('../../../data/' + ticker + '/' + year + '/processed')


                output_path = "../../../data/" + ticker + "/" + year + "/unprocessed/" + filename
                print("Output Path :: " + output_path  + "\n")

                try:
                    urllib.request.urlretrieve(path + "/Financial_Report.xlsx", filename=output_path + ".xlsx")

                except HTTPError as err:
                    try:
                        urllib.request.urlretrieve(path + "/Financial_Report.xls", filename=output_path + ".xls")
                    except HTTPError as err:
                        print(err)

        print("***** " + ticker + " COMPLETED *****\n\n\n")


def get_path_list(data):
    # parse fetched data using BeautifulSoup
    soup = BeautifulSoup(data, features='lxml')

    path_dict = dict()

    for element in soup.find_all('filing'):
        if (element.find("xbrlref") != None):
            filing = element.find('filinghref')
            year = (element.find('datefiled').text)[:4]

            path = "/".join(filing.text.split("/")[:-1])

            if not year in path_dict:
                path_dict[year] = []

            path_dict[year].append(path)

    return path_dict


def getCIK(ticker):
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    cik_dict = {}

    f = requests.get(URL.format(ticker), stream = True)
    results = CIK_RE.findall(f.text)
    if len(results):
        results[0] = int(re.sub('\.[0]*', '.', results[0]))
        cik_dict[str(ticker).upper()] = str(results[0])

    f = open('cik_dict', 'w')
    f.close()

    return cik_dict


if __name__ == "__main__":
    main()



