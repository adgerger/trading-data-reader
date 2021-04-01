import os

from exceptions import (
    OverDailyLimit,
    OverHourlyLimit
)
# ! change the path to full directory name in the main code base


class LimitManager:

    HOURLY_MAX = 500
    DAILY_MAX = 20000
    BANDWITH = 5.00

    API_TOKENS = ["0a1d713c046f36d549361069b68441e40b33ee74", "0a1d713c046f36d549361069b68441e40b33ee74"]

    TOKEN = {}

    NUM_TOKENS = len(API_TOKENS)

    def __init__(self):
        self._init_tokens()

        if os.path.isfile('../../data/api-info.txt'): # Assumes if the file exists, the data in it is not corrupt
            with open ('../../data/api-info.txt', 'r+') as fp:
                lines = fp.readlines()
                print(lines)
                self.current_token = int(lines[3].strip('\n'))

                self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] = int(lines[0].strip('\n'))
                self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] = int(lines[1].strip('\n'))
                self.TOKEN[self.API_TOKENS[self.current_token]]["BANDWITH"] = int(lines[2].strip('\n'))

        else:
            self.current_token = 0

            self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] = 0
            self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] = 0
            self.TOKEN[self.API_TOKENS[self.current_token]]["BANDWITH"] = 0

    def _init_tokens(self):
        for token in self.API_TOKENS:
            self.TOKEN[token] = {"HOURLY_REQ": 0, "DAILY_REQ": 0, "BANDWITH": 0}

    def make_call(self):
        if (self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] < self.HOURLY_MAX and self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] < self.DAILY_MAX):

            self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] += 1
            self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] += 1

        else:
            if not (self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] < self.HOURLY_MAX):
                raise OverHourlyLimit(self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"])

            if not ( self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] < self.DAILY_MAX):
                raise OverDailyLimit(self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"])

    def write_to_file(self):
        with open ('../../data/api-info.txt', 'w+') as fp:
            lines = list()
            if self.current_token == -1:
                lines.append("0\n")
                lines.append("0\n")
                lines.append("0\n")
                lines.append("-1\n")
            else:
                lines.append(str(self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"]) + '\n')
                lines.append(str(self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"]) + '\n')
                lines.append(str(self.TOKEN[self.API_TOKENS[self.current_token]]["BANDWITH"]) + '\n')
                lines.append(str(self.current_token) + '\n')

            fp.writelines(lines)


    def get_auth_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization' : 'Token {0}'.format(self.API_TOKENS[self.current_token])
        }

    def switch_token(self):
        self.current_token += 1

    def get_current_token(self):
        if self.current_token >= self.NUM_TOKENS:
            # self.reset()
            self.current_token = -1

        return self.current_token

    def reset(self):
        print(self.current_token)
        self.TOKEN[self.API_TOKENS[self.current_token]]["HOURLY_REQ"] = 0
        self.TOKEN[self.API_TOKENS[self.current_token]]["DAILY_REQ"] = 0
        self.TOKEN[self.API_TOKENS[self.current_token]]["BANDWITH"] = 0

    def make_test_request(self):
        res = requests.get("https://api.tiingo.com/api/test", headers=headers)

        json_res = res.json()

        print(json_res)

        if json_res['message'] == 'You successfully sent a request':
            return 1
        else:
            print(json_res['message'])
            return 0


