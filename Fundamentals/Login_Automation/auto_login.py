from kiteconnect import KiteConnect
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os 
import time
from time import sleep 
from pyotp import TOTP
import base64
import binascii
from datetime import datetime
from urllib.parse import urlparse,parse_qs

folder_name = 'api_keys'


def get_curr_path(folder_name):
    curr_dir = os.getcwd()
    curr_path = os.path.join(curr_dir,folder_name)
    return curr_path

# curr_path = get_curr_path(curr_dir,folder_name)
# print(curr_path)

file_name = 'credentials.txt'

def get_credentials(curr_path,file_name):
    file_dir = os.path.join(curr_path,file_name)
    file = open(file_dir,'r').read().split()
    api_key = file[0]
    api_secret = file[1]
    user_name = file[2]
    pwd = file[3]
    totp_key = file[-1]
    return api_key,api_secret,user_name,pwd,totp_key

# api_key,api_secret,user_name,pwd,totp_key = get_credentials(curr_path,file_name='credentials.txt')
# print(api_key,api_secret,user_name,pwd,totp_key)

def auto_login(api_key,user_name,pwd,totp_key):
    kite = KiteConnect(api_key=api_key)
    service = Service(ChromeDriverManager().install())
    service.start()
    options = Options()
    #options.add_argument('--headless')
    options.to_capabilities()
    driver = webdriver.Remote(
        command_executor=service.service_url,
        options=options)
    driver.get(kite.login_url())
    driver.implicitly_wait(5)
    username = driver.find_element(By.XPATH, "//input[@type='text']")
    username.send_keys(user_name)
    # print(username)
    password = driver.find_element(By.XPATH, "//input[@type='password']")
    password.send_keys(pwd)
    # print(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    sleep(1)
    totp = driver.find_element(By.XPATH,"//input[@type='number']")
    totp_token = TOTP(totp_key)
    #print(totp_token)
    token = totp_token.now()
    # print(token)
    totp.send_keys(token)
    driver.find_element(By.XPATH,"//button[@type = 'submit']").click()
    sleep(1)
    current_url = driver.current_url
    # print(current_url)
    parsed_url = urlparse(current_url)
    # print(parsed_url)
    query_params = parse_qs(parsed_url.query)
    # print(query_params) 
    request_token = query_params.get('request_token',[None])[0]
    # print(request_token)
    with open('request_token.txt', 'w') as f:
        f.write(request_token)
    # print(r)
    request_token = open('request_token','r').read().split()
    driver.quit()
    return request_token
    

    
# request_token = auto_login(api_key,api_secret,user_name,pwd,totp_key)

def generate_access_token(request_token,api_key,api_secret):
    kite = KiteConnect(api_key=api_key)
    data = kite.generate_session(request_token=request_token,api_secret=api_secret)
    data
    with open('access_token.txt','w') as f:
        f.write(data['access_token'])
    access_token = open('access_token','r').read().split()
    return access_token

# access_token = generate_access_token(request_token,api_key,api_secret)

    