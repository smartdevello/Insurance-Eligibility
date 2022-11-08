import pandas as pd
import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import csv
import random
import logging
from PIL import Image
import json
from webdriver_manager.firefox import GeckoDriverManager
from PyPDF2 import PdfFileMerger
from PyPDF2 import PdfFileReader


class Bot:
    def __init__(self):
        self.url = "https://infocenter.humana-military.com/provider/service/Account/Login"
        self.msg_url = "https://infocenter.humana-military.com/provider/service/communications/SecureMessages/compose"
        self.username = 'homefrontpumpse1'
        self.pw = '!@#Hudspeth815'
        self.api_key = "2c00cd3434f14892b5372c24a9581946"
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.pdf_path = ''
        self.url4list = "http://metabase-izk7e-env.us-east-1.elasticbeanstalk.com/public/question/21c6de82-1cf0-450a-8fbf-cd1a4a58d2da.json"
        self.url4attachtomodel = "http://dmez.us-east-1.elasticbeanstalk.com/api/documents/attach_to_model.json?api_key=2c00cd3434f14892b5372c24a9581946"
        self.headers = {'Cookie': 'CAKEPHP=91f37b149b22c2518b0b6c304ed49502'}

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
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "hi")
        
        # options.add_argument("--headless")
        # binary = FirefoxBinary('/usr/bin/firefox-esr')
        # executable_path = "/usr/local/bin/geckodriver"

        binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
        executable_path = 'D:\My Work\Vijay\geckodriver.exe'
        
       
        drive = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary, executable_path=executable_path,options=options)
        
        drive.get(self.url)
        drive.set_window_size(1440, 1440)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        user_name = drive.find_element(By.ID, 'txtUserId')
        user_name.send_keys(self.username)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        password = drive.find_element(By.ID, 'txtPassword')
        password.send_keys(self.pw)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        login_button = drive.find_element(By.ID, 'btnLogIn')
        drive.execute_script("arguments[0].click();", login_button)
        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)
        self.drive = drive

    def main(self):

        url_list = []
        while True:
            flag = False
            try:
                response = requests.get(self.url4list)
                if response.status_code == 200:
                    tricare_list = response.json()
                    for tricare in tricare_list:
                        if tricare['id'] == 1:
                            print(tricare)
                            url_list.append(tricare['url'])
                    flag = True
            except Exception as e:
                pass
            if flag:
                break


        for patient_info in url_list:
            try:
                response = self.send_document_claims(patient_info)
                if response is False:
                    logging.warning('failed')
            except Exception as e:
                print(e)
                pass

    def get_dob(self, customer_dob):
        dob = ""
        print(customer_dob)
        tmp = customer_dob.split(' ')[0].split('-')
        dob = tmp[1] + '/' + tmp[2] + '/' + tmp[0]
        return dob

    def get_name(self, customer):
        name = ''
        try:
            if len(customer['middlename']) > 0:
                name = customer['firstname'] + ' ' + customer['middlename'] + ' ' + customer['lastname']
            else:
                name = customer['firstname'] + ' ' + customer['lastname']
        except Exception as e:
            name = customer['firstname'] + ' ' + customer['lastname']
        return name

    def send_document_claims(self, info_url):
        print(info_url)
        model_id = ''
        dob = ''
        dbn = ''
        customer_name = ''
        try:
            info_text = requests.get(info_url + '?api_key=' + self.api_key).text
            info_json = json.loads(info_text)
            model_id = info_json['cmn']['id']
            dob = self.get_dob(info_json['cmn']['customers_payer']['customer']['customer_dob'])
            dbn = info_json['cmn']['customers_payer']['member_number']
            customer_name = self.get_name(info_json['cmn']['customers_payer']['customer'])

        except Exception as e:
            print(e)
            self.update_cmn_status_failed(str(model_id))
            return False
        info = {
            'dbn': dbn,
            'dob': dob,
        }

        print(info)

        signed_cmn_links = []
        for doc in info_json['cmn']['documents']:
            if doc['type'] == 'Signed CMN':
                signed_cmn_links.append({'id': doc['id'], 'url': doc['s3_url']})
        if len(signed_cmn_links) == 0:
            logging.warning('The Signed CMN Not Exist!')
            self.update_cmn_status_failed(str(model_id))
            return False

        signed_cmn_paths = []
        for signed_cmn_link in signed_cmn_links:
            try:
                r = requests.get(signed_cmn_link['url']) 
                open(self.abs_path + "/" + 'east_tmp{}.pdf'.format(signed_cmn_link['id']), 'wb').write(r.content)
                signed_cmn_paths.append(self.abs_path + "/" + 'east_tmp{}.pdf'.format(signed_cmn_link['id']))
            except Exception as e:
                logging.warning("The s3 url doesn't exist")
                self.update_cmn_status_failed(str(model_id))
                print(e)
                return False
        try:
            os.remove(self.abs_path + "/" + 'east_cmn.pdf')
        except Exception as e:
            pass
        
        merger = PdfFileMerger(strict=False)
        try:
            for pdf in signed_cmn_paths:
                merger.append(PdfFileReader(pdf), 'rb')
        except Exception as e:
            print(e)
            self.update_cmn_status_failed(str(model_id))
            return False      

        with open(self.abs_path + "/" + 'east_cmn.pdf', "wb") as fout:
            merger.write(fout)
        for signed_cmn_path in signed_cmn_paths:
            try:
                os.remove(signed_cmn_path)
            except Exception as e:
                pass
        drive = self.drive
        drive.get(self.msg_url)
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)

        drive.find_element(By.ID, 'selCategories').click()
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)

        drive.find_element(By.XPATH, "//select/option[@value='Claims']").click()
        iwait = random.randint(1, 2) + random.random()
        time.sleep(iwait)

        drive.execute_script("document.getElementById('replyMessage').style.height = '250px';")

        msg_content = "Please see the attached certificate of medical necessity for the following member: \n\nName: {}\nMember Number: {}\nDOB: {}\n\nThis CMN is use to support claims for services provided by our DME.  The claims will be submitted in the next 4 Days."
        

        message_type_radio = drive.find_elements(By.CSS_SELECTOR, '#doctypechecklabel #docType')
        message_type_radio[1].click()

        drive.find_element(By.ID, 'replyMessage').send_keys(msg_content.format(customer_name, dbn, dob))
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)

        file_path = os.path.join(self.abs_path, "east_cmn.pdf")
        print(file_path)

        drive.find_element(By.ID, 'inputUpload1').send_keys(file_path)
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)

        drive.save_screenshot(self.abs_path + "/" + 'screenshot1.png')
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)
        drive.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        
        drive.find_element(By.ID, 'btnSendReply').click()

        iwait = random.randint(15, 20) + random.random()
        time.sleep(iwait)
        
        WebDriverWait(drive, 300).until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='folders']/li[@class='last']/a")))

        drive.find_element(By.XPATH, "//ul[@id='folders']/li[@class='last']/a").click()
        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)

        # sent_detail = drive.find_elements_by_xpath("//a[@href='#']")
        sent_details = drive.find_elements(By.CSS_SELECTOR, "div.messages.sent a.read")

        sent_details[0].click()
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)

        drive.save_screenshot(self.abs_path + "/" + 'screenshot2.png')
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)

        try:
            image1 = Image.open(self.abs_path + "/" + "screenshot1.png")
            im1 = image1.convert('RGB')
            image2 = Image.open(self.abs_path + "/" + "screenshot2.png")
            im2 = image2.convert('RGB')
        except Exception as e:
            logging.warning('screenshot error')

        pdf_path = self.abs_path + "/" + str(dbn) + '-' + str(dob.replace('/', '')) + '-' + time.strftime('%Y%m%d') + '.pdf'
        print(pdf_path)
        try:
            im1.save(pdf_path, save_all=True, append_images=[im2])
            payload1={'model': 'Cmns', 'model_id': str(model_id), 'type': 'Submission Confirmation'}
            pdf_fp = open(pdf_path,'rb')
            files1=[('file', open(pdf_path,'rb'))]
            response = requests.request("POST", self.url4attachtomodel, headers=self.headers, data=payload1, files=files1)
            print(response.text)
            pdf_fp.close()
            self.update_cmn_status_success(str(model_id))
        except Exception as e:
            print(e)
            logging.warning('pdf creating error')
            self.update_cmn_status_failed(str(model_id))
            return False
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)

        try:
            os.remove(self.abs_path + "/" + 'screenshot1.png')
        except Exception as e:
            pass
        try:
            os.remove(self.abs_path + "/" + 'screenshot2.png')
        except Exception as e:
            pass
        try:
            os.remove(self.abs_path + "/" + 'east_cmn.pdf')
        except Exception as e:
            pass
        try:
            os.remove(pdf_path)
        except Exception as e:
            pass
        return True
    
    def update_cmn_status_success(self, model_id):
        post_url = "http://dmez.us-east-1.elasticbeanstalk.com/api/cmns/edit/" + model_id + ".json?api_key=" + self.api_key
        payload={'id': model_id, 'status_id': '74'}
        files=[]
        response = requests.request("POST", post_url, headers=self.headers, data=payload, files=files)
    
    def update_cmn_status_failed(self, model_id):
        post_url = "http://dmez.us-east-1.elasticbeanstalk.com/api/cmns/edit/" + model_id + ".json?api_key=" + self.api_key
        payload={'id': model_id, 'status_id': '73'}
        files=[]
        response = requests.request("POST", post_url, headers=self.headers, data=payload, files=files)

with Bot() as scraper:
    scraper.browser_init()
    scraper.main()    