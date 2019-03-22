from setting import ACCOUNTS_FILE_NAME
from setting import ACCOUNTS_FILE_SEP
from db import Mongo

class GetAccounts(object):
    """ Get username and password from file"""
    def __init__(self, filename=ACCOUNTS_FILE_NAME, sep=ACCOUNTS_FILE_SEP):
        self.filename = ACCOUNTS_FILE_NAME
        self.sep = ACCOUNTS_FILE_SEP
        self.accounts = self.getall()
        self.db = Mongo()

    def getall(self):
        """ Get a generator of username and password. 
        Each element in this format: (username, password)
        """
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    username, password = line.split(self.sep)
                except:
                    print('[ERROR] Error occured when reading accounts: ', line)
                if not self.db.exist(username):
                    yield (username.strip(), password.strip())



if __name__ == "__main__":
    a = GetAccounts().accounts
    for i in a:
        print(i)
