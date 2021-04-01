

class OverHourlyLimit(Exception):
    """Exception raised when over hourly call limit.

    Attributes:
        hourly_req -- current hourly requests made
    """
    def __init__(self, hourly_req):
        self.hourly_req = hourly_req
        self.message = "You are over your hourly request limit ({0} requests made).".format(self.hourly_req)
        super().__init__(self.message)



class OverDailyLimit(Exception):
    """Exception raised when over daily call limit.

    Attributes:
        daily_req -- current hourly requests made
    """
    def __init__(self, daily_req):
        self.daily_req = daily_req
        self.message = "You are over your daily request limit ({0} requests made).".format(self.daily_req)
        super().__init__(self.message)


class OutOfTokensException(Exception):
    """
    Exception raised when there are no available api tokens left.
    """
    def __init__(self):
        self.message = "There are no more tokens left to use."
        super().__init__(self.message)

class ClientCallError(Exception):
    """
    Exception to wrap around HTTP GET request errors.
    """
    pass



