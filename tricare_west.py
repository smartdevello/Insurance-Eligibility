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
import random
import logging
from PIL import Image


class Bot:
    def __init__(self):
        self.url = "https://www.tricare-west.com/idp/prov-login.fcc"
        self.username = 'homefrontpumpsw1'
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
            
            chrome_options.binary_location = "/usr/bin/google-chrome" 
            chrome_options.add_argument("--headless")
            executable_path = "/home/ubuntu/.wdm/drivers/chromedriver/linux64/91.0.4472.101/chromedriver"
            
            # executable_path = 'D:\My Work\Vijay\chromedriver.exe'

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
            login_button = drive.find_element(By.ID, 'signOnButton').click()
            iwait = random.randint(4, 5) + random.random()
            time.sleep(iwait)
            self.drive = drive
            drive.save_screenshot(self.abs_path + "/login_tricare_west.png")
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


    def check_tricare_west(self, patient):
        print(patient)
        drive = self.drive
        payload = {}
        patient_dob = self.get_dob(patient['customer_dob'])
        tmp = ''
        if patient['member_number'][-1] == '0' and patient['member_number'][-2] == '0':
            tmp = patient['member_number'][:-1] + '1'
        print(tmp)
        img_tmp = 'tmpimg_' + str(patient['customers_payers_id']) + '-' + str(patient['order_id']) + '-' + time.strftime('%Y%m%d')
        url = "https://www.tricare-west.com/content/hnfs/home/tw/prov/secure/app-forms/ohi/search-ohi.html"
        drive.get(url)
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)

        try:
            # drive.find_element_by_xpath("//a[@title='Click to close.']").click()
            drive.find_element(By.ID, 'acsFocusFirst').click()
            iwait = random.randint(5, 8) + random.random()
            time.sleep(iwait)
        except Exception as e:
            pass
        print(drive.current_url)
        drive.save_screenshot('searchUserOHIDBN.png')
        DBN_checkbox = drive.find_element(By.ID, 'searchUserOHIDBN').click()

        DBN_input = drive.find_element(By.ID, 'patientDBN')
        DBN_input.clear()
        DBN_input.send_keys(patient['member_number'])

        DOB_date = drive.find_element(By.ID, 'dbnPatientDOBText')
        DOB_date.clear()
        DOB_date.send_keys(patient_dob)

        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)
        search_button = drive.find_elements(By.XPATH, "//form[@id='formSearchUserOHIDBN']/div/button")[0].click()
        iwait = random.randint(2, 3) + random.random()
        time.sleep(iwait)

        OHI = {}
        try:
            view_button = drive.find_element(By.ID, 'views').click()
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            OHI['policyHolderName'] = drive.find_element(By.ID, 'policyHolderName').text
            OHI['ohiInsuranceType'] = drive.find_element(By.ID, 'ohiInsuranceType').text
            OHI['insuranceName'] = drive.find_element(By.ID, 'insuranceName').text
            OHI['relationshipToPolicyHolder'] = drive.find_element(By.ID, 'relationshipToPolicyHolder').text
            OHI['effectiveDate1'] = drive.find_element(By.ID, 'effectiveDate1').text
            OHI['endDate1'] = drive.find_element(By.ID, 'endDate1').text
            OHI['policyNumber'] = drive.find_element(By.ID, 'policyNumber').text
            OHI['drugCoverage'] = drive.find_element(By.ID, 'drugCoverage').text
            OHI['hmoppo'] = drive.find_element(By.ID, 'hmoppo').text
            print(OHI)
            print('success in step 1')
        except Exception as e:
            try:
                if tmp is not '':
                    drive.get(url)
                    iwait = random.randint(2, 3) + random.random()
                    time.sleep(iwait)

                    try:                        
                        drive.find_element(By.ID, 'acsFocusFirst').click()
                        iwait = random.randint(5, 8) + random.random()
                        time.sleep(iwait)
                    except Exception as e:
                        pass
                    drive.find_element(By.ID, 'searchUserOHIDBN').click()

                    drive.find_element(By.ID, 'patientDBN').clear()
                    drive.find_element(By.ID, 'patientDBN').send_keys(tmp)

                    drive.find_element(By.ID, 'dbnPatientDOBText').clear()
                    drive.find_element(By.ID, 'dbnPatientDOBText').send_keys(patient_dob)

                    drive.find_elements(By.XPATH, "//form[@id='formSearchUserOHIDBN']/div/button")[0].click()
                    iwait = random.randint(2, 3) + random.random()
                    time.sleep(iwait)
                    try:
                        drive.find_element(By.ID, 'views').click()
                        iwait = random.randint(2, 3) + random.random()
                        time.sleep(iwait)
                        OHI['policyHolderName'] = drive.find_element(By.ID, 'policyHolderName').text
                        OHI['ohiInsuranceType'] = drive.find_element(By.ID, 'ohiInsuranceType').text
                        OHI['insuranceName'] = drive.find_element(By.ID, 'insuranceName').text
                        OHI['relationshipToPolicyHolder'] = drive.find_element(By.ID, 'relationshipToPolicyHolder').text
                        OHI['effectiveDate1'] = drive.find_element(By.ID, 'effectiveDate1').text
                        OHI['endDate1'] = drive.find_element(By.ID, 'endDate1').text
                        OHI['policyNumber'] = drive.find_element(By.ID, 'policyNumber').text
                        OHI['drugCoverage'] = drive.find_element(By.ID, 'drugCoverage').text
                        OHI['hmoppo'] = drive.find_element(By.ID, 'hmoppo').text
                        print(OHI)
                        print('success in step 1-1')
                    except Exception as e:
                        pass
            except Exception as e1:
                pass

        drive.set_window_size(1440, 1440)
        iwait = random.randint(10, 15) + random.random()
        time.sleep(iwait)
        flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'tw0.png')
        if flag == False:
            print('================faield to save screenshot tw0.png========================')
        else:
            print('================saved screenshot ' + img_tmp + 'tw0.png========================')
            
        payload['other_health_insurance'] = OHI

        url = "https://www.tricare-west.com/content/hnfs/home/tw/prov/secure/app-forms/check-eligibility.html"
        drive.get(url)
        iwait = random.randint(5, 8) + random.random()
        time.sleep(iwait)
        try:
            # drive.find_element_by_xpath("//a[@title='Click to close.']").click()
            drive.find_element(By.ID, 'acsFocusFirst').click()
            iwait = random.randint(5, 8) + random.random()
            time.sleep(iwait)
        except Exception as e:
            pass

        DBN_checkbox = drive.find_element(By.ID, 'HNFSCheckEligibilityDBNid').click()

        DBN_input = drive.find_element(By.ID, 'dbnid1')
        DBN_input.clear()
        DBN_input.send_keys(patient['member_number'])

        DOB_date = drive.find_element(By.ID, 'dobDBNDate1')
        DOB_date.clear()
        DOB_date.send_keys(patient_dob)

        search_button = drive.find_element(By.ID, 'dbnSearch').click()
        iwait = random.randint(4, 5) + random.random()
        time.sleep(iwait)
        try:
            drive.execute_script("window.scrollTo(0, 500)")
            iwait = random.randint(10, 15) + random.random()
            time.sleep(iwait)
            flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'tw1.png')
            if flag == False:
                print('================faield to save screenshot tw1.png========================')
            else:
                print('================saved screenshot ' + img_tmp + 'tw1.png========================')
                
            
            iwait = random.randint(2, 3) + random.random()
            time.sleep(iwait)
            
            payload['eligibility_status'] = drive.find_element(By.ID, 'provDbnStatus').text
            payload['plan'] = drive.find_element(By.ID, 'provDbnPlan').text
            payload['beneficiary_name'] = drive.find_element(By.ID, 'provDbnHeading').text
            payload['relationship'] = drive.find_element(By.ID, 'provDbnRelationship').text
            payload['region'] = drive.find_element(By.ID, 'provDbnRegionType').text
            payload['effective_date'] = drive.find_element(By.ID, 'provDbnSecEffDate').text
            payload['end_date'] = drive.find_element(By.ID, 'provDbnSecEndDate').text
            payload['customers_payers_id'] = patient['customers_payers_id']
            payload['order_id'] = patient['order_id']
            payload['group_name'] = drive.find_element(By.ID, 'provDbnGroup').text
            payload['sponsor_benefit_type'] = drive.find_element(By.ID, 'provDbnSponsorType').text
            payload['gender'] = drive.find_element(By.ID, 'provDbnGender').text
            payload['primary_care_manager_name'] = drive.find_element(By.ID, 'provDbnManager').text
            payload['primary_care_manager_number'] = drive.find_element(By.ID, 'provDbnManagerPhone').text
            payload['secondary_plan'] = drive.find_element(By.ID, 'provDbnSecPlan').text
            payload['plan_year'] = drive.find_element(By.ID, 'provDbnFiscalYear').text
            payload['network_individual_deductible_met'] = drive.find_element(By.ID, 'provDbnIndDed').text.split(' / ')[0].replace('$', '')
            payload['network_individual_deductible_max'] = drive.find_element(By.ID, 'provDbnIndDed').text.split(' / ')[-1].replace('$', '')
            payload['network_family_deductible_met'] = drive.find_element(By.ID, 'provDbnFamDed').text.split(' / ')[0].replace('$', '')
            payload['network_family_deductible_max'] = drive.find_element(By.ID, 'provDbnFamDed').text.split(' / ')[-1].replace('$', '')
            payload['non_network_individual_deductible_met'] = drive.find_element(By.ID, 'provDbnIndDedNon').text.split(' / ')[0].replace('$', '')
            payload['non_network_individual_deductible_max'] = drive.find_element(By.ID, 'provDbnIndDedNon').text.split(' / ')[-1].replace('$', '')
            payload['non_network_family_deductible_met'] = drive.find_element(By.ID, 'provDbnFamDedNon').text.split(' / ')[0].replace('$', '')
            payload['non_network_family_deductible_max'] = drive.find_element(By.ID, 'provDbnFamDedNon').text.split(' / ')[-1].replace('$', '')
            payload['individual_catastrophic_cap_met'] = drive.find_element(By.ID, 'provDbnIndCatCap').text.split(' / ')[0].replace('$', '')
            payload['individual_catastrophic_cap_max'] = drive.find_element(By.ID, 'provDbnIndCatCap').text.split(' / ')[-1].replace('$', '')
            payload['family_catastrophic_cap_met'] = drive.find_element(By.ID, 'provDbnFamCatCap').text.split(' / ')[0].replace('$', '')
            payload['family_catastrophic_cap_max'] = drive.find_element(By.ID, 'provDbnFamCatCap').text.split(' / ')[-1].replace('$', '')
            payload['parse_error'] = 0
            
            print('success in step 2')
        except Exception as e:
            if tmp is not '':
                drive.get(url)
                iwait = random.randint(2, 3) + random.random()
                time.sleep(iwait)

                drive.find_element(By.ID, 'HNFSCheckEligibilityDBNid').click()

                drive.find_element(By.ID, 'dbnid1').clear()
                drive.find_element(By.ID, 'dbnid1').send_keys(tmp)

                drive.find_element(By.ID, 'dobDBNDate1').clear()
                drive.find_element(By.ID, 'dobDBNDate1').send_keys(patient_dob)

                drive.find_element(By.ID, 'dbnSearch').click()
                iwait = random.randint(4, 5) + random.random()
                time.sleep(iwait)
                try:
                    drive.execute_script("window.scrollTo(0, 500)")
                    iwait = random.randint(10, 15) + random.random()
                    time.sleep(iwait)
                    flag = drive.save_screenshot(self.abs_path + "/" + img_tmp + 'tw1.png')
                    if flag == False:
                        print('================faield to save screenshot tw1.png========================')
                    else:
                        print('================saved screenshot ' + img_tmp + 'tw1.png========================')
            
                    iwait = random.randint(2, 3) + random.random()
                    time.sleep(iwait)
                    
                    payload['eligibility_status'] = drive.find_element(By.ID, 'provDbnStatus').text
                    payload['plan'] = drive.find_element(By.ID, 'provDbnPlan').text
                    payload['beneficiary_name'] = drive.find_element(By.ID, 'provDbnHeading').text
                    payload['relationship'] = drive.find_element(By.ID, 'provDbnRelationship').text
                    payload['region'] = drive.find_element(By.ID, 'provDbnRegionType').text
                    payload['effective_date'] = drive.find_element(By.ID, 'provDbnSecEffDate').text
                    payload['end_date'] = drive.find_element(By.ID, 'provDbnSecEndDate').text
                    payload['customers_payers_id'] = patient['customers_payers_id']
                    payload['order_id'] = patient['order_id']
                    payload['group_name'] = drive.find_element(By.ID, 'provDbnGroup').text
                    payload['sponsor_benefit_type'] = drive.find_element(By.ID, 'provDbnSponsorType').text
                    payload['gender'] = drive.find_element(By.ID, 'provDbnGender').text
                    payload['primary_care_manager_name'] = drive.find_element(By.ID, 'provDbnManager').text
                    payload['primary_care_manager_number'] = drive.find_element(By.ID, 'provDbnManagerPhone').text
                    payload['secondary_plan'] = drive.find_element(By.ID, 'provDbnSecPlan').text
                    payload['plan_year'] = drive.find_element(By.ID, 'provDbnFiscalYear').text
                    payload['network_individual_deductible_met'] = drive.find_element(By.ID, 'provDbnIndDed').text.split(' / ')[0].replace('$', '')
                    payload['network_individual_deductible_max'] = drive.find_element(By.ID, 'provDbnIndDed').text.split(' / ')[-1].replace('$', '')
                    payload['network_family_deductible_met'] = drive.find_element(By.ID, 'provDbnFamDed').text.split(' / ')[0].replace('$', '')
                    payload['network_family_deductible_max'] = drive.find_element(By.ID, 'provDbnFamDed').text.split(' / ')[-1].replace('$', '')
                    payload['non_network_individual_deductible_met'] = drive.find_element(By.ID, 'provDbnIndDedNon').text.split(' / ')[0].replace('$', '')
                    payload['non_network_individual_deductible_max'] = drive.find_element(By.ID, 'provDbnIndDedNon').text.split(' / ')[-1].replace('$', '')
                    payload['non_network_family_deductible_met'] = drive.find_element(By.ID, 'provDbnFamDedNon').text.split(' / ')[0].replace('$', '')
                    payload['non_network_family_deductible_max'] = drive.find_element(By.ID, 'provDbnFamDedNon').text.split(' / ')[-1].replace('$', '')
                    payload['individual_catastrophic_cap_met'] = drive.find_element(By.ID, 'provDbnIndCatCap').text.split(' / ')[0].replace('$', '')
                    payload['individual_catastrophic_cap_max'] = drive.find_element(By.ID, 'provDbnIndCatCap').text.split(' / ')[-1].replace('$', '')
                    payload['family_catastrophic_cap_met'] = drive.find_element(By.ID, 'provDbnFamCatCap').text.split(' / ')[0].replace('$', '')
                    payload['family_catastrophic_cap_max'] = drive.find_element(By.ID, 'provDbnFamCatCap').text.split(' / ')[-1].replace('$', '')
                    payload['parse_error'] = 0
                    
                    print('success in step 2-2')
                except Exception as e:
                    payload['parse_error'] = 1
                    pass
            # print(e)
            pass
        
        self.pdf_path = self.abs_path + "/" + str(payload['customers_payers_id']) + '-' + str(payload['order_id']) + '-' + time.strftime('%Y%m%d') + '.pdf'
        # print(payload)
        final_payload = {'payload': payload,
                         'pdf_path': self.pdf_path,
                         'img_tmp': img_tmp}

        return final_payload
    
    def check_other_not_serviced(self, patient):
        payload = {}
        return payload

    def post_info_to_dmez(self, payload):
        print(self.pdf_path)
        files=[('pdf', open(self.pdf_path,'rb'))]
        headers = {'Cookie': 'CAKEPHP=3b653b4a5bce6ae92bd6d1ca71ca16d9'}
        response = requests.request("POST", self.post_url, headers=headers, data=payload, files=files)
        try:
            os.remove(self.abs_path + "/" + 'screenshottw0.png')
        except Exception as e:
            pass
        try:
            os.remove(self.abs_path + "/" + 'screenshottw1.png')
        except Exception as e:
            pass
        try:
            os.remove(self.pdf_path)
        except Exception as e:
            pass
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.text)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++')

    def main(self):
        metabase_json = self.get_metabase()
        for patient in metabase_json:
            if patient['payer_id'] == 1:
                continue
                self.post_info_to_dmez(self.check_tricare_east(patient))
            elif patient['payer_id'] == 2:
                self.post_info_to_dmez(self.check_tricare_west(patient))
            elif patient['payer_id'] == 3:
                continue
                self.post_info_to_dmez(self.check_other_not_serviced(patient))


# with Bot() as scraper:
#     scraper.browser_init()
#     scraper.main()