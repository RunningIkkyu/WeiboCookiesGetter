from setting import ACCOUNTS_FILE_NAME
from setting import ACCOUNTS_FILE_SEP
from db import Mongo

class Accounts(object):
    """ Provie operations about accounts"""
    def __init__(self, filename=ACCOUNTS_FILE_NAME, sep=ACCOUNTS_FILE_SEP):
        self.filename = ACCOUNTS_FILE_NAME
        self.sep = ACCOUNTS_FILE_SEP
        self.accounts = self.getall()
        self.db = Mongo()

    def delete(self, username):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        with open(self.filename, 'w') as f:
            for line in lines:
                if username not in line:
                    f.write(line)

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
    a = Accounts().accounts
    for i in a:
        print(i)
