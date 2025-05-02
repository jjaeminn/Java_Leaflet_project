from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import pandas as pd
import os
import re

class SevenElevenEventCrawler:
    def __init__(self, url, crawl_all_pages=True, max_pages=20, wait_time=10):
        """
        세븐일레븐 행사상품 크롤러 초기화 (1+1, 2+1 행사 모두 크롤링)
        
        Args:
            url (str): 크롤링할 웹사이트 URL
            crawl_all_pages (bool): 모든 페이지를 크롤링할지 여부
            max_pages (int): crawl_all_pages가 False일 때 크롤링할 최대 페이지 수
            wait_time (int): 요소 로딩 대기 시간(초)
        """
        self.url = url
        self.crawl_all_pages = crawl_all_pages
        self.max_pages = max_pages
        self.wait_time = wait_time
        self.products = []
        self.product_names = set()  # 상품명 중복 체크를 위한 집합
        
        # 행사 유형 매핑
        self.promotion_mapping = {
            "opo": "1+1",
            "tpo": "2+1"
        }
        
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 헤드리스 모드 (필요시 주석처리)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # WebDriver 초기화
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, wait_time)
    
    def start_crawling(self):
        """크롤링 시작 - 모든 행사 유형 크롤링"""
        try:
            # 웹사이트 접속
            self.driver.get(self.url)
            print(f"웹사이트 접속 완료: {self.url}")
            
            # 페이지 로딩 대기
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.detailList")))
            
            # 페이지가 완전히 로드될 때까지 추가 대기
            time.sleep(3)
            
            # 첫 페이지 크롤링
            current_page = 1
            products_on_page = self._crawl_current_page()
            
            # 결과가 없으면 종료
            if not products_on_page:
                print("상품을 찾을 수 없습니다.")
                return []
                
            self._add_unique_products(products_on_page)
            print(f"페이지 {current_page} 크롤링 완료 - {len(products_on_page)}개 상품 추출")
            
            # 더보기 버튼을 클릭하며 모든 페이지 크롤링
            while self.crawl_all_pages and current_page < self.max_pages:
                try:
                    # 현재 페이지 업데이트
                    next_page_input = self.driver.find_element(By.ID, "nextPage")
                    next_page = int(next_page_input.get_attribute("value"))
                    
                    # 더보기 버튼 찾기
                    more_button = self.driver.find_element(By.ID, "btn_More")
                    
                    # 더보기 버튼이 있으면 클릭
                    if more_button:
                        self.driver.execute_script("arguments[0].click();", more_button)
                        print(f"더보기 버튼 클릭 (페이지 {next_page})")
                        
                        # 페이지 로딩 대기
                        time.sleep(3)
                        
                        # AJAX 로딩 완료 대기
                        self.wait.until(EC.staleness_of(more_button))
                        time.sleep(2)  # 추가 대기
                        
                        # 새로 로드된 페이지 번호 확인
                        current_page = next_page
                        
                        # 새로 로드된 페이지의 상품 크롤링
                        product_count_before = len(self.products)
                        products_on_page = self._crawl_current_page()
                        
                        # 결과가 없으면 마지막 페이지로 판단
                        if not products_on_page:
                            print(f"페이지 {current_page}에 상품이 없습니다. 크롤링을 종료합니다.")
                            break
                        
                        self._add_unique_products(products_on_page)
                        product_count_after = len(self.products)
                        
                        print(f"페이지 {current_page} 크롤링 완료 - {len(products_on_page)}개 상품 추출")
                        print(f"고유 상품 {product_count_after - product_count_before}개 추가됨")
                    else:
                        print("더 이상의 더보기 버튼이 없습니다. 마지막 페이지로 판단합니다.")
                        break
                        
                except NoSuchElementException:
                    print("더보기 버튼을 찾을 수 없습니다. 마지막 페이지로 판단합니다.")
                    break
                except Exception as e:
                    print(f"다음 페이지로 이동 중 오류 발생: {str(e)}")
                    print("마지막 페이지로 판단하고 크롤링을 종료합니다.")
                    break
            
            # 결과 저장
            self._save_results()
            
            return self.products
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return []
            
        finally:
            # 드라이버 종료
            self.driver.quit()
    
    def _add_unique_products(self, products_list):
        """중복되지 않은 상품만 추가"""
        added_count = 0
        for product in products_list:
            product_name = product["상품명"]
            # 이미 추가된 상품명이 아닌 경우에만 추가
            if product_name not in self.product_names:
                self.products.append(product)
                self.product_names.add(product_name)
                added_count += 1
            else:
                print(f"중복 상품 발견 - 제외: {product_name}")
        
        return added_count
    
    def _crawl_current_page(self):
        """현재 페이지의 상품 정보 추출"""
        products_on_page = []
        
        # 페이지가 완전히 로드될 때까지 기다림
        time.sleep(2)
        
        try:
            # 모든 상품 항목 찾기 (타일 뷰)
            product_items = self.driver.find_elements(By.CSS_SELECTOR, "#tileView li")
            
            if not product_items:
                print("현재 페이지에서 상품을 찾을 수 없습니다.")
                return []
                
            print(f"현재 페이지에서 {len(product_items)}개의 상품을 발견했습니다.")
            
            # 각 상품 정보 추출
            for item in product_items:
                try:
                    # 이미지 URL 추출
                    img_element = item.find_element(By.CSS_SELECTOR, "div.img img")
                    img_url = img_element.get_attribute("src")
                    
                    # 상품명 추출
                    name_element = item.find_element(By.CSS_SELECTOR, "div.tit-box p")
                    name = name_element.text.strip()
                    
                    # 가격 추출 (쉼표 제거)
                    price_element = item.find_element(By.CSS_SELECTOR, "span.money")
                    price_text = price_element.text.split('원')[0].strip().replace(',', '')
                    price = price_text
                    
                    # 행사 유형 추출 (1+1, 2+1)
                    promotion_element = item.find_element(By.CSS_SELECTOR, "span.promotion")
                    promotion_class = promotion_element.get_attribute("class")
                    promotion_type = ""
                    
                    for key, value in self.promotion_mapping.items():
                        if key in promotion_class:
                            promotion_type = value
                            break
                    
                    # 행사 분류 (카테고리) 추출
                    try:
                        category_element = item.find_element(By.CSS_SELECTOR, "span.category")
                        category = category_element.text.strip()
                    except NoSuchElementException:
                        category = ""
                    
                    # 상품 정보 저장
                    product_info = {
                        "이미지URL": img_url,
                        "상품명": name,
                        "가격": price,
                        "행사유형": promotion_type,
                        "행사분류": category
                    }
                    
                    products_on_page.append(product_info)
                    print(f"상품 정보 추출: {name} - {price}원 ({promotion_type})")
                    
                except Exception as e:
                    print(f"상품 정보 추출 중 오류: {str(e)}")
            
            return products_on_page
            
        except Exception as e:
            print(f"현재 페이지 크롤링 중 오류: {str(e)}")
            return []
    
    def _save_results(self):
        """크롤링 결과를 CSV 파일로 저장"""
        if not self.products:
            print("저장할 데이터가 없습니다.")
            return
        
        # 결과 디렉토리 생성
        output_dir = "seven_eleven_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 파일명 생성 (현재 시간 포함)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"세븐일레븐_행사상품_{timestamp}.csv")
        
        # DataFrame 생성 및 저장
        df = pd.DataFrame(self.products)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\n크롤링 결과 요약:")
        print(f"- 총 {len(self.products)}개의 상품 정보 수집 (중복 제거됨)")
        print(f"- 결과 저장 경로: {file_path}")
        
        # 행사 분류별 통계
        if '행사분류' in df.columns and df['행사분류'].notna().any():
            category_counts = df['행사분류'].value_counts().to_dict()
            for category, count in category_counts.items():
                if category:  # 빈 문자열이 아닌 경우
                    print(f"- {category}: {count}개 상품")
        
        # 행사 유형별 통계 (1+1, 2+1)
        promotion_counts = df['행사유형'].value_counts().to_dict()
        for promotion_type, count in promotion_counts.items():
            if promotion_type:  # 빈 문자열이 아닌 경우
                print(f"- {promotion_type}: {count}개 상품")

    def set_filter(self, event_type=None, category=None, search_text=None):
        """
        필터 설정 (행사 유형, 카테고리, 검색어)
        
        Args:
            event_type (str): 행사 유형 (1plus1 또는 2plus1)
            category (str): 카테고리
            search_text (str): 검색어
        """
        try:
            # 웹사이트 접속
            self.driver.get(self.url)
            print(f"웹사이트 접속 완료: {self.url}")
            
            # 페이지 로딩 대기
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.detailList")))
            
            # 행사 유형 필터 설정
            if event_type:
                event_select = self.driver.find_element(By.ID, "strEventType")
                event_select.click()
                time.sleep(1)
                
                # 옵션 선택
                option = self.driver.find_element(By.CSS_SELECTOR, f"option[value='{event_type}']")
                option.click()
                time.sleep(1)
                
                print(f"행사 유형 필터 적용: {event_type}")
            
            # 카테고리 필터 설정
            if category:
                category_select = self.driver.find_element(By.ID, "strCategory")
                category_select.click()
                time.sleep(1)
                
                # 옵션 선택
                option = self.driver.find_element(By.CSS_SELECTOR, f"option[value='{category}']")
                option.click()
                time.sleep(1)
                
                print(f"카테고리 필터 적용: {category}")
            
            # 검색어 입력
            if search_text:
                search_input = self.driver.find_element(By.ID, "searchText")
                search_input.clear()
                search_input.send_keys(search_text)
                
                # 검색 버튼 클릭
                search_button = self.driver.find_element(By.ID, "btn_Search")
                search_button.click()
                time.sleep(2)
                
                print(f"검색어 적용: {search_text}")
            
            # 페이지가 완전히 로드될 때까지 추가 대기
            time.sleep(3)
            
        except Exception as e:
            print(f"필터 설정 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 크롤링할 웹사이트 URL
    website_url = "https://www.mycvs.co.kr/v2/plusevent/?cvs=7eleven"
    
    # 크롤러 객체 생성 - wait_time 증가 및 최대 페이지 조정
    crawler = SevenElevenEventCrawler(website_url, crawl_all_pages=True, max_pages=50, wait_time=15)
    
    # 필터 설정 (선택 사항)
    # crawler.set_filter(event_type="1plus1")  # 1+1 행사만 필터링
    # crawler.set_filter(event_type="2plus1")  # 2+1 행사만 필터링
    # crawler.set_filter(category="음료")  # 음료 카테고리만 필터링
    # crawler.set_filter(search_text="생수")  # 검색어로 필터링
    
    # 크롤링 시작
    print("세븐일레븐 행사 상품 크롤링 시작...")
    products = crawler.start_crawling()
    
    print(f"\n크롤링이 완료되었습니다. 총 {len(products)}개의 상품 정보가 수집되었습니다.")