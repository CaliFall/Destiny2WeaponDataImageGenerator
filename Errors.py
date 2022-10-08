class MyError(Exception):
    pass

class APINetworkError(MyError):
    pass

class APILocalError(MyError):
    pass

class DataBaseNetworkError(MyError):
    pass

class DataBaseLocalError(MyError):
    pass

class BotNetworkError(MyError):
    pass

class BotLocalError(MyError):
    pass


if __name__ == "__main__":
    pass
