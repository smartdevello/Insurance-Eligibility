import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import random
import logging
from PIL import Image


class Bot:
    def __init__(self):
        self.url = "https://secure.healthx.com/v3app/publicservice/loginv1/login.aspx?bc=b970749d-9da8-414c-a829-a290ab4bea1d&serviceid=0d390b88-4c5f-4144-84ed-eee85184d067"
        self.username = 'BSPMDWISE'
        self.pw = 'KiindeHFP123'
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
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--profile-directory=Default')
            
            # chrome_options.binary_location = "/usr/bin/google-chrome" 
            # chrome_options.add_argument("--headless")
            # executable_path = "/home/ubuntu/.wdm/drivers/chromedriver/linux64/91.0.4472.101/chromedriver"
            
            executable_path = 'D:\My Work\Vijay\chromedriver.exe'

            print("=====executable chrome path=====")
            print(executable_path)
            drive = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
            drive.get(self.url)
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            
            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "username")))
            user_name = drive.find_element(By.ID, 'username')
            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "password")))
            password = drive.find_element(By.ID, 'password')
            
            user_name.send_keys(self.username)
            password.send_keys(self.pw)
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            drive.find_element(By.ID, 'loginButton').click()
            iwait = random.randint(4, 5) + random.random()
            time.sleep(iwait)

            drive.find_element(By.CSS_SELECTOR, 'input[value="Accept"]').click()
            iwait = random.randint(4, 5) + random.random()
            time.sleep(iwait)

            drive.execute_script('document.getElementById("ctl00_MainContent_uxModalDialogPanel_Normal").scrollTo(0, 500);')            
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            drive.find_element(By.CSS_SELECTOR, 'input[value="I agree"]').click()
            iwait = random.randint(4, 5) + random.random()
            time.sleep(iwait)


            drive.find_elements(By.CSS_SELECTOR, '#hxUserMenu li.personaItem>a')[1].click()
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)

            self.drive = drive
            drive.save_screenshot(self.abs_path + "/login_mdwise.png")

            
        except  Exception as e:
            print(e)
            return
    
    def get_metabase(self):
        metabase_json = requests.get(self.metabase_url).json()
        logging.warning("The metabase has {} patients info.".format(len(metabase_json)))
        return metabase_json
    
    def get_dob(self, customer_dob):
        dob = ""
        tmp = customer_dob.split('T')[0].split('-')
        dob = tmp[1] + '/' + tmp[2] + '/' + tmp[0]
        return dob

    def check_tricare_east(self, patient):
        payload = {}
        return payload


    def check_validity(self, patient):        
        print(patient)
        drive = self.drive
        payload = {}
        patient_dob = self.get_dob(patient['customer_dob'])

        if len( patient['member_number'] ) == 11:
            patient['member_number'] = patient['member_number'] + '9'
        if len(patient['member_number']) !=12:
            logging.warning('This customer member number length is not 12')
            
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')

        payload['customers_payers_id'] = patient['customers_payers_id']
        payload['order_id'] = patient['order_id']
        payload['parse_error'] = 0
        try:
            DBN_input = drive.find_element(By.ID, 'ctl00_MainContent_uxEligControl_MemberIDInput')
            DBN_input.clear()
            DBN_input.send_keys(patient['member_number'])
            drive.find_element(By.ID, 'ctl00_MainContent_uxEligControl_uxSearch').click()
            iwait = random.randint(8, 10) + random.random()
            time.sleep(iwait)

            message = drive.find_element(By.ID, 'ctl00_MainContent_uxEligControl_uxMessageLabel').text
            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'mdwiese1.png')
            if flag == False:
                print('================faield to save screenshot mdwiese1.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'mdwiese1.png========================')

            if "record found" not in message:
                logging.warning('Customer search failed, not found')
                payload["eligibility_status"] = message
                payload["plan"] = "No Plan,Not Found"
                self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
                # print(payload)
                final_payload = {
                    'payload': payload,
                    'pdf_path': self.pdf_path,
                    'img_tmp': img_tmp,
                    'img_names' : [ 'mdwiese1.png']
                }
                return final_payload
            OHI = {}            
            payload['other_health_insurance'] = OHI

            # get patient link


            img_member_id = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(2)').text

            payload["date_of_birth"] = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(4)').text

            payload["effective_date"] = ""
            payload["end_date"] = ""
            payload["family_catastrophic_cap_max"] = ""
            payload["family_catastrophic_cap_met"] = ""
            payload["gender"] = "Female" if drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(5)').text == "F" else "Male"
            payload["group_name"] = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(3)').text
            # payload["individual_catastrophic_cap_max"] = ""
            # payload["individual_catastrophic_cap_met"] = ""
            payload["parse_error"] = 0


            img_benefit_plan = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(6)').text
            payload["patient_address"] = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(7)').text
            img_home_phone = drive.find_element(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row td:nth-child(8)').text




            time.sleep(10)
            links = drive.find_elements(By.CSS_SELECTOR, 'div.pagegrid_container tr.pagegrid_row a')
            links[0].click()
            
            iwait = random.randint(10, 15) + random.random()
            time.sleep(iwait)
            drive.execute_script("window.scrollTo(0, 250)")
            time.sleep(1)

            patient_info_view = requests.get("http://dmez.us-east-1.elasticbeanstalk.com/api/customers-payers/view/{}.json?api_key={}".format(patient['customers_payers_id'], self.api_key)).json()
            
            patient_first_name = patient_info_view["customersPayer"]["customer"]["firstname"]
            patient_last_name = patient_info_view["customersPayer"]["customer"]["lastname"]
            print(patient_first_name)
            print(patient_last_name)

            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'mdwiese2.png')
            if flag == False:
                print('================faield to save screenshot mdwiese2.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'mdwiese2.png========================')

            tables = drive.find_elements(By.CSS_SELECTOR, 'div.pageview_container table')            
            payload["beneficiary_name"] = tables[0].find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(1) td:nth-child(2)').text
            payload["group_name"] = tables[0].find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(1) td:nth-child(4)').text
            member_id  = tables[0].find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(2) td:nth-child(2)').text
            group_number  = tables[0].find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(2) td:nth-child(4)').text
            payload["eligibility_status"] = tables[0].find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(3) td:nth-child(2)').text


            trs = tables[1].find_elements(By.CSS_SELECTOR, 'tr')
            coverage_history = []
            for i in range(0, len(trs), 3):
                # sss = trs[i].text
                # effective_date = trs[i + 1].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
                # termination_date = trs[i + 1].find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
                # plan = trs[i + 2].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
                # hclass = trs[i + 2].find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
                if payload["effective_date"] == "":
                    payload["effective_date"] = trs[i + 1].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
                coverage_history.append({
                    "status" : "",
                    "plan" : trs[i + 2].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text,
                    "start_date" : trs[i + 1].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text,
                    "end_date" : trs[i + 1].find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text,
                    "end_reason" : ""
                })
            payload["coverage_history"] = coverage_history
        except Exception as e:
            print(e)
            return None
        
        self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
        # print(payload)
        final_payload = {
            'payload': payload,
            'pdf_path': self.pdf_path,
            'img_tmp': img_tmp,
            'img_names' : [ 'mdwiese1.png' , 'mdwiese2.png' ]
        }

        return final_payload
        
    

# with Bot() as scraper:
#     scraper.browser_init()
#     scraper.main()