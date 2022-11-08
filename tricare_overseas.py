import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import time
import csv
import random
import logging
from PIL import Image


class Bot:
    def __init__(self):
        self.url = "https://portal.tricare-overseas.com/wps/myportal/osp/tricare-provider-os/!ut/p/z1/jY_NCsIwEISfpke78a8Wb0GoRdNSQbDmIqmkaSBNShpb8OkNeBKUurfZ_XZmFyiUQDUbpGBOGs2U11ca3Yo0jdJ5jMienDYIF9GxyJN8gZIVXKYA6sfoR2EEhynAX7Cw2S4TQDvmmpnUtYFSGSG1D6d_-AtlqvcrWFfL2BtZXnPLbfiwvt041_XbAAVoHMdQGCMUD--mDdC3lcb0DspPErq2fJL6vFYDwS8StybZ/dz/d5/L2dBISEvZ0FBIS9nQSEh/"
        self.username = 'HFPOverseas'
        self.pw = 'Y@tgubQJY74*eQn'
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
                self.drive.close()
                self.drive.quit()
        except Exception as e:
            pass

    def browser_init(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--profile-directory=Default')
            
        chrome_options.binary_location = "/usr/bin/google-chrome" 
        chrome_options.add_argument("--headless")
        executable_path = "/home/ubuntu/.wdm/drivers/chromedriver/linux64/91.0.4472.101/chromedriver"
        
        # executable_path = 'D:\My Work\Vijay\chromedriver.exe'

        drive = webdriver.Chrome(executable_path, chrome_options=chrome_options)
        drive.get(self.url)
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)

        try:
            drive.find_element(By.CSS_SELECTOR, '#myModalPaperlessPay button.close').click()
        except Exception as e:
            pass

        user_name = drive.find_element(By.ID, 'username')
        user_name.send_keys(self.username)
        password = drive.find_element(By.ID, 'password')
        password.send_keys(self.pw)
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)
        login_button = drive.find_element(By.CSS_SELECTOR, '#loginForm button').click()
        iwait = random.randint(4, 5) + random.random()        
        time.sleep(iwait)

        try:
            drive.find_element(By.CSS_SELECTOR, '#loginForm div.a-forgot a').click()
            time.sleep(3)
        except Exception as e:
            pass

        try:
            drive.find_element(By.CSS_SELECTOR, '#myModalPaperlessPay button.close').click()
            time.sleep(3)
        except Exception as e:
            pass
        drive.set_window_size(1440, 1440)
        self.drive = drive
    
    def get_metabase(self):
        metabase_json = requests.get(self.metabase_url).json()
        logging.warning("The metabase has {} patients info.".format(len(metabase_json)))
        return metabase_json
    
    def get_dob(self, customer_dob):
        dob = ""
        tmp = customer_dob.split('T')[0].split('-')
        dob = tmp[1] + '/' + tmp[2] + '/' + tmp[0]
        return dob


    def check_tricare_overseas(self, patient):
        drive = self.drive
        WebDriverWait(self.drive, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#aw-wps-main-navigation li.patient-eligibility a"))).click()
        eligibilityOptions = drive.find_element(By.ID, 'eligibilityOptions')
        Select(eligibilityOptions).select_by_index(1)
        time.sleep(3)

        drive.find_element(By.ID, 'sponsorSsnOption').send_keys(patient['member_number'])

        time.sleep(2)
        drive.find_element(By.ID, 'patientEligibilitySearch').click()
        time.sleep(5)

        drive.find_element(By.CSS_SELECTOR, '#patientEligibilityContainer button').click()
        time.sleep(3)
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')
        drive.execute_script("window.scrollTo(0, 200);")
        time.sleep(3)
        flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'to0.png')
        if flag == False:
            print('================faield to save screenshot to0.png========================')
        else:
            print('================saved screenshot ' + img_tmp + 'to0.png========================')
            
# with Bot() as scraper:            
#     scraper.browser_init()
#     scraper.check_tricare_overseas({})