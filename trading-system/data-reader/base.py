import logging
import requests
import atexit
import datetime
from collections import namedtuple
import json
import re

from bs4 import BeautifulSoup

import pandas as pd

from limitmanager import LimitManager
from exceptions import *


class ClientBase:
    """
    Parent class of data fetchers that interacts with data provider back-end services.
    """

    def __init__(self, session = False):
        self._base_tiingo_url = "https://api.tiingo.com/tiingo/"

        self.lm = LimitManager()

        atexit.register(self._exit_handler)

        # TODO : add default case if the current token read at init is invalid
        self.current_token = self.lm.get_current_token()

        self.query_base = 'https://query1.finance.yahoo.com'

        self._exp_dates = {}

        if session is True:
            self._current_session = requests.Session()
        else:
            self._current_session = requests


    def _make_request(self, url):
        '''
        Makes an HTTP request and returns the response.
        Params:
        - url: The url endpoint that is going to be added on top of the base
        '''

        try:
            self.lm.make_call()
        except (OverDailyLimit, OverHourlyLimit):
            self.lm.switch_token()

            if self.lm.get_current_token() == -1:
                raise OutOfTokensException()
            else:
                self.lm.reset()
                self.lm.make_call()

        current_token = self.lm.get_current_token()
        if current_token == -1:
            self.lm.reset()
            raise OutOfTokensException()

        header = self.lm.get_auth_header()

        res = self._current_session.get(''.join([self._base_tiingo_url, url]), headers=header)

        return res

    def _exit_handler(self):
        self.lm.write_to_file()

    def _retrieve_option_chain(self, ticker, date=None):
        if date is None:
            options = self._download_options(ticker)
        else:
            if not self._exp_dates:
                self._download_options(ticker)
            if date not in self._exp_dates:
                raise ValueError()
            date = self._exp_dates[date]
            options = self._download_options(ticker, date)

        return namedtuple('Options', ['calls', 'puts'])(**{
            "calls": self._getOption(options['calls']),
            "puts": self._getOption(options['puts'])
        })

    def _getOption(self, option):
        data = pd.DataFrame(option).reindex(columns=[
            'contractSymbol', 'lastTradeDate', 'strike', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 
            'volume', 'openInterest', 'impliedVolatility', 'inTheMoney', 'contractSize', 'currency'])

        data['lastTradeDate'] = pd.to_datetime(
            data['lastTradeDate'], unit='s')

        return data

    def _download_options(self, ticker, date=None):
        if date is None:
            url = "{}/v7/finance/options/{}".format(
            self.query_base, ticker)
        else:
            url = "{}/v7/finance/options/{}?date={}".format(
            self.query_base, ticker, date)

        r = requests.get(url=url).json()
        if r['optionChain']['result']:
            for exp in r['optionChain']['result'][0]['expirationDates']:
                self._exp_dates[datetime.datetime.fromtimestamp(exp).strftime('%Y-%m-%d')] = exp
            return r['optionChain']['result'][0]['options'][0]
        return {}

    def _retrieve_option_dates(self, ticker):
        if not self._exp_dates:
            self._download_options(ticker)
        return tuple(self._exp_dates.keys())

    def _retrieve_current_price(self, ticker):
        url_yfin = "https://finance.yahoo.com/quote/{0}?p={1}&.tsrc=fin-srch".format(ticker, ticker)

        res = requests.get(url_yfin)

        soup = BeautifulSoup(res.text, 'html.parser')

        price = soup.find_all('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text

        return price

    def _retrieve_recommendations(self, ticker):
        url = 'https://finance.yahoo.com/quote/{0}'.format(ticker)

        data = self._retrieve_quote_json(url)

        self.scrape_base = 'https://finance.yahoo.com/quote'

        info = pd.DataFrame(data['upgradeDowngradeHistory']['history'])
        
        info['earningsDate'] = pd.to_datetime(info['epochGradeDate'], unit='s')
        
        info.set_index('earningsDate', inplace=True)
        info.index.name = 'Date'

        info.columns = [re.sub("([a-z])([A-Z])", "\g<1> \g<2>", i).title() for i in info.columns]

        self._recommendations = info[['Firm', 'To Grade', 'From Grade', 'Action']].sort_index()

        return self._recommendations

    def _retrieve_quote_json(self, url):
        page = requests.get(url=url).text
        if "QuoteSummaryStore" not in html:
            page = requests.get(url=url).text
            if "QuoteSummaryStore" not in html:
                return {}

        string = page.split('root.App.main =')[1].split('(this)')[0].split(';\n}')[0].strip()
        
        str_data = json.loads(string)['context']['dispatcher']['stores']['QuoteSummaryStore']

        json_str = json.dumps(str_data).replace('{}', 'null')
        
        json_str = re.sub(r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)\}', r'\1', json_str)

        return json.loads(json_str)

    def _retrieve_holder_info(self, ticker):
        url = "https://finance.yahoo.com/quote/{0}/holders".format(ticker)

        holders = pd.read_html(url)

        major_holders = holders[0]

        return major_holders

    def _retrieve_instituional_holders(self, ticker):
        url = "https://finance.yahoo.com/quote/{0}/holders".format(ticker)

        holders = pd.read_html(url)

        if (len(holders) < 2):
            return None

        institutional_holders = holders[1]

        if 'Date Reported' in institutional_holders:
            institutional_holders['Date Reported'] = pd.to_datetime(
                institutional_holders['Date Reported'])

        if '% Out' in institutional_holders:
            institutional_holders['% Out'] = institutional_holders[
                '% Out'].str.replace('%', '').astype(float)/100

        return institutional_holders

    def _retrieve_sustainability_info(self, ticker):
        url = 'https://finance.yahoo.com/quote/{0}'.format(ticker)
        data = self._retrieve_quote_json(url)

        dic = {}
        if isinstance(data.get('esgScores'), dict):
            for item in data['esgScores']:
                if not isinstance(data['esgScores'][item], (dict, list)):
                    dic[item] = data['esgScores'][item]

            info = pd.DataFrame(index=[0], data=dic)[-1:].T
            info.columns = ['Value']
            info.index.name = '%.f-%.f' % (info[info.index == 'ratingYear']['Value'].values[0], info[info.index == 'ratingMonth']['Value'].values[0])

            sust_info = info[~info.index.isin(
                ['maxAge', 'ratingYear', 'ratingMonth'])]

        return sust_info

    def _retrieve_isin(self, ticker):
        if "-" in ticker or "^" in ticker:
            self._isin = '-'
            return self._isin

        q = ticker

        url = 'https://markets.businessinsider.com/ajax/' \
            'SearchController_Suggest?max_results=25&query=%s' \
            % q
        data = requests.get(url=url).text

        search_str = '"{}|'.format(ticker)
        if search_str not in data:
            if q.lower() in data.lower():
                search_str = '"|'
                if search_str not in data:
                    self._isin = '-'
                    return self._isin
            else:
                self._isin = '-'
                return self._isin

        isin = data.split(search_str)[1].split('"')[0].split('|')[0]
        
        return isin



