import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()
        self.initialize_csv_files()
    
    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_csv_files(self):
        csv_files = {
            'clubs': ['name', 'icon', 'description', 'president', 'max_members', 'created_date'],
            'user_clubs': ['username', 'club_name', 'joined_date'],
            'posts': ['id', 'title', 'content', 'author', 'club', 'timestamp', 'likes'],
            'chat_logs': ['id', 'username', 'message', 'club', 'timestamp', 'deleted'],
            'assignments': ['id', 'title', 'description', 'club', 'due_date', 'creator', 'status', 'created_date'],
            'submissions': ['id', 'assignment_id', 'username', 'content', 'file_path', 'score', 'feedback', 'submitted_date'],
            'attendance': ['id', 'username', 'club', 'date', 'status', 'recorder'],
            'schedule': ['id', 'title', 'description', 'date', 'club', 'creator', 'created_date'],
            'badges': ['id', 'username', 'badge_name', 'description', 'awarded_date', 'awarded_by'],
            'points': ['id', 'username', 'points', 'reason', 'date', 'awarded_by'],
            'votes': ['id', 'title', 'description', 'options', 'creator', 'club', 'end_date', 'created_date'],
            'vote_responses': ['id', 'vote_id', 'username', 'selected_option', 'voted_date'],
            'quizzes': ['id', 'title', 'description', 'club', 'difficulty', 'time_limit', 'questions', 'creator', 'created_date'],
            'quiz_attempts': ['id', 'quiz_id', 'username', 'answers', 'score', 'attempted_date'],
            'galleries': ['id', 'title', 'description', 'image_path', 'author', 'club', 'created_date', 'likes'],
            'gallery_comments': ['id', 'gallery_id', 'username', 'comment', 'created_date'],
            'notifications': ['id', 'title', 'content', 'sender', 'recipient', 'category', 'priority', 'created_date'],
            'notification_reads': ['id', 'notification_id', 'username', 'read_date'],
            'notification_settings': ['deadline_reminder', 'schedule_reminder', 'new_member_notification', 'chat_mention', 'updated_date'],
            'user_notification_settings': ['username', 'frequency', 'quiet_hours_enabled', 'quiet_start', 'quiet_end', 'updated_date'],
            'reports': ['id', 'title', 'content', 'creator', 'club', 'report_date', 'created_date']
        }
        
        for filename, column_list in csv_files.items():
            filepath = os.path.join(self.data_dir, f'{filename}.csv')
            if not os.path.exists(filepath):
                # Create empty DataFrame with specified columns
                data = {col: [] for col in column_list}
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        # Initialize clubs if empty
        self.initialize_default_clubs()
    
    def initialize_default_clubs(self):
        clubs_file = os.path.join(self.data_dir, 'clubs.csv')
        df = pd.read_csv(clubs_file, encoding='utf-8-sig')
        
        if df.empty:
            default_clubs = [
                {
                    'name': '코딩',
                    'icon': '💻',
                    'description': '프로그래밍과 컴퓨터 과학을 배우는 동아리',
                    'president': 'president1',
                    'max_members': 20,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'name': '댄스',
                    'icon': '💃',
                    'description': '다양한 춤을 배우고 공연하는 동아리',
                    'president': 'president1',
                    'max_members': 15,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'name': '만들기',
                    'icon': '🔨',
                    'description': '손으로 만드는 모든 것을 탐구하는 동아리',
                    'president': 'president1',
                    'max_members': 12,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'name': '미스테리탐구',
                    'icon': '🔍',
                    'description': '신비한 현상과 미스터리를 탐구하는 동아리',
                    'president': 'president1',
                    'max_members': 10,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'name': '줄넘기',
                    'icon': '🪢',
                    'description': '줄넘기 기술을 연마하고 체력을 기르는 동아리',
                    'president': 'president1',
                    'max_members': 25,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'name': '풍선아트',
                    'icon': '🎈',
                    'description': '풍선으로 다양한 작품을 만드는 동아리',
                    'president': 'president1',
                    'max_members': 15,
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ]
            
            df = pd.DataFrame(default_clubs)
            df.to_csv(clubs_file, index=False, encoding='utf-8-sig')
            
            # Add some users to clubs
            self.initialize_user_clubs()
    
    def initialize_user_clubs(self):
        user_clubs_data = [
            {'username': 'president1', 'club_name': '코딩', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'president1', 'club_name': '댄스', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'vicepresident1', 'club_name': '코딩', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'treasurer1', 'club_name': '만들기', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'recorder1', 'club_name': '미스테리탐구', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'designer1', 'club_name': '풍선아트', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'member1', 'club_name': '코딩', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'member1', 'club_name': '줄넘기', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'member2', 'club_name': '댄스', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
            {'username': 'member2', 'club_name': '풍선아트', 'joined_date': datetime.now().strftime('%Y-%m-%d')},
        ]
        
        user_clubs_file = os.path.join(self.data_dir, 'user_clubs.csv')
        df = pd.DataFrame(user_clubs_data)
        df.to_csv(user_clubs_file, index=False, encoding='utf-8-sig')
    
    def load_csv(self, filename):
        try:
            filepath = os.path.join(self.data_dir, f'{filename}.csv')
            return pd.read_csv(filepath, encoding='utf-8-sig')
        except:
            return pd.DataFrame()
    
    def save_csv(self, filename, df):
        try:
            filepath = os.path.join(self.data_dir, f'{filename}.csv')
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def get_user_clubs(self, username):
        user_clubs_df = self.load_csv('user_clubs')
        clubs_df = self.load_csv('clubs')
        
        if user_clubs_df.empty or clubs_df.empty:
            return pd.DataFrame()
        
        user_clubs = user_clubs_df[user_clubs_df['username'] == username]
        result = user_clubs.merge(clubs_df, left_on='club_name', right_on='name', how='left')
        return result
    
    def create_account(self, username, password, name, role):
        accounts_df = self.load_csv('accounts')
        
        if username in accounts_df['username'].values:
            return False
        
        new_account = {
            'username': username,
            'password': password,
            'name': name,
            'role': role,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        accounts_df = pd.concat([accounts_df, pd.DataFrame([new_account])], ignore_index=True)
        return self.save_csv('accounts', accounts_df)
    
    def create_club(self, name, icon, description, president, max_members):
        clubs_df = self.load_csv('clubs')
        
        if name in clubs_df['name'].values:
            return False
        
        new_club = {
            'name': name,
            'icon': icon,
            'description': description,
            'president': president,
            'max_members': max_members,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        clubs_df = pd.concat([clubs_df, pd.DataFrame([new_club])], ignore_index=True)
        return self.save_csv('clubs', clubs_df)
    
    def delete_club(self, club_name):
        clubs_df = self.load_csv('clubs')
        clubs_df = clubs_df[clubs_df['name'] != club_name]
        
        # Also remove user associations
        user_clubs_df = self.load_csv('user_clubs')
        user_clubs_df = user_clubs_df[user_clubs_df['club_name'] != club_name]
        
        self.save_csv('clubs', clubs_df)
        self.save_csv('user_clubs', user_clubs_df)
    
    def add_user_to_club(self, username, club_name):
        user_clubs_df = self.load_csv('user_clubs')
        
        # Check if already member
        existing = user_clubs_df[(user_clubs_df['username'] == username) & 
                                (user_clubs_df['club_name'] == club_name)]
        if not existing.empty:
            return False
        
        new_membership = {
            'username': username,
            'club_name': club_name,
            'joined_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        user_clubs_df = pd.concat([user_clubs_df, pd.DataFrame([new_membership])], ignore_index=True)
        return self.save_csv('user_clubs', user_clubs_df)
    
    def add_post(self, author, title, content, club):
        posts_df = self.load_csv('posts')
        
        new_id = len(posts_df) + 1
        new_post = {
            'id': new_id,
            'title': title,
            'content': content,
            'author': author,
            'club': club,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'likes': 0
        }
        
        posts_df = pd.concat([posts_df, pd.DataFrame([new_post])], ignore_index=True)
        return self.save_csv('posts', posts_df)
    
    def add_chat_message(self, username, message, club):
        chat_logs_df = self.load_csv('chat_logs')
        
        new_id = len(chat_logs_df) + 1
        new_message = {
            'id': new_id,
            'username': username,
            'message': message,
            'club': club,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deleted': False
        }
        
        chat_logs_df = pd.concat([chat_logs_df, pd.DataFrame([new_message])], ignore_index=True)
        return self.save_csv('chat_logs', chat_logs_df)
    
    def add_assignment(self, title, description, club, due_date, creator):
        assignments_df = self.load_csv('assignments')
        
        new_id = len(assignments_df) + 1
        new_assignment = {
            'id': new_id,
            'title': title,
            'description': description,
            'club': club,
            'due_date': due_date,
            'creator': creator,
            'status': 'active',
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        assignments_df = pd.concat([assignments_df, pd.DataFrame([new_assignment])], ignore_index=True)
        return self.save_csv('assignments', assignments_df)
    
    def add_submission(self, assignment_id, username, content, file_path=None):
        submissions_df = self.load_csv('submissions')
        
        new_id = len(submissions_df) + 1
        new_submission = {
            'id': new_id,
            'assignment_id': assignment_id,
            'username': username,
            'content': content,
            'file_path': file_path or '',
            'score': 0,
            'feedback': '',
            'submitted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        submissions_df = pd.concat([submissions_df, pd.DataFrame([new_submission])], ignore_index=True)
        return self.save_csv('submissions', submissions_df)
    
    def add_schedule(self, title, description, date, club, creator):
        schedule_df = self.load_csv('schedule')
        
        new_id = len(schedule_df) + 1
        new_event = {
            'id': new_id,
            'title': title,
            'description': description,
            'date': date,
            'club': club,
            'creator': creator,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        schedule_df = pd.concat([schedule_df, pd.DataFrame([new_event])], ignore_index=True)
        return self.save_csv('schedule', schedule_df)
    
    def add_points(self, username, points, reason):
        points_df = self.load_csv('points')
        
        new_id = len(points_df) + 1
        new_points = {
            'id': new_id,
            'username': username,
            'points': points,
            'reason': reason,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'awarded_by': 'system'
        }
        
        points_df = pd.concat([points_df, pd.DataFrame([new_points])], ignore_index=True)
        return self.save_csv('points', points_df)
