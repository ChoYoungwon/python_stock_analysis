import pandas as pd
import pymysql
import os
import requests
from datetime import datetime
from dotenv import load_dotenv          # .env 파일 읽기

class DBUpdater:
    # 생성자 : MariaDB 연결, 종목코드 딕셔너리 생성
    def __init__(self):
        load_dotenv()  # .env 파일 로드
        
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user=os.getenv('MARIADB_USER', 'youngwon'), 
            password=os.getenv('MARIADB_PASSWORD'), 
            db=os.getenv('MARIADB_DATABASE', 'KOSPI'), 
            charset='utf8'
        )
        
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY (code))
            """
            curs.execute(sql)
            
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date))
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
        # self.update_comp_info()
    
    # 소멸자: MariaDB 연결 해제
    def __del__(self):
        self.conn.close()
        
    # KRX로부터 상장기업 목록파일을 읽어와서 데이터프레임으로 반환
    def read_krx_code(self):
        url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method='\
            'download&searchType=13'
        krx = pd.read_html(url, header=0, encoding='cp949')[0]
        krx = krx[['종목코드', '회사명']]
        krx = krx.rename(columns={'종목코드' : 'code', '회사명':'company'})
        krx.code = krx.code.map('{:06d}'.format)
        return krx
    
    # 종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장
    def update_comp_info(self, self.conn):
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.conn)
        
        for idx in range(len(df)):   # 종목코드와 회사명 codes 딕셔너리로 제작
            self.codes[df['code'].values[idx]]=df['company'].values[idx]        
        
        with self.conn.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()     # querry문 가장 최근 업데이트 날짜 가져오기
            today = datetime.today().strftime('%Y-%m-%d')
            
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:  # 날짜 비교 후 업데이트
                krx = self.read_krx_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO company_info (code, company, last"\
                        f"_update) VALUES ('{code}', '{comapny}', '{today}')"
                    curs.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] {idx:04d} REPLACE INTO company_info "\
                        f"VALUES ({code}, {company}, {today})")
                self.conn.commit()
                print('')  
    
if __name__ == '__main__':
    try:
        db_updater = DBUpdater()
        krx_data = db_updater.read_krx_code()
        print("연결 성공")
        print(f"읽어온 기업 수 : {len(krx_data)}")
        print(krx_data.head())
    except Exception as e:
        print(f"연결실패: {e}")
    