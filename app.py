# 1. pip install virtualenv 가상환경 설치 

# 2. cd test_folder (project) 

# 3. folder/Scripts/activate - 가상환경 활성화 
# 3. deactivate -가상환경 비활성화 

# 4. Unauthorized Access 에러가 발생 -> powershell 관리자 권한 실행 -> Set-ExecutionPolicy 

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

import chromedriver_autoinstaller

chromedriver_autoinstaller.install()



# 1. 웹 브라우저 주소창을 컨트롤하기 드라이버.가져오기 
driver = webdriver.Chrome()
driver.get("http://gs25.gsretail.com/gscvs/ko/products/event-goods#;")
time.sleep(3)


# 요소를 찾아서 copy 조지기 
css_selector = "p.tit"
# 2-2. 찾아온 요소를 find_element로 가져와 변수 놓기 
group_nav = driver.find_element(By.CSS_SELECTOR, css_selector)

# 3-1 데이터 가져오기
print(group_nav.text)


# 3-2 요소를 클릭하기 
group_nav.click()

input()

