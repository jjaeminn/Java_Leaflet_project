import pandas as pd
import mysql.connector
from mysql.connector import Error

def csv_to_mysql(csv_file, host='localhost', user='root', password='2741', database='seven_db', table_name='seven_products'):
    conn = None
    cursor = None
    
    try:
        # CSV 파일 경로 출력하여 확인
        print(f"처리할 CSV 파일: {csv_file}")
        print(f"저장될 데이터베이스: {database}")
        print(f"저장될 테이블: {table_name}")
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"CSV 파일에서 {len(df)}개 상품 정보를 읽었습니다.")
        print(f"CSV 파일 컬럼: {list(df.columns)}")
        
        # MySQL 연결
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # 데이터베이스 생성 (없는 경우)
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            cursor.execute(f"USE {database}")
            print(f"데이터베이스 '{database}'에 연결되었습니다.")
            
            # 테이블이 이미 존재하는지 확인 
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()
            if table_exists:
                print(f"테이블 '{table_name}'이 이미 존재합니다.")
            
            # 테이블 생성 - CSV 파일의 컬럼에 맞춰 동적으로 생성
            columns = []
            columns.append("id INT AUTO_INCREMENT PRIMARY KEY")
            
            for col in df.columns:
                if col == "상품명":
                    columns.append(f"`{col}` VARCHAR(255) NOT NULL")
                elif "URL" in col:
                    columns.append(f"`{col}` VARCHAR(500)")
                else:
                    columns.append(f"`{col}` VARCHAR(100)")
            
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            cursor.execute(create_table_query)
            print(f"테이블 '{table_name}' 생성 완료")
            
            # 데이터 삽입
            for _, row in df.iterrows():
                # CSV 파일의 열 구성에 따라 쿼리 구성
                columns = list(row.index)
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join([f"`{col}`" for col in columns])
                
                insert_query = f"""
                INSERT INTO {table_name} 
                ({columns_str})
                VALUES ({placeholders})
                """
                
                # 행의 값들을 리스트로 변환
                values = [row[col] if pd.notna(row[col]) else None for col in columns]
                
                cursor.execute(insert_query, values)
            
            # 변경사항 저장
            conn.commit()
            print(f"총 {len(df)}개의 상품 정보가 데이터베이스에 성공적으로 저장되었습니다.")
            
    except Error as e:
        print(f"MySQL 오류 발생: {e}")
        # 에러 세부 정보 출력
        if e.errno:
            print(f"에러 코드: {e.errno}")
        if hasattr(e, 'sqlstate'):
            print(f"SQL 상태: {e.sqlstate}")
        if hasattr(e, 'msg'):
            print(f"에러 메시지: {e.msg}")
    except Exception as e:
        print(f"일반 오류 발생: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL 연결이 종료되었습니다.")

# 사용 예 - 세븐일레븐 행사상품 저장
csv_to_mysql(
    csv_file=r"C:\Webcrawl\test_folder\seven_eleven_results\세븐일레븐_행사상품_20250502_122252.csv",
    user="root", 
    password="2741",
    database="seven_db",  # 세븐일레븐 전용 데이터베이스
    table_name="seven_products"  # 세븐일레븐 전용 테이블
)