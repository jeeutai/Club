import pandas as pd
import os
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.accounts_file = 'data/accounts.csv'
        self.ensure_data_directory()
        self.initialize_accounts()
    
    def ensure_data_directory(self):
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def initialize_accounts(self):
        if not os.path.exists(self.accounts_file):
            # Create initial accounts
            initial_accounts = [
                {
                    'username': '조성우',
                    'password': 'admin',
                    'name': '조성우 선생님',
                    'role': '선생님',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'president1',
                    'password': '1234',
                    'name': '김회장',
                    'role': '회장',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'vicepresident1',
                    'password': '1234',
                    'name': '이부회장',
                    'role': '부회장',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'treasurer1',
                    'password': '1234',
                    'name': '박총무',
                    'role': '총무',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'recorder1',
                    'password': '1234',
                    'name': '최기록',
                    'role': '기록부장',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'designer1',
                    'password': '1234',
                    'name': '정디자인',
                    'role': '디자인담당',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'member1',
                    'password': '1234',
                    'name': '강동아리',
                    'role': '동아리원',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'username': 'member2',
                    'password': '1234',
                    'name': '윤학생',
                    'role': '동아리원',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ]
            
            df = pd.DataFrame(initial_accounts)
            df.to_csv(self.accounts_file, index=False, encoding='utf-8-sig')
    
    def login(self, username, password):
        try:
            df = pd.read_csv(self.accounts_file, encoding='utf-8-sig')
            user = df[(df['username'] == username) & (df['password'] == password)]
            
            if not user.empty:
                return user.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def create_account(self, username, password, name, role):
        try:
            df = pd.read_csv(self.accounts_file, encoding='utf-8-sig')
            
            # Check if username already exists
            if username in df['username'].values:
                return False
            
            new_account = {
                'username': username,
                'password': password,
                'name': name,
                'role': role,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            df = pd.concat([df, pd.DataFrame([new_account])], ignore_index=True)
            df.to_csv(self.accounts_file, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"Account creation error: {e}")
            return False
    
    def get_all_accounts(self):
        try:
            return pd.read_csv(self.accounts_file, encoding='utf-8-sig')
        except:
            return pd.DataFrame()
