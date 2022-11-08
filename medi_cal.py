import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.action_chains import ActionChains 
from selenium. webdriver. common. keys import Keys
import time

import random
import logging
from datetime import datetime

class Bot:
    def __init__(self):

        self.login_url = "https://www.medi-cal.ca.gov/Common/Menu.aspx"
        self.search_url = "https://www.medi-cal.ca.gov/eligibility/Eligibility.aspx"
        self.username = '1932759131'
        self.pw = '0847343'

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

        # chrome_options.binary_location = "/usr/bin/google-chrome"
        # chrome_options.add_argument("--headless")
        # executable_path = "/home/ubuntu/.wdm/drivers/chromedriver/linux64/91.0.4472.101/chromedriver"

        executable_path = 'D:\My Work\Vijay\chromedriver.exe'
        print("=====executable path=======")

        drive = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)

        drive.get(self.login_url)
                
        # drive.set_window_size(1440, 1440)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        user_name = drive.find_element(By.ID, 'MainContent_txtUserID')
        user_name.send_keys(self.username)

        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        password = drive.find_element(By.ID, 'MainContent_txtPassword')
        password.clear()
        password.send_keys(self.pw)
        iwait = random.randint(3, 4) + random.random()
        time.sleep(iwait)
        login_button = drive.find_element(By.ID, 'MainContent_btnSubmit')
        
        # login_button.click()
        drive.execute_script("arguments[0].click();", login_button)
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)

        self.drive = drive
        drive.save_screenshot(self.abs_path + "/login_medi_cal.png")


    def get_metabase(self):
        metabase_json = requests.get(self.metabase_url).json()
        logging.warning("The metabase has {} patients info.".format(len(metabase_json)))
        return metabase_json
    
    def get_dob(self, customer_dob):
        dob = ""
        tmp = customer_dob.split('T')[0].split('-')
        dob = tmp[1]  + tmp[2]  + tmp[0]
        return dob

    def check_validity(self, patient):
        print("====Starting Mei Cal check=================")
        drive = self.drive
        drive.get(self.search_url)
        iwait = random.randint(7, 10) + random.random()
        time.sleep(iwait)
        payload = {}
        patient_dob = self.get_dob(patient['customer_dob'])
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')

        payload['customers_payers_id'] = patient['customers_payers_id']
        payload['order_id'] = patient['order_id']
        payload['parse_error'] = 0

        try:
            member_number = drive.find_element(By.ID, "MainContent_RecipID")            
            member_number.clear()
            member_number.send_keys(patient['member_number'])

            member_dob = drive.find_element(By.ID, "MainContent_RecipDOB")
           
            member_dob.clear()

            ActionChains(drive).move_to_element(member_dob).click().send_keys(Keys.LEFT).send_keys(Keys.LEFT).send_keys(patient_dob).perform()

            current_date = datetime.today().strftime('%m%d%Y')
            member_issue_date = drive.find_element(By.ID, "MainContent_RecipDOI")
            member_issue_date.clear()
            ActionChains(drive).move_to_element(member_issue_date).click().send_keys(Keys.LEFT).send_keys(Keys.LEFT).send_keys(current_date).perform()


            member_service_date = drive.find_element(By.ID, "MainContent_RecipDOS")
            member_service_date.clear()
            ActionChains(drive).move_to_element(member_service_date).click().send_keys(Keys.LEFT).send_keys(Keys.LEFT).send_keys(current_date).send_keys(Keys.ESCAPE).perform()


            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            drive.find_element(By.ID, "MainContent_Submit").click()

            iwait = random.randint(3, 5) + random.random()
            time.sleep(iwait)

            error_div = drive.find_element(By.CLASS_NAME, 'error-alert-dv')

            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'md_cal1.png')
            if flag == False:
                print('================faield to save screenshot md_cal1.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'md_cal1.png========================')

            if error_div is not None:                
                payload["eligibility_status"] = "Ineligible"
                payload["plan"] = "No Plan,Not Found"
                self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
                final_payload = {
                    'payload': payload,
                    'pdf_path': self.pdf_path,
                    'img_tmp': img_tmp,
                    'img_names' : [ 'md_cal1.png']
                }

                return final_payload

        except Exception as e:
            return None
            x =0 

        final_payload = {
            'payload': payload,
            'pdf_path': self.pdf_path,
            'img_tmp': img_tmp,
            'img_names' : [ 'md_cal1.png']
        }
        return final_payload
            # for i in range(0, 10):
            #     dob_element.send_keys(Keys.BACK_SPACE)


        # except Exception as e:
        #     drive.refresh
        #     iwait = random.randint(3, 5) + random.random()
        #     time.sleep(iwait)
        #     drive.get(self.search_url)
        #     iwait = random.randint(12, 15) + random.random()
        #     time.sleep(iwait)
        #     patient_dob = self.get_dob(patient['customer_dob'])

        #     tricate_id = drive.find_element(By.ID, "txtTricareID1")
        #     tricate_id.clear()
        #     tricate_id.send_keys(patient['member_number'])

        # tricate_dob = drive.find_element(By.ID, "txtDateOfBirth1")
        
        # tricate_dob.clear()        
        # tricate_dob.send_keys(patient_dob)

        # payload['customers_payers_id'] = patient['customers_payers_id']
        # payload['order_id'] = patient['order_id']

        # try:            
        #     drive.find_element(By.ID, "viewBeneficiaryProfileLink").click()
        #     iwait = random.randint(5, 8) + random.random()
        #     time.sleep(iwait)

        #     try:
        #         obj = drive.switch_to.alert
        #         message=obj.text
        #         print ("Alert shows following message: "+ message )
        #         obj.accept()
        #         iwait = random.randint(5, 8) + random.random()
        #         time.sleep(iwait)
        #     except Exception as e:
        #         pass

        #     drive.execute_script("window.scrollTo(0, 100)")
        #     iwait = random.randint(10, 15) + random.random()
        #     time.sleep(iwait)

        #     try:
        #         patient_info_view = requests.get("http://dmez.us-east-1.elasticbeanstalk.com/api/customers-payers/view/{}.json?api_key={}".format(patient['customers_payers_id'], self.api_key)).json()
                
        #         patient_first_name = patient_info_view["customersPayer"]["customer"]["firstname"]
        #         patient_last_name = patient_info_view["customersPayer"]["customer"]["lastname"]
        #         print(patient_first_name)
        #         print(patient_last_name)
        #         patient_links = drive.find_elements(By.XPATH, "//div[@id='divPatientList']/div[@class='k-grid-content']/table/tbody/tr/td/a")
        #         for patient_link in patient_links:
        #             print(patient_link.text)
        #             if (patient_first_name in patient_link.text) or (patient_last_name in patient_link.text):
        #                 action = ActionChains(drive) 
        #                 action.click(on_element = patient_link) 
        #                 action.perform()
        #                 iwait = random.randint(15, 18) + random.random()
        #                 time.sleep(iwait)
        #                 break

        #     except Exception as e:
        #         logging.warning('impossible to find patient lists.')
        #         logging.warning(e)

        #     flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'te1.png')
        #     if flag == False:
        #         print('================faield to save screenshot te1.png========================')
        #     else:
        #         print('================saved screenshot ' + img_tmp + 'te1.png========================')
                
        #     iwait = random.randint(10, 15) + random.random()
        #     time.sleep(iwait)
        #     drive.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
        #     flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'te2.png')
        #     if flag == False:
        #         print('================faield to save screenshot te2.png========================')
        #     else:
        #         print('================saved screenshot ' + img_tmp + 'te2.png========================')
                
        #     iwait = random.randint(10, 15) + random.random()
        #     time.sleep(iwait)
        #     patient_info = drive.find_element(By.ID, "patientInfoData").text.split('\n')
        #     try:
        #         payload["eligibility_status"] = drive.find_element(By.XPATH, "//label[@for='PatientInfo_EligibilityStatus']/parent::div/following::div[@class='patientInfoDataRight']").text
        #     except Exception as e:
        #         payload["eligibility_status"] = ""
        #     payload['plan'] = ""
        #     payload['beneficiary_name'] = patient_info[2]
        #     payload['patient_address'] = patient_info[3]
        #     payload['relationship'] = ""
        #     try:
        #         payload["date_of_birth"] = drive.find_element(By.XPATH, "//label[@for='PatientInfo_DateOfBirth']/parent::div/following::div[@class='patientInfoDataRight']").text
        #     except Exception as e:
        #         payload["date_of_birth"] = ""
        #     try:
        #         payload["sponsor_name"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_SponsorName']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["sponsor_name"] = ""
        #     try:
        #         payload["sponsor_status"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_Status']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["sponsor_status"] = ""
        #     try:
        #         payload["sponsor_branch"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_Branch']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["sponsor_branch"] = ""
        #     try:
        #         payload["sponsor_rank"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_RankAndGrade']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["sponsor_rank"] = ""
        #     try:
        #         payload["military_base"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_MilitaryBase']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["military_base"] = ""
        #     try:
        #         payload["region"] = drive.find_element(By.XPATH, "//label[@for='SponsorInfo_Region']/parent::div/following::div[@class='sponsorInfoDataRight']").text
        #     except Exception as e:
        #         payload["region"] = ""
        #     effective = drive.find_element(By.ID, "fiscalDate").text.split('(')[-1].split(')')[0].split(' - ')
        #     payload['effective_date'] = effective[0]
        #     payload['end_date'] = effective[1]

        #     try:
        #         pos = drive.find_element(By.ID, "planYearAmountsPerPlanType").text.split('\n')
        #         payload['network_individual_deductible_met'] = pos[2].split(' ')[1]
        #         payload['network_individual_deductible_max'] = pos[2].split(' ')[2]
        #         payload['network_family_deductible_met'] = pos[3].split(' ')[1]
        #         payload['network_family_deductible_max'] = pos[3].split(' ')[2]
        #     except Exception as e:
        #         payload['network_individual_deductible_met'] = ""
        #         payload['network_individual_deductible_max'] = ""
        #         payload['network_family_deductible_met'] = ""
        #         payload['network_family_deductible_max'] = ""
        #     payload['non_network_individual_deductible_met'] = ""
        #     payload['non_network_individual_deductible_max'] = ""
        #     payload['non_network_family_deductible_met'] = ""
        #     payload['non_network_family_deductible_max'] = ""

        #     try:
        #         catastrophic = drive.find_element(By.ID, "planYearAmountsCap").text.split('\n')
        #         payload['individual_catastrophic_cap_met'] = catastrophic[2].split(' ')[1]
        #         payload['individual_catastrophic_cap_max'] = catastrophic[2].split(' ')[2]
        #         payload['family_catastrophic_cap_met'] = catastrophic[3].split(' ')[1]
        #         payload['family_catastrophic_cap_max'] = catastrophic[3].split(' ')[2]
        #     except Exception as e:
        #         payload['individual_catastrophic_cap_met'] = ""
        #         payload['individual_catastrophic_cap_max'] = ""
        #         payload['family_catastrophic_cap_met'] = ""
        #         payload['family_catastrophic_cap_max'] = ""
        #     payload['parse_error'] = 0

        #     try:
        #         drive.find_element(By.ID, "tricareRegionMap1").click()
        #         iwait = random.randint(10, 15) + random.random()
        #         time.sleep(iwait)
                
        #         flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'te3.png')
        #         if flag == False:
        #             print('==============faield to save screenshot te3.png==================')
        #         else:
        #             print('================saved screenshot ' + img_tmp + 'te3.png========================')
                    
        #         iwait = random.randint(2, 3) + random.random()
        #         time.sleep(iwait)
        #         ohi_obj_list = drive.find_elements(By.XPATH, "//div[@id='divOHI']/div[@class='k-grid-content']/table/tbody/tr/td")
        #         ohi = []
        #         print(len(ohi_obj_list))
        #         for ohi_obj in ohi_obj_list:
        #             ohi.append(ohi_obj.text)

        #         print(ohi)
        #         payload['other_health_insurance'] = {
        #             'insurance_type': str(ohi[0]), 
        #             'effective_date': str(ohi[1]),
        #             'end_date': str(ohi[2]),
        #             'coverage_type': str(ohi[3]),
        #             'carrier_name': str(ohi[4]),
        #             'policy_id': str(ohi[5])}
        #     except Exception as e:
        #         payload['other_health_insurance'] = {}

        #     payload['coverage_history'] = []
        #     try:
        #         coverages = drive.find_elements(By.XPATH, "//div[@id='divCoverageHistory']/div/table/tbody/tr/td")
        #         ran_max = len(coverages) / 5
        #         idx = 0
        #         for i in range(int(ran_max)):
        #             cov = {}
        #             cov["status"] = coverages[idx].text
        #             cov["plan"] = coverages[idx + 1].text
        #             cov["start_date"] = coverages[idx + 2].text
        #             cov["end_date"] = coverages[idx + 3].text
        #             cov["end_reason"] = coverages[idx + 4].text
        #             payload['coverage_history'].append(cov)
        #             idx = idx + 5
        #     except Exception as e:
        #         print(e)
        #         logging.warning('error in coverage history parsing')
        #     self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
        # except Exception as e:
        #     payload['parse_error'] = 1
        # final_payload = {'payload': payload,
        #                  'pdf_path': self.pdf_path,
        #                  'img_tmp': img_tmp}



# with Bot() as scraper:
#     scraper.browser_init()
#     scraper.main()