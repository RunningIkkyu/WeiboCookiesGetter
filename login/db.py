import pymongo
from pymongo import MongoClient
from setting import MONGODB_IP, MONGODB_PROT

class Mongo(object):
    """ Database relavent operation. """
    def __init__(self, ip=MONGODB_IP, port=MONGODB_PROT):
        """ Connecting to mongodb and open database"""
        self.client = MongoClient(ip, port)
        db = self.client.cookies_db
        self.set = db.cookie_set
        self.set.create_index([('username', pymongo.ASCENDING)], unique=True)

    def exist(self, username):
        """See if username in database. 
        Return the item if found success, else return None.
        """
        query = {'username': username}
        return self.set.find_one(query)

    def insert_one(self, username, cookie):
        """ Insert one data to db. 
        : param username: username
        : param cookie: the cookie of username in the type of dict. 
        """
        d = {}
        d['username'] = username
        d['cookie'] = cookie
        try:
            self.set.insert_one(d)
        except Exception as e:
            print("[ERROR] Insert Failed!", e)

    def del_cookie(self, username):
        """ Delete a cookie from database by given username."""
        try:
            self.set.remove({'username': username})
        except Exception as e:
            print("[ERROR] Remove Failed!", e)

    def update_cookie(self, username, cookie):
        """ Update cookie. """
        query = {'username': username}
        newvalue = {"$set": {'cookie': cookie}}
        try:
            self.set.update_one(query, newvalue)
        except Exception as e:
            print("[ERROR] Remove Failed!", e)

    def getcookie(self, username):
        """ Get the cookie of given username."""
        query = {'username': username}
        try:
            record = self.set.find_one(query)
            if record:
                return record.get('cookie')
            else:
                print('[ERROR] {} was not found in db.'.format(username))
        except Exception as e:
            print("[ERROR] Query Failed!", e)

    def getall(self):
        """ Get all record in the database return as generator. """
        for record in self.set.find():
            yield record



if __name__ == "__main__":
    db = Mongo()
    #username = 'xxx@bbb.com'
    #cookie = {
    #    'SEO':'aieng',
    #    'alive':True,
    #}
    ## insert test
    #db.insert_one(username, cookie)
    #for i in db.getall():
    #    print(i)
    print(db.exist('kfzj280618539@sina.co1m'))

    #print('query test')
    #res = db.getcookie(username)
