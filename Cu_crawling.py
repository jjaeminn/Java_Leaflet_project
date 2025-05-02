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

class CUEventCrawler:
    def __init__(self, url, crawl_all_pages=True, max_pages=20, wait_time=10):
        """
        CU 행사상품 크롤러 초기화 (1+1, 2+1 행사 모두 크롤링)
        
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
        
        # 행사 탭 ID 목록
        self.event_tabs = {
            "": "전체",
            "23": "1+1",
            "24": "2+1"
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
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.depth3Lnb")))
            
            # 페이지가 완전히 로드될 때까지 추가 대기
            time.sleep(3)
            
            # 각 행사 탭별로 크롤링 진행
            for tab_id, tab_name in self.event_tabs.items():
                print(f"\n===== {tab_name} 크롤링 시작 =====")
                try:
                    self._crawl_event_tab(tab_id, tab_name)
                    # 탭 간 전환 시 페이지가 안정화될 시간 추가
                    time.sleep(3)
                except Exception as e:
                    print(f"{tab_name} 탭 크롤링 중 오류 발생: {str(e)}")
                    print(f"다음 탭으로 진행합니다.")
                    continue
            
            # 결과 저장
            self._save_results()
            
            return self.products
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return []
            
        finally:
            # 드라이버 종료
            self.driver.quit()
    
    def _crawl_event_tab(self, tab_id, tab_name):
        """특정 행사 탭의 상품 정보 크롤링"""
        try:
            # 페이지 새로고침을 통해 초기 상태로 돌아가기
            self.driver.refresh()
            time.sleep(3)
            
            # 탭 선택 - JavaScript 함수 호출하여 탭 변경
            if tab_id:  # 빈 문자열이 아닌 경우 (전체가 아닌 경우)
                script = f"goDepth('{tab_id}');"
                self.driver.execute_script(script)
                print(f"{tab_name} 탭 클릭 완료")
                
                # 탭 변경 후 로딩 대기
                time.sleep(3)
            
            # 현재 활성화된 탭 확인
            current_page = 1
            total_pages = 100  # 많이 설정해서 모든 페이지를 순회하게 함
            
            # 첫 페이지 크롤링
            product_count_before = len(self.products)
            products_on_page = self._crawl_current_page(tab_name)
            self._add_unique_products(products_on_page)
            product_count_after = len(self.products)
            
            print(f"{tab_name}: 페이지 {current_page} 크롤링 완료 - {len(products_on_page)}개 상품 추출")
            print(f"고유 상품 {product_count_after - product_count_before}개 추가됨")
            
            # 더보기 버튼을 클릭하며 모든 페이지 크롤링
            while current_page < total_pages:
                try:
                    # 더보기 버튼 찾기
                    more_button = self.driver.find_element(By.CSS_SELECTOR, "div.prodListBtn-w a")
                    
                    # 더보기 버튼이 있으면 클릭
                    if more_button:
                        self.driver.execute_script("arguments[0].click();", more_button)
                        print(f"더보기 버튼 클릭 (페이지 {current_page+1})")
                        
                        # 페이지 로딩 대기
                        time.sleep(3)
                        
                        current_page += 1
                        
                        # 새로 로드된 페이지의 상품 크롤링
                        product_count_before = len(self.products)
                        products_on_page = self._crawl_current_page(tab_name)
                        
                        # 결과가 없으면 마지막 페이지로 판단
                        if not products_on_page:
                            print(f"{tab_name} 탭의 페이지 {current_page}에 상품이 없습니다. 크롤링을 종료합니다.")
                            break
                        
                        self._add_unique_products(products_on_page)
                        product_count_after = len(self.products)
                        
                        print(f"{tab_name}: 페이지 {current_page} 크롤링 완료 - {len(products_on_page)}개 상품 추출")
                        print(f"고유 상품 {product_count_after - product_count_before}개 추가됨")
                    else:
                        print("더 이상의 더보기 버튼이 없습니다. 마지막 페이지로 판단합니다.")
                        break
                        
                except NoSuchElementException:
                    print("더보기 버튼을 찾을 수 없습니다. 마지막 페이지로 판단합니다.")
                    break
                except Exception as e:
                    print(f"다음 페이지로 이동 중 오류 발생: {str(e)}")
                    print("마지막 페이지로 판단하고 이 탭의 크롤링을 종료합니다.")
                    break
                
        except Exception as e:
            print(f"{tab_name} 탭 크롤링 중 오류 발생: {str(e)}")
    
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
    
    def _crawl_current_page(self, event_type):
        """현재 페이지의 상품 정보 추출"""
        products_on_page = []
        
        # 페이지가 완전히 로드될 때까지 기다림
        time.sleep(2)
        
        try:
            # 모든 상품 항목 찾기
            product_items = self.driver.find_elements(By.CSS_SELECTOR, "li.prod_list")
            
            if not product_items:
                print("현재 페이지에서 상품을 찾을 수 없습니다.")
                return []
                
            print(f"현재 페이지에서 {len(product_items)}개의 상품을 발견했습니다.")
            
            # 각 상품 정보 추출
            for item in product_items:
                try:
                    # 상품 링크 요소 찾기
                    product_link = item.find_element(By.CSS_SELECTOR, "a.prod_item")
                    
                    # 이미지 URL 추출
                    img_element = item.find_element(By.CSS_SELECTOR, "div.prod_img img")
                    img_url = img_element.get_attribute("src")
                    
                    # 상품명 추출
                    name_element = item.find_element(By.CSS_SELECTOR, "div.name p")
                    name = name_element.text.strip()
                    
                    # 가격 추출
                    price_element = item.find_element(By.CSS_SELECTOR, "div.price strong")
                    price = price_element.text.strip().replace(',', '')
                    
                    # 행사 유형 추출 (1+1, 2+1)
                    promotion = ""
                    promotion_elements = item.find_elements(By.CSS_SELECTOR, "div.badge span")
                    if promotion_elements:
                        for element in promotion_elements:
                            class_name = element.get_attribute("class")
                            if "plus1" in class_name:
                                promotion = "1+1"
                            elif "plus2" in class_name:
                                promotion = "2+1"
                    
                    # 상품 정보 저장
                    product_info = {
                        "이미지URL": img_url,
                        "상품명": name,
                        "가격": price,
                        "행사유형": promotion,
                        "행사분류": event_type
                    }
                    
                    products_on_page.append(product_info)
                    print(f"상품 정보 추출: {name} - {price}원 ({promotion})")
                    
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
        output_dir = "cu_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 파일명 생성 (현재 시간 포함)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"CU_행사상품_{timestamp}.csv")
        
        # DataFrame 생성 및 저장
        df = pd.DataFrame(self.products)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\n크롤링 결과 요약:")
        print(f"- 총 {len(self.products)}개의 상품 정보 수집 (중복 제거됨)")
        print(f"- 결과 저장 경로: {file_path}")
        
        # 행사 유형별 통계
        event_counts = df['행사분류'].value_counts().to_dict()
        for event_type, count in event_counts.items():
            print(f"- {event_type}: {count}개 상품")
        
        # 행사 유형별 통계 (1+1, 2+1)
        promotion_counts = df['행사유형'].value_counts().to_dict()
        for promotion_type, count in promotion_counts.items():
            if promotion_type:  # 빈 문자열이 아닌 경우
                print(f"- {promotion_type}: {count}개 상품")

    def crawl_single_event(self, tab_id):
        """특정 행사 유형만 크롤링"""
        try:
            # 웹사이트 접속
            self.driver.get(self.url)
            print(f"웹사이트 접속 완료: {self.url}")
            
            # 페이지 로딩 대기
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.depth3Lnb")))
            
            # 지정된 행사 탭만 크롤링
            if tab_id in self.event_tabs:
                tab_name = self.event_tabs[tab_id]
                print(f"\n===== {tab_name} 크롤링 시작 =====")
                self._crawl_event_tab(tab_id, tab_name)
                
                # 결과 저장
                self._save_results()
                
                return self.products
            else:
                print(f"유효하지 않은 행사 유형: {tab_id}")
                print(f"유효한 행사 유형: {list(self.event_tabs.keys())}")
                return []
                
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return []
            
        finally:
            # 드라이버 종료
            self.driver.quit()

if __name__ == "__main__":
    # 크롤링할 웹사이트 URL
    website_url = "https://cu.bgfretail.com/event/plus.do?category=event&depth2=1&sf=N"
    
    # 크롤러 객체 생성 - wait_time 증가 및 최대 페이지 조정
    crawler = CUEventCrawler(website_url, crawl_all_pages=True, max_pages=100, wait_time=15)
    
    # 모든 탭 크롤링
    print("모든 행사 상품 크롤링 시작...")
    products = crawler.start_crawling()
    
    # 또는 각 탭을 개별적으로 크롤링할 수 있습니다
    # print("1+1 행사 상품만 크롤링...")
    # products = crawler.crawl_single_event("23")  # 1+1 행사만 크롤링
    
    # print("2+1 행사 상품만 크롤링...")
    # products = crawler.crawl_single_event("24")  # 2+1 행사만 크롤링
    
    # print("전체 행사 상품만 크롤링...")
    # products = crawler.crawl_single_event("")  # 전체 행사만 크롤링
    
    print(f"\n크롤링이 완료되었습니다. 총 {len(products)}개의 상품 정보가 수집되었습니다.")