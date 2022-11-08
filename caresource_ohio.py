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
        self.url = "https://providerportal.caresource.com/OH/Default.aspx"
        self.eligibility_url = "https://providerportal.caresource.com/OH/Member/Search/Eligibility.aspx"
        self.username = 'HfpBsp2022'
        self.pw = '4!UcXiM5imGXXTX'
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
            
            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_cphContent_cphContent_ctl00_lgnProviderLogin_UserName")))
            user_name = drive.find_element(By.ID, 'ctl00_ctl00_cphContent_cphContent_ctl00_lgnProviderLogin_UserName')
            WebDriverWait(drive, 60).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_cphContent_cphContent_ctl00_lgnProviderLogin_Password")))
            password = drive.find_element(By.ID, 'ctl00_ctl00_cphContent_cphContent_ctl00_lgnProviderLogin_Password')
            
            user_name.send_keys(self.username)
            password.send_keys(self.pw)
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            drive.find_element(By.ID, 'ctl00_ctl00_cphContent_cphContent_ctl00_lgnProviderLogin_LoginButton').click()
            iwait = random.randint(4, 5) + random.random()
            time.sleep(iwait)            
            drive.set_window_size(1440, 1440)
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

    def scroll_to_element(self, element):
        desired_y = (element.size['height'] / 2) + element.location['y']
        window_h = self.drive.execute_script('return window.innerHeight')
        window_y = self.drive.execute_script('return window.pageYOffset')
        current_y = (window_h / 2) + window_y
        scroll_y_by = desired_y - current_y

        self.drive.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)

    def check_validity(self, patient):        
        print(patient)
        drive = self.drive

        drive.get(self.eligibility_url)
        iwait = random.randint(6, 8) + random.random()
        time.sleep(iwait)

        try:
            btns = drive.find_elements(By.CSS_SELECTOR, "div.QSIWebResponsive-creative-container-fade>div button")
            btns[1].click()
            time.sleep(1)            
        except Exception as e:
            pass

        try:
            # Switch to Iframe
            WebDriverWait(drive, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="sbox-content"]/iframe')))
            drive.find_element(By.ID, "ctl00_ctl00_cphContent_cphContent_ctl00_cmdSecureVerify").click()
            time.sleep(1)          
            # switch to main content
            drive.switch_to.default_content()
        except Exception as e:
            print(e)
            pass


        drive.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        payload = {}
        patient_dob = self.get_dob(patient['customer_dob'])
            
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')

        payload['customers_payers_id'] = patient['customers_payers_id']
        payload['order_id'] = patient['order_id']
        payload['parse_error'] = 0
        self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
        try:
            DBN_input = drive.find_element(By.ID, 'ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_rwMemberId_txtMemberId')
            DBN_input.send_keys(patient['member_number'])
            drive.find_element(By.ID, 'ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_rwActions_ctl02_ctl00_btnSubmit').click()
            try:
                WebDriverWait(drive, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "dl#ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_csAccordion dt")))
            except Exception as e1:
                payload["eligibility_status"]  = "Ineligible"
                drive.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'caresource1.png')
                if flag == False:
                    print('================faield to save screenshot caresource1.png========================')
                else:
                    print('================saved screenshot ' + img_tmp + 'caresource1.png========================')
                
                final_payload = {
                    'payload': payload,
                    'pdf_path': self.pdf_path,
                    'img_tmp': img_tmp,
                    'img_names' : [ 'caresource1.png']
                }
                print("Not Found Patient")
                return final_payload


            dts = drive.find_elements(By.CSS_SELECTOR, "dl#ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_csAccordion dt")
            dds = drive.find_elements(By.CSS_SELECTOR, "dl#ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_csAccordion dd")

            content = dds[0].text
            print(content)
            member_details_divs = dds[0].find_elements(By.CSS_SELECTOR, "div#ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_fvMemberDetails_ctl01_pnlDetails>div.grid-data")

            tempdiv = member_details_divs[0].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["beneficiary_name"] = tempdiv[1].text
            payload["patient_address"] = tempdiv[3].text

            tempdiv = member_details_divs[1].find_elements(By.CSS_SELECTOR, "div.cell")
            caresoure_id = tempdiv[1].text
            country_of_residence = tempdiv[3].text

            tempdiv = member_details_divs[2].find_elements(By.CSS_SELECTOR, "div.cell")
            country_of_eligibility = tempdiv[3].text

            tempdiv = member_details_divs[3].find_elements(By.CSS_SELECTOR, "div.cell")
            medicaid = tempdiv[1].text
            phone = tempdiv[3].text

            tempdiv = member_details_divs[4].find_elements(By.CSS_SELECTOR, "div.cell")
            case_number = tempdiv[1].text
            payload["date_of_birth"]  = tempdiv[3].text

            tempdiv = member_details_divs[5].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["gender"] = tempdiv[1].text
            payload["relationship"]  = tempdiv[3].text

            tempdiv = member_details_divs[6].find_elements(By.CSS_SELECTOR, "div.cell")
            member_profile = tempdiv[1].text
            program_details = tempdiv[3].text

            tempdiv = member_details_divs[7].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["effective_date"] = tempdiv[1].text.split(' ')[0]
            payload["end_date"] = ""
            payload["eligibility_status"] = drive.find_element(By.ID, "ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_flash").text
            member_eligibility_date = tempdiv[3].text

            tempdiv = member_details_divs[8].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["plan"] = tempdiv[1].text

            provider_details_divs = dds[0].find_elements(By.CSS_SELECTOR, "div#ctl00_ctl00_cphContent_cphContent_ctl00_MemberId_ctl02_fvMemberDetails_ctl01_pnlProviderDetails>div.grid-data")
            tempdiv = provider_details_divs[0].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["primary_care_manager_name"] = tempdiv[1].text
            pcp_phone = tempdiv[3].text

            tempdiv = provider_details_divs[1].find_elements(By.CSS_SELECTOR, "div.cell")
            payload["primary_care_manager_number"] = tempdiv[1].text

            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'caresource1.png')
            if flag == False:
                print('================faield to save screenshot caresource1.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'caresource1.png========================')

            
            self.scroll_to_element(dts[-1])
            dts[-1].click()
            time.sleep(3)
            self.scroll_to_element(dds[-1])
            time.sleep(3)

            trs = dds[-1].find_elements(By.CSS_SELECTOR, "table tr")
            coverage_history = []
            for i in range(1, len(trs)):
                coverage_history.append({
                    "status" : "",
                    "start_date" : trs[i].find_element(By.CSS_SELECTOR, 'td:nth-child(1)').text,
                    "end_date" : trs[i].find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text,
                    "plan" : trs[i].find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text,
                    "end_reason" : ""
                })

            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'caresource2.png')
            if flag == False:
                print('================faield to save screenshot caresource2.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'caresource2.png========================')

            payload["coverage_history"] = coverage_history


        except Exception as e:
            print(e)
            return None        

        print("============================before return valid payload ===========================")
        final_payload = {
            'payload': payload,
            'pdf_path': self.pdf_path,
            'img_tmp': img_tmp,
            'img_names' : [ 'caresource1.png' , 'caresource2.png' ]
        }

        return final_payload
        
    

# with Bot() as scraper:
#     scraper.browser_init()
#     scraper.main()