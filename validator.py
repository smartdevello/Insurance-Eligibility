import os
import requests
import logging
from PIL import Image
import json
import re

from tricare_west import Bot as triwest
from tricare_east import Bot as trieast
from mdwise import Bot as MDwise
from caresource_ohio import Bot as CareSource
from tricare_overseas import Bot as trioverseas
from buckeyehealthplan import Bot  as Buckeye
from medi_cal import Bot as Medi_cal

api_key = "2c00cd3434f14892b5372c24a9581946"
post_url = "http://dmez.us-east-1.elasticbeanstalk.com/api/customers-payers/verify.json?api_key={}".format(api_key)
#http://dmez.us-east-1.elasticbeanstalk.com/orders/getautoval.json
abs_path = os.path.abspath(os.path.dirname(__file__))
metabase_url = "http://metabase-izk7e-env.us-east-1.elasticbeanstalk.com/public/question/28f0fdde-3733-4881-87dc-94b78ed51c23.json"

#ip address 3.142.247.228
# 4682
def post_info_to_dmez(payload, pdf_path, tmp_img, img_names = []):

    print("================Payload before submit==============")
    print(payload)
    imgs = []
    for img_name in img_names:
        try:
            imgs.append(Image.open(abs_path + "/" + tmp_img + img_name).convert('RGB'))
        except Exception as e:
            pass
    if len(imgs) == 1:
        imgs[0].save(pdf_path, save_all=True, append_images=[])
    else: imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:])

    print('ready to submit pdf file')
    try:
        files = [('pdf', open(pdf_path, 'rb'))]
    except Exception as e:
        print('error while opening pdf file ' )
        print(pdf_path)
        print(e)
        files = [('pdf', None)]
        return
    
    headers = {'Cookie': 'CAKEPHP=3b653b4a5bce6ae92bd6d1ca71ca16d9'}
    response = requests.request("POST", post_url, headers=headers, data=payload, files=files)
    try:
        for fname in os.listdir(abs_path):
            if tmp_img in fname:
                print(fname)
                os.remove(abs_path + "/" + fname)
    except Exception as e:
        pass
    try:
        os.remove(pdf_path)
    except Exception as e:
        pass
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(response.text)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')


def post_tinfo_to_dmez(payload, pdf_path, tmp_img):
    path = abs_path + "/" + tmp_img + "te1.png"
    print('===================Image Path===================')
    print(path)
    print('==================================================')
    try:
        image1 = Image.open(abs_path + "/" + tmp_img + "te1.png")
        im1 = image1.convert('RGB')
        image2 = Image.open(abs_path + "/" + tmp_img + "te2.png")
        im2 = image2.convert('RGB')
    except Exception as e:
        logging.warning('screenshotte2.png error')
        print(e)
        pass
    try:
        image3 = Image.open(abs_path + "/" + tmp_img + "te3.png")
        im3 = image3.convert('RGB')
    except Exception as e:
        logging.warning('screenshotte3.png error')
        print(e)
        pass

    try:
        image4 = Image.open(abs_path + "/" + tmp_img + "tw0.png")
        im4 = image4.convert('RGB')
    except Exception as e:
        logging.warning('screenshottw0.png error')
        print(e)
        pass
    try:
        image5 = Image.open(abs_path + "/" + tmp_img + "tw1.png")
        im5 = image5.convert('RGB')
    except Exception as e:
        logging.warning('screenshottw1.png error')
        print(e)
        pass
    
    image6_flag = False
    try:
        image6 = Image.open(abs_path + "/" + tmp_img + "to0.png")
        image6_flag = True
        im6 = image6.convert('RGB')
    except Exception as e:
        logging.warning('screenshotto0.png error')
        print(e)
        pass


    try:
        if image6_flag:
            im1.save(pdf_path, save_all=True, append_images=[im2, im3, im4, im5, im6])
        else:
            im1.save(pdf_path, save_all=True, append_images=[im2, im3, im4, im5])
    except Exception as e:
        logging.warning('screenshotto6.png error')
        print(e)
        try:
            if image6_flag:
                im1.save(pdf_path, save_all=True, append_images=[im2, im4, im5, im6])
            else:
                im1.save(pdf_path, save_all=True, append_images=[im2, im4, im5])
        except Exception as e1:
            logging.warning(e1)
            print(e1)

    print('ready to submit pdf file')
    try:
        files = [('pdf', open(pdf_path, 'rb'))]
    except Exception as e:
        print('error while opening pdf file ' )
        print(pdf_path)
        print(e)
        files = [('pdf', None)]
        return
    
    headers = {'Cookie': 'CAKEPHP=3b653b4a5bce6ae92bd6d1ca71ca16d9'}
    response = requests.request("POST", post_url, headers=headers, data=payload, files=files)
    try:
        for fname in os.listdir(abs_path):
            if tmp_img in fname:
                print(fname)
                os.remove(abs_path + "/" + fname)
    except Exception as e:
        pass
    try:
        os.remove(pdf_path)
    except Exception as e:
        pass
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(response.text)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')


def get_metabase():
    metabase_json = requests.get(metabase_url).json()
    logging.warning("The metabase has {} patients info.".format(len(metabase_json)))
    return metabase_json


def conv_date(str_date):
    try:
        ary = str_date.split('/')
        return ary[2] + "-" + ary[0] + "-" + ary[1]
    except Exception as e:
        pass
    try:
        ary = re.split(' |, ', str_date)
        month_dict = {
            "Jan" : "01",
            "Feb" : "02",
            "Mar" : "03",
            "Apr" : "04",
            "May" : "05",
            "Jun" : "06",
            "Jul" : "07",
            "Aug" : "08",
            "Sep" : "09",
            "Oct" : "10",
            "Nov" : "11",
            "Dec" : "12",
        }
        if len(ary[1]) == 1:
            ary[1] = "0" + ary[1]
        return ary[2] + "-" + month_dict[ary[0]] + "-" + ary[1]        
    except Exception as e:
        pass
    return ""

def conv2float(price):
    try:
        tmp = price.replace("$", "").replace(",", "").replace("-", "0")
        f_price = float(tmp)
        return f_price
    except Exception as e:
        return float(0)
def checkKey(dic, key):
    if key in dic.keys():
        return True
    else:
        return False
def convertPayloadformat(c):
    try:
        c["effective_date"] = conv_date(c["effective_date"])
    except Exception as e:
        pass

    try:
        c["end_date"] = conv_date(c["end_date"])   
    except Exception as e:
        pass

    
    try:
        c["date_of_birth"] = conv_date(c["date_of_birth"])
    except Exception as e:
        c["date_of_birth"] = ""
        pass
        
    try:
        for i in range(len(c["coverage_history"])):
            if c["coverage_history"][i]["start_date"] !="": c["coverage_history"][i]["start_date"] = conv_date(c["coverage_history"][i]["start_date"])
            if c["coverage_history"][i]["end_date"] !="":  c["coverage_history"][i]["end_date"] = conv_date(c["coverage_history"][i]["end_date"])
    except Exception as e:
        c["coverage_history"] = ""
        pass
    c["coverage_history"] = json.dumps(c["coverage_history"])

    if checkKey(c, "network_individual_deductible_met"): c["network_individual_deductible_met"] = conv2float(c["network_individual_deductible_met"])
    if checkKey(c, "network_individual_deductible_max"): c["network_individual_deductible_max"] = conv2float(c["network_individual_deductible_max"])
    if checkKey(c, "network_family_deductible_met")    : c["network_family_deductible_met"] = conv2float(c["network_family_deductible_met"])
    if checkKey(c, "network_family_deductible_max"):    c["network_family_deductible_max"] = conv2float(c["network_family_deductible_max"])
    if checkKey(c, "non_network_individual_deductible_met"): c["non_network_individual_deductible_met"] = conv2float(c["non_network_individual_deductible_met"])
    if checkKey(c, "non_network_individual_deductible_max"): c["non_network_individual_deductible_max"] = conv2float(c["non_network_individual_deductible_max"])
    if checkKey(c, "non_network_family_deductible_met"):     c["non_network_family_deductible_met"] = conv2float(c["non_network_family_deductible_met"])
    if checkKey(c, "non_network_family_deductible_max"):   c["non_network_family_deductible_max"] = conv2float(c["non_network_family_deductible_max"])
    if checkKey(c, "individual_catastrophic_cap_met") : c["individual_catastrophic_cap_met"] = conv2float(c["individual_catastrophic_cap_met"])
    if checkKey(c, "individual_catastrophic_cap_max"): c["individual_catastrophic_cap_max"] = conv2float(c["individual_catastrophic_cap_max"])
    if checkKey(c, "family_catastrophic_cap_met"):    c["family_catastrophic_cap_met"] = conv2float(c["family_catastrophic_cap_met"])
    if checkKey(c, "family_catastrophic_cap_max"):    c["family_catastrophic_cap_max"] = conv2float(c["family_catastrophic_cap_max"])
    return c
def return_checked_merged(merged, main, passive):
    for key in merged.keys():
        try:
            if merged[key] == '' or merged[key] == {} or merged[key] == []:
                merged[key] = main[key]
        except Exception as e:
            pass
        try:
            if merged[key] == '' or merged[key] == {} or merged[key] == []:
                merged[key] = passive[key]
        except Exception as e:
            pass
    return merged
# metabase_json = get_metabase()
# if ( isinstance(metabase_json, list)):
#     medicalfiltered = list(filter(lambda x: x['payer_id'] == 55, metabase_json))
#     if len(medicalfiltered) > 0:
#         with Medi_cal() as medi_calbot:
#             medi_calbot.browser_init()
#             for patient in medicalfiltered:
#                 if patient['member_number'] == '':
#                     continue
#                 try:
#                     final_payload = medi_calbot.check_validity(patient)
#                     payload = convertPayloadformat(final_payload["payload"])

#                     # print(c)
#                     post_info_to_dmez(payload, final_payload["pdf_path"], final_payload["img_tmp"], final_payload["img_names"])

#                 except Exception as e:
#                     print('Medi Cal !!! \n')
#                     print(e)
                # invalid member number

metabase_json = get_metabase()

if isinstance(metabase_json, list):
    mdwisefiltered = []
    mdwisefiltered = list(filter(lambda x: x['payer_id'] == 35, metabase_json))
    if len(mdwisefiltered) > 0:
        with MDwise() as mdwisebot:
            mdwisebot.browser_init()
            for patient in mdwisefiltered:
                try:
                    try:
                        if patient['member_number'] == '':
                            continue
                    except Exception as e:
                        continue
                    
                    final_payload = mdwisebot.check_validity(patient)
                    payload = convertPayloadformat(final_payload["payload"])

                    # print(c)
                    post_info_to_dmez(payload, final_payload["pdf_path"], final_payload["img_tmp"], final_payload["img_names"])
                except Exception as e:
                    print('Stopped MDWise !!! \n')
                    print(e)


if isinstance(metabase_json, list):
    buckeyefiltered = []
    buckeyefiltered = list(filter(lambda x: x['payer_id'] == 18, metabase_json))
    if len (buckeyefiltered) > 0:
        with Buckeye() as buckeyebot:
            buckeyebot.browser_init()
            for patient in buckeyefiltered:
                try:
                    try:
                        if patient['member_number'] == '':
                            continue
                    except Exception as e:
                        continue
                    
                    final_payload = buckeyebot.check_validity(patient)
                    payload = convertPayloadformat(final_payload["payload"])

                    # print(c)
                    post_info_to_dmez(payload, final_payload["pdf_path"], final_payload["img_tmp"], final_payload["img_names"])
                except Exception as e:
                    print('Stopped Buckeye !!! \n')
                    print(e)

if isinstance(metabase_json, list):
    caresource_filtered = list(filter(lambda x: x['payer_id'] == 56, metabase_json))

    if len(caresource_filtered) > 0:
        with CareSource() as caresourcebot:
            caresourcebot.browser_init()
            for patient in caresource_filtered:
                try:
                    try:
                        if patient['member_number'] == '':
                            continue
                    except Exception as e:
                        continue
                    
                    final_payload = caresourcebot.check_validity(patient)
                    payload = convertPayloadformat(final_payload["payload"])

                    post_info_to_dmez(payload, final_payload["pdf_path"], final_payload["img_tmp"], final_payload["img_names"])

                except Exception as e:
                    print('Stopped CareSource !!! \n')
                    print(e)


if isinstance(metabase_json, list):
    tricare_filtered = []
    for patient in metabase_json:
        if patient['payer_id'] not in [1, 2, 4]: continue
        if patient['member_number'] == None: continue    
        tricare_filtered.append(patient)
    if len(tricare_filtered) > 0:  
        with trieast() as eastbot:
            eastbot.browser_init()
            with triwest() as westbot:
                westbot.browser_init()
                for patient in tricare_filtered:      
                    try:
                        try:
                            for fname in os.listdir(abs_path):
                                if 'tmpimg_' in fname:
                                    print(fname)
                                    os.remove(abs_path + "/" + fname)
                        except Exception as e:
                            pass
                        try:
                            if patient['member_number'] == '':
                                continue
                        except Exception as e:
                            continue
                        

                        payload_east = eastbot.check_tricare_east(patient)
                        print(payload_east)
                        print('========east payload check done============')
                        
                        payload_west = westbot.check_tricare_west(patient)
                        print(payload_west)
                        print('========west payload done============')

                        
                        print('====================')              


                        c = {}
                        if patient['payer_id'] == 1:
                            overwrt = dict(payload_west["payload"], **payload_east["payload"])
                            c = return_checked_merged(overwrt, payload_east["payload"], payload_west["payload"])
                            x = 0
                            
                        elif patient['payer_id'] == 2:
                            overwrt  = dict(payload_east["payload"], **payload_west["payload"])
                            c = return_checked_merged(overwrt, payload_west["payload"], payload_east["payload"])
                            
                        elif patient['payer_id'] == 4:
                            with trioverseas() as overseasbot:
                                overseasbot.browser_init()                        
                                overseasbot.check_tricare_overseas(patient)
                            overwrt  = dict(payload_east["payload"], **payload_west["payload"])
                            c = return_checked_merged(overwrt, payload_west["payload"], payload_east["payload"])
                            print('=======overseasbot payload=============')

                        c = convertPayloadformat(c)

                        # print(c)
                        if c['eligibility_status'] == 'Unable to retrieve information':
                            print('Error: Tricare East Error!!!.')
                            continue
                        if c['parse_error'] == 1 and c['eligibility_status'] == '':
                            print('Error: PArse Error!!!.')
                            c['eligibility_status'] = 'No Patients Found'

                        post_info_to_dmez(c, payload_west["pdf_path"], payload_west["img_tmp"], ['te1.png', 'te2.png', 'te3.png', 'tw0.png', 'tw1.png', 'to0.png'])
                    except Exception as e:
                        print('Stopped !!! \n')
                        print(e)

