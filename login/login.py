import json
import csv
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from random_user_agent.user_agent import UserAgent

from proxy import GetProxy
from db import Mongo
from account import GetAccounts
from setting import PROXY_ENABLE, LOGIN_ENTRANCE


class Crack(object):
    """
    crack geetest click captcha and auto login.
    please make sure you have generated the mouse-track file before.
    And make sure mongod server is running.
    """
    def __init__(self, username, password, trackfilename='track.txt'):
        # get login information and init variable.
        self.username = username
        self.password = password
        self.cookies = ''
        self.db = Mongo()

        # this is login entrance
        self.url = LOGIN_ENTRANCE
        self.proxy = ''

        # read track data
        self.trackfilename = trackfilename
        self.track = []
        with open(self.trackfilename,'r') as f:
            self.track = json.load(f)

    def exist(self):
        """ Check if the username is verified before. """
        return self.db.exist(self.username)

    def get_proxy(self):
        # Get proxy.
        self.proxy = GetProxy().getproxy()

    def open_browser(self):
        """ Start Chrome headless, add proxy and run in headless mode."""
        print('Getting user agent...')
        ua = UserAgent().get_random_user_agent()
        chrome_options = Options()
        chrome_options.add_argument('user-agent={}'.format(ua))
        print('[INFO] Setting useragent success: {ua}')
        #chrome_options.add_argument('--headless')

        # If proxy flag is open, then get a proxy.
        if PROXY_ENABLE:
            self.get_proxy()
            chrome_options.add_argument('--proxy-server=' + self.proxy.get('http'))
            print('[INFO] Proxy set success')
        try:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            print('[INFO] Browser open success')
        except Exception as e:
            print('[WANNING login.py] Proxy cannnot use.') 
        self.wait = WebDriverWait(self.driver, 6)

        # Waiting for login entrance.
        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(5)
        except Exception as e:
            print("Target URL cannot be reached: ", e)

    def __del__(self):
        """ Destroy the web browser """
        self.driver.close()

    def wait_for_main_page(self):
        """ 
        Waiting for the loading of main page
        :return : If the main page load in given time, return True.
        """
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'main-wrap')))
            print('[INFO] Mainpage loaded')
            return True
        except:
            print('[INFO] Mainpage no found!')
            return False

    def move(self):
        """ Move mouse by using given track """
        print('[INFO] Moving mouse.')
        for offset, sleeptime in self.track:
            x, y = offset
            ActionChains(self.driver).move_by_offset(x,y).perform()
            time.sleep(sleeptime)
        ActionChains(self.driver).click().perform()

    def wait_for_login(self):
        """ Waiting until the presence of login button. """
        class button():
            def __call__(self, driver):
                if driver.find_element_by_xpath('//*[@id="loginAction"]'):
                    return True
                else:
                    return False
        try:
            WebDriverWait(self.driver, 10, 0.5).until(button())
        except:
            print('waiting too long')
            return False
        return True

    def login(self):
        """ 
        Login weibo by selenium.
        This method will input username and password and auto submit the form.
        If there is a CAPTCHA after submit form, will call crack function.
        """


        # Input username and password.
        print('Inputing username and password...', end='')
        username_area = self.driver.find_element_by_xpath('//*[@id="loginName"]')
        username_area.send_keys(self.username)
        time.sleep(2)
        psw_area = self.driver.find_element_by_xpath('//*[@id="loginPassword"]')
        psw_area.send_keys(self.password)
        time.sleep(3)
        print('Ok')

        # Submit login form.
        print('Posting form data...', end='')
        btn = self.driver.find_element_by_xpath('//*[@id="loginAction"]')
        btn.click()
        print('Ok')

        #WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(By.ID, 'errorMsg'))
        if self.driver.find_element_by_xpath('//*[@id="errorMsg"]'):
            print('Password wrong')
            return 

        # If their is a CAPTCHA, then crack it.
        if self.driver.current_url.find('CAPTCHA'):
            print('[INFO] CAPTCHA has been detected, need crack.')
            self.crack()
        else:
            ret = self.wait_for_main_page()
            self.cookies = self.driver.get_cookies()

    def crack(self):
        """ Crack the click CAPTCHA """
        # Waiting for button loading.
        class button():
            def __call__(self, driver):
                if driver.find_element_by_xpath('//div[@aria-label="点击按钮进行验证"]'):
                    return True
                else:
                    return False
        print('Loading CAPTCHA...', end='')
        WebDriverWait(self.driver, 10, 0.5).until(button())
        print('Compelete')
        
        # find button and move to the button
        print('Cracking...', end='')
        btn = self.driver.find_element_by_xpath('//div[@aria-label="点击按钮进行验证"]')
        time.sleep(1)
        ActionChains(self.driver).move_to_element(btn).perform()
        self.move()
        ActionChains(self.driver).click().perform()
        print('Complete')

        # waiting from page and get cookies
        ret = self.wait_for_main_page()
        if ret:
            print('Cracking success!')
        # Choose-Word-CAPTCHA  has been appeared, need second verification.
        elif EC.presence_of_element_located((By.CLASS_NAME, 'geetest_commit_tip')):
            print('[INFO] Cracking failed, Choose-Word-CAPTCHA has been appeared!')
            return False
            # crack_choose_CAPTCH()
        # Slide-CAPTCHA  has been appeared, need second verification.
        elif EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slider_track')):
            print('[INFO] Cracking failed, Slider-CAPTCHA has been appeared!')
            return
            # crack_slide_CAPTCH()
        else:
            print('[INFO] Unknown Error!')
            return
            # log_error()

        if ret:
            cookies_dict = {}
            cookies = self.driver.get_cookies()
            for d in cookies:
                cookies_dict[d['name']] = d['value']
            print('Get cookies:', cookies_dict)
            self.cookies = json.dumps(cookies_dict)

    def save(self):
        """
        Save cookie to database if got success.
        This function will check if _T_WM showed in cookies as a sign of success.
        """
        if self.cookies.find('_T_WM'):
            self.db.insert_one(self.username, self.cookies)
        else:
            print('[ERROR login.py] cookies not valid. cookies: {}'.format(self.cookies))


    def run(self):
        self.open_browser()
        self.login()
        self.save()


if __name__ == '__main__':
    accounts = list(GetAccounts().accounts)
    for username, password in accounts:
        Crack(username, password).run()
