from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
# from headless_chrome import create_driver
import os
load_dotenv()

def Login(student_ID: str, passwordString: str, icheckinCode: str):
  
  if os.environ.get("AWS_EXECUTION_ENV") is None:
    chrome_options = webdriver.ChromeOptions()
    if os.environ.get("AWS_EXECUTION_ENV") is not None:
      chrome_options.binary_location = "/opt/headless-chromium" # FOR AWS LAMBDA
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome('/opt/chromedriver',options=chrome_options) if os.environ.get("AWS_EXECUTION_ENV") else webdriver.Chrome('chromedriver',chrome_options=chrome_options) # FOR AWS LAMBDA and LOCAL
    browser = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
  else:  # AWS LAMBDA
    # browser = create_driver()
    browser = None

  browser.get("https://izone.sunway.edu.my/login")

  username = browser.find_element(By.ID , "student_uid")
  username.send_keys(student_ID)

  password = browser.find_element(By.ID, "password")
  password.send_keys(passwordString)

  submitBtn = browser.find_element(By.ID, "submit")
  submitBtn.click()
  
  # check for errors
  browser.implicitly_wait(1)
  try:
    login_error = browser.find_element(By.ID, "msg")
    return login_error.text
  except:
    pass # no error
    
  # wait for 6 seconds for logging in process before proceeding
  icheckin = WebDriverWait(browser, 6).until(
  EC.presence_of_element_located((By.ID, 'iCheckInUrl')))
  icheckin.click()

  # wait until icheckin page loads
  icheckinInput = WebDriverWait(browser, 6).until(
  EC.presence_of_element_located((By.ID, 'checkin_code')))
  icheckinInput.send_keys(icheckinCode)
  print("icheckin Code:", icheckinCode)

  # click check in button
  checkInBtn = browser.find_element(By.ID, "iCheckin")
  checkInBtn.click()

  # wait until notification pops up
  notification = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.ID, "notification")))
  reply = notification.text

  # exit browser
  browser.close()
  
  # return the reply from server
  print(reply)
  return reply
    
if __name__ == "__main__":
  Login("1806631", "Sunway4edu@me", "123456")