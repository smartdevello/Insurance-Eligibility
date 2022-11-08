# -*- coding: utf-8 -*-
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import random
import logging
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager.firefox import GeckoDriverManager

class Bot:
    def __init__(self):
        self.url = "https://infocenter.humana-military.com/provider/service/Account/Login"
        self.search_url = "https://infocenter.humana-military.com/provider/service/"
        self.username = 'homefrontpumpse1'
        self.pw = '815!@#Hudspeth'
        self.metabase_url = "http://metabase-izk7e-env.us-east-1.elasticbeanstalk.com/public/question/28f0fdde-3733-4881-87dc-94b78ed51c23.json"
        self.api_key = "2c00cd3434f14892b5372c24a9581946"
        self.post_url = "http://dmez.us-east-1.elasticbeanstalk.com/api/customers-payers/verify.json?api_key={}".format(self.api_key)
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.pdf_path = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        try:
            if self.drive is not None:
                self.drive.quit()
        except Exception as e:
            pass

    def browser_init(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        binary = FirefoxBinary('/usr/bin/firefox-esr')
        
        profile = webdriver.FirefoxProfile()

        profile.set_preference("general.useragent.override", "hi")
        
        webdriver.Firefox( executable_path=GeckoDriverManager().install(), options=options)#
        drive = webdriver.Firefox(profile)


        drive.get(self.url)
        drive.set_window_size(1440, 1440)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        user_name = drive.find_element_by_id('txtUserId')
        user_name.send_keys(self.username)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        password = drive.find_element_by_id('txtPassword')
        password.send_keys(self.pw)
        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)
        login_button = drive.find_element_by_id('btnLogIn')
        drive.execute_script("arguments[0].click();", login_button)

        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)
        
        drive.save_screenshot(self.abs_path + "/bypass_or_not.png")
        
        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)
        self.drive = drive


with Bot() as scraper:
    scraper.browser_init()