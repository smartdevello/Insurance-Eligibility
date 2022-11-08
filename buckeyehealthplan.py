import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time
import random
import logging
from PIL import Image


class Bot:
    def __init__(self):
        self.url = "https://provider.buckeyehealthplan.com/careconnect/home?execution=e1s1"
        self.username = 'support@homefrontpumps.com'
        self.pw = '123HFPbsp!'
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
            
            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "identifierInput")))
            user_name = drive.find_element(By.ID, 'identifierInput')
           
            user_name.send_keys(self.username)
            time.sleep(2)
            drive.find_element(By.ID, 'postButton').click()
            time.sleep(2)

            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "password")))
            password = drive.find_element(By.ID, 'password')

            password.send_keys(self.pw)
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            drive.find_element(By.ID, 'signOnButtonSpan').click()
            time.sleep(2)
            select_plans = drive.find_element(By.ID, 'providerProfileName')

            Select(select_plans).select_by_index(0)           
            
            time.sleep(2)
            drive.find_element(By.ID, 'medicalDropdownSubmitID').click()
            time.sleep(5)
            drive.set_window_size(1440, 1440)
            self.drive = drive
            drive.save_screenshot(self.abs_path + "/login_buckeye.png")

            
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
        drive.get("https://provider.buckeyehealthplan.com/careconnect/home?execution=e2s1")
        time.sleep(5)

        payload = {}
        patient_dob = self.get_dob(patient['customer_dob'])

            
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')

        payload['customers_payers_id'] = patient['customers_payers_id']
        payload['order_id'] = patient['order_id']
        payload['parse_error'] = 0
        try:
            DBN_input = drive.find_element(By.NAME, 'memberIdOrLastName')
            DBN_input.clear()
            DBN_input.send_keys(patient['member_number'])
            time.sleep(2)

            dob_input = drive.find_element(By.NAME, 'dob')
            dob_input.clear()
            dob_input.send_keys(patient_dob)
            time.sleep(2)
            drive.find_element(By.NAME, 'submit').click()

            iwait = random.randint(5, 8) + random.random()
            time.sleep(iwait)

            message = ''
            try:
                message = drive.find_element(By.CLASS_NAME, 'errorMessage').text
            except Exception as errorMessage:
                pass

            drive.execute_script("window.scrollTo(0, 250)")
            time.sleep(2)

            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'buckeye1.png')
            if flag == False:
                print('================faield to save screenshot buckeye1.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'buckeye1.png========================')

            if "No Patients" in message:
                logging.warning('Customer search failed, not found')
                payload["eligibility_status"] = "Ineligible"
                payload["plan"] = "No Plan,Not Found"
                self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
                # print(payload)
                final_payload = {
                    'payload': payload,
                    'pdf_path': self.pdf_path,
                    'img_tmp': img_tmp,
                    'img_names' : [ 'buckeye1.png']
                }
                return final_payload

            OHI = {}            
            payload['other_health_insurance'] = OHI

            # get patient link
            # payload["eligibility_status"] = drive.find_element(By.CSS_SELECTOR, 'div.alert.alert-success').text
            payload["eligibility_status"] = "eligible"
            payload["beneficiary_name"] = drive.find_element(By.CSS_SELECTOR, 'div.patient_info div.info-horizontal:nth-child(1) span').text
            payload["gender"]  = "Female" if drive.find_element(By.CSS_SELECTOR, 'div.patient_info div.info-horizontal:nth-child(2) span').text == "F" else "Male"
            payload["date_of_birth"]  = drive.find_element(By.CSS_SELECTOR, 'div.patient_info div.info-horizontal:nth-child(3) span').text
            payload["patient_address"] = drive.find_element(By.CSS_SELECTOR, 'div.patient_info div.info-horizontal:nth-child(6) span').text
            payload["primary_care_manager_name"] = drive.find_element(By.CSS_SELECTOR, 'div#pcpInformationDiv div.info-horizontal:nth-child(1) span').text

            try:
                drive.find_element(By.ID, 'toggleEligHistButton').click()
                time.sleep(2)
            except:
                pass
            table = drive.find_element(By.ID, 'eligHistTable')

            trs = table.find_elements(By.CSS_SELECTOR, '#eligHistTable tr[class^="eligHist"]')
            coverage_history = []
            for tr in trs:
                coverage_history.append({
                    "status" : "",
                    "start_date" : tr.find_element(By.CSS_SELECTOR, 'td:nth-child(1)').text,
                    "end_date" : tr.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text,
                    "plan" : tr.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text,
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
            'img_names' : [ 'buckeye1.png']
        }

        return final_payload
        
    

# with Bot() as scraper:
#     scraper.browser_init()
#     scraper.main()