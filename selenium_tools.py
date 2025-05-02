# 1. pip install virtualenv 가상환경 설치 

# 2. cd test_folder (project) 

# 3. folder/Scripts/activate - 가상환경 활성화 
# 3. deactivate -가상환경 비활성화 

# 4. Unauthorized Access 에러가 발생 -> powershell 관리자 권한 실행 -> Set-ExecutionPolicy 

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

import chromedriver_autoinstaller

chromedriver_autoinstaller.install()



# 1. Navigation 네비게이션 관련 툴  -> 네비게이션이란 특정 웹 사이트로 이동하는 걸 말한다.(새로고침도 포함)
# 1-1 .get() 원하는 페이지로 이동하는 함수
# 2-1. title ~ 웹 사이트 타이틀 가지고 옴 
# 2-2  currnet_url 주소창을 그대로 가지고옴 
# 3. driver wait -> 네트웨크 
driver = webdriver.Chrome()

driver.get("https://www.naver.com")
# 10초 넘어가면 에러던진다. 

try:
     selector = "#account > div > div > a:nth-child(1)"
     WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located
                                (By.CSS_SELECTOR,selector
                                                                    ))
except:
    print("예외 발생")
print("엘리먼트 로딩 끝")
print("다음 코드 실행")
input()
# time.sleep(3)
# driver.get("https://www.google.com")
# # 1-2 .back() -뒤로가기 
# driver.back()
# time.sleep(2)
# # 1-3. forward() -앞으로 가기 
# driver.forward()
# time.sleep(2)
# # 1-4. refresh() - 페이지 새로고침 

# driver.refresh()
# time.sleep(2)
# time.sleep(2)
# print("동작 끝 ㅅㄱ")
# #input()













