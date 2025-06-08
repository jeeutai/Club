import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

class NotificationSystem:
    def __init__(self):
        pass
    
    def show_notification_interface(self, user):
        st.markdown("### 🔔 알림 센터")
        
        if user['role'] in ['선생님', '회장', '부회장']:
            tab1, tab2, tab3 = st.tabs(["📬 알림 확인", "📢 알림 발송", "⚙️ 알림 설정"])
            
            with tab1:
                self.show_notifications(user)
            
            with tab2:
                self.show_send_notification(user)
            
            with tab3:
                self.show_notification_settings(user)
        else:
            tab1, tab2 = st.tabs(["📬 내 알림", "⚙️ 알림 설정"])
            
            with tab1:
                self.show_notifications(user)
            
            with tab2:
                self.show_user_notification_settings(user)
    
    def show_notifications(self, user):
        st.markdown("#### 📬 알림 목록")
        
        notifications_df = st.session_state.data_manager.load_csv('notifications')
        
        if notifications_df.empty:
            st.info("알림이 없습니다.")
            return
        
        # Filter notifications for user
        user_notifications = notifications_df[
            (notifications_df['recipient'] == user['username']) |
            (notifications_df['recipient'] == '전체') |
            (notifications_df['recipient'] == user['role'])
        ].sort_values('created_date', ascending=False)
        
        if user_notifications.empty:
            st.info("받은 알림이 없습니다.")
            return
        
        # Mark all as read button
        if st.button("📖 모든 알림 읽음 처리"):
            self.mark_all_as_read(user['username'])
            st.rerun()
        
        # Display notifications
        for _, notification in user_notifications.iterrows():
            self.show_notification_card(notification, user)
    
    def show_notification_card(self, notification, user):
        # Check if read
        read_status_df = st.session_state.data_manager.load_csv('notification_reads')
        is_read = not read_status_df[
            (read_status_df['notification_id'] == notification['id']) &
            (read_status_df['username'] == user['username'])
        ].empty
        
        # Notification styling
        if is_read:
            card_style = "background-color: #f8f9fa; opacity: 0.8;"
            status_text = "읽음"
            status_color = "#6c757d"
        else:
            card_style = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
            status_text = "새 알림"
            status_color = "#ffc107"
        
        # Priority icon
        priority_icons = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        priority_icon = priority_icons.get(notification.get('priority', 'medium'), '🟡')
        
        with st.container():
            st.markdown(f"""
            <div style="{card_style} padding: 16px; border-radius: 10px; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <h4>{priority_icon} {notification['title']}</h4>
                    <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">
                        {status_text}
                    </span>
                </div>
                <p>{notification['content']}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <small>👤 {notification['sender']} | 📅 {notification['created_date']}</small>
                    <small>🏷️ {notification.get('category', '일반')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if not is_read:
                    if st.button("✅ 읽음", key=f"read_{notification['id']}"):
                        self.mark_as_read(notification['id'], user['username'])
                        st.rerun()
    
    def show_send_notification(self, user):
        st.markdown("#### 📢 알림 발송")
        
        with st.form("send_notification"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("알림 제목", placeholder="알림 제목을 입력하세요")
                category = st.selectbox("카테고리", [
                    "일반", "긴급", "과제", "일정", "공지", "이벤트", "기타"
                ])
                priority = st.selectbox("우선순위", ["low", "medium", "high"])
            
            with col2:
                # Recipient selection
                recipient_type = st.selectbox("수신 대상", [
                    "전체", "특정 동아리", "특정 역할", "개별 사용자"
                ])
                
                if recipient_type == "특정 동아리":
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    recipient = st.selectbox("동아리 선택", clubs_df['name'].tolist())
                elif recipient_type == "특정 역할":
                    recipient = st.selectbox("역할 선택", [
                        "회장", "부회장", "총무", "기록부장", "디자인담당", "동아리원"
                    ])
                elif recipient_type == "개별 사용자":
                    accounts_df = st.session_state.data_manager.load_csv('accounts')
                    recipient = st.selectbox("사용자 선택", accounts_df['username'].tolist())
                else:
                    recipient = "전체"
            
            content = st.text_area("알림 내용", height=120, placeholder="알림 내용을 상세히 입력하세요...")
            
            # Schedule notification
            schedule_option = st.checkbox("예약 발송")
            if schedule_option:
                schedule_date = st.date_input("발송일", min_value=date.today())
                schedule_time = st.time_input("발송시간")
            
            if st.form_submit_button("📢 알림 발송", use_container_width=True):
                if title and content:
                    success = self.send_notification(
                        title, content, user['username'], recipient, 
                        category, priority
                    )
                    
                    if success:
                        st.success("알림이 성공적으로 발송되었습니다!")
                        st.rerun()
                    else:
                        st.error("알림 발송 중 오류가 발생했습니다.")
                else:
                    st.error("제목과 내용을 모두 입력해주세요.")
    
    def send_notification(self, title, content, sender, recipient, category, priority):
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            
            new_id = len(notifications_df) + 1
            new_notification = {
                'id': new_id,
                'title': title,
                'content': content,
                'sender': sender,
                'recipient': recipient,
                'category': category,
                'priority': priority,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            notifications_df = pd.concat([notifications_df, pd.DataFrame([new_notification])], ignore_index=True)
            return st.session_state.data_manager.save_csv('notifications', notifications_df)
        
        except Exception as e:
            print(f"Notification send error: {e}")
            return False
    
    def mark_as_read(self, notification_id, username):
        try:
            reads_df = st.session_state.data_manager.load_csv('notification_reads')
            
            # Check if already marked as read
            existing = reads_df[
                (reads_df['notification_id'] == notification_id) &
                (reads_df['username'] == username)
            ]
            
            if existing.empty:
                new_id = len(reads_df) + 1
                new_read = {
                    'id': new_id,
                    'notification_id': notification_id,
                    'username': username,
                    'read_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                reads_df = pd.concat([reads_df, pd.DataFrame([new_read])], ignore_index=True)
                return st.session_state.data_manager.save_csv('notification_reads', reads_df)
            
            return True
        
        except Exception as e:
            print(f"Mark as read error: {e}")
            return False
    
    def mark_all_as_read(self, username):
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            reads_df = st.session_state.data_manager.load_csv('notification_reads')
            
            # Get user's unread notifications
            user_notifications = notifications_df[
                (notifications_df['recipient'] == username) |
                (notifications_df['recipient'] == '전체')
            ]
            
            for _, notification in user_notifications.iterrows():
                # Check if already read
                existing = reads_df[
                    (reads_df['notification_id'] == notification['id']) &
                    (reads_df['username'] == username)
                ]
                
                if existing.empty:
                    new_id = len(reads_df) + 1
                    new_read = {
                        'id': new_id,
                        'notification_id': notification['id'],
                        'username': username,
                        'read_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    reads_df = pd.concat([reads_df, pd.DataFrame([new_read])], ignore_index=True)
            
            return st.session_state.data_manager.save_csv('notification_reads', reads_df)
        
        except Exception as e:
            print(f"Mark all as read error: {e}")
            return False
    
    def show_notification_settings(self, user):
        st.markdown("#### ⚙️ 알림 설정")
        
        # Auto-notification settings
        st.markdown("##### 🤖 자동 알림 설정")
        
        settings = self.load_notification_settings()
        
        with st.form("notification_settings"):
            # Assignment deadline reminders
            deadline_reminder = st.checkbox(
                "과제 마감일 알림", 
                value=settings.get('deadline_reminder', True),
                help="과제 마감 1일 전에 자동 알림 발송"
            )
            
            # Schedule reminders
            schedule_reminder = st.checkbox(
                "일정 알림",
                value=settings.get('schedule_reminder', True),
                help="일정 시작 1시간 전에 자동 알림 발송"
            )
            
            # New member notifications
            new_member_notification = st.checkbox(
                "신규 회원 알림",
                value=settings.get('new_member_notification', True),
                help="새로운 회원이 가입했을 때 알림 발송"
            )
            
            # Chat mention notifications
            chat_mention = st.checkbox(
                "채팅 멘션 알림",
                value=settings.get('chat_mention', True),
                help="채팅에서 언급되었을 때 알림 발송"
            )
            
            if st.form_submit_button("💾 설정 저장"):
                new_settings = {
                    'deadline_reminder': deadline_reminder,
                    'schedule_reminder': schedule_reminder,
                    'new_member_notification': new_member_notification,
                    'chat_mention': chat_mention
                }
                
                if self.save_notification_settings(new_settings):
                    st.success("알림 설정이 저장되었습니다!")
                    st.rerun()
    
    def show_user_notification_settings(self, user):
        st.markdown("#### ⚙️ 개인 알림 설정")
        
        user_settings = self.load_user_notification_settings(user['username'])
        
        with st.form("user_notification_settings"):
            # Enable/disable categories
            st.markdown("##### 📂 카테고리별 알림 수신")
            
            categories = ["일반", "긴급", "과제", "일정", "공지", "이벤트"]
            category_settings = {}
            
            for category in categories:
                category_settings[category] = st.checkbox(
                    f"{category} 알림 수신",
                    value=user_settings.get(f'{category}_enabled', True)
                )
            
            # Notification frequency
            st.markdown("##### ⏰ 알림 빈도")
            
            frequency = st.selectbox(
                "알림 요약 빈도",
                ["즉시", "1시간마다", "일일 요약", "주간 요약"],
                index=["즉시", "1시간마다", "일일 요약", "주간 요약"].index(
                    user_settings.get('frequency', '즉시')
                )
            )
            
            # Quiet hours
            quiet_hours = st.checkbox(
                "조용한 시간 설정",
                value=user_settings.get('quiet_hours_enabled', False),
                help="지정된 시간에는 알림을 받지 않습니다"
            )
            
            quiet_start = None
            quiet_end = None
            if quiet_hours:
                col1, col2 = st.columns(2)
                with col1:
                    quiet_start = st.time_input(
                        "조용한 시간 시작",
                        value=datetime.strptime(user_settings.get('quiet_start', '22:00'), '%H:%M').time()
                    )
                with col2:
                    quiet_end = st.time_input(
                        "조용한 시간 종료",
                        value=datetime.strptime(user_settings.get('quiet_end', '08:00'), '%H:%M').time()
                    )
            
            if st.form_submit_button("💾 설정 저장"):
                new_settings = {
                    'frequency': frequency,
                    'quiet_hours_enabled': quiet_hours,
                }
                
                if quiet_hours and quiet_start is not None and quiet_end is not None:
                    new_settings['quiet_start'] = quiet_start.strftime('%H:%M')
                    new_settings['quiet_end'] = quiet_end.strftime('%H:%M')
                
                # Add category settings
                for category, enabled in category_settings.items():
                    new_settings[f'{category}_enabled'] = enabled
                
                if self.save_user_notification_settings(user['username'], new_settings):
                    st.success("개인 알림 설정이 저장되었습니다!")
                    st.rerun()
    
    def load_notification_settings(self):
        try:
            settings_df = st.session_state.data_manager.load_csv('notification_settings')
            if not settings_df.empty:
                return settings_df.iloc[0].to_dict()
            return {}
        except:
            return {}
    
    def save_notification_settings(self, settings):
        try:
            settings['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            settings_df = pd.DataFrame([settings])
            return st.session_state.data_manager.save_csv('notification_settings', settings_df)
        except Exception as e:
            print(f"Notification settings save error: {e}")
            return False
    
    def load_user_notification_settings(self, username):
        try:
            settings_df = st.session_state.data_manager.load_csv('user_notification_settings')
            user_settings = settings_df[settings_df['username'] == username]
            if not user_settings.empty:
                return user_settings.iloc[0].to_dict()
            return {}
        except:
            return {}
    
    def save_user_notification_settings(self, username, settings):
        try:
            settings_df = st.session_state.data_manager.load_csv('user_notification_settings')
            
            # Remove existing settings for user
            settings_df = settings_df[settings_df['username'] != username]
            
            # Add new settings
            settings['username'] = username
            settings['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            new_settings_df = pd.concat([settings_df, pd.DataFrame([settings])], ignore_index=True)
            return st.session_state.data_manager.save_csv('user_notification_settings', new_settings_df)
        
        except Exception as e:
            print(f"User notification settings save error: {e}")
            return False
    
    def get_unread_count(self, username):
        """Get count of unread notifications for a user"""
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            reads_df = st.session_state.data_manager.load_csv('notification_reads')
            
            # Get user's notifications
            user_notifications = notifications_df[
                (notifications_df['recipient'] == username) |
                (notifications_df['recipient'] == '전체')
            ]
            
            # Get read notification IDs
            read_ids = reads_df[reads_df['username'] == username]['notification_id'].tolist()
            
            # Count unread
            unread_count = len(user_notifications[~user_notifications['id'].isin(read_ids)])
            return unread_count
        
        except:
            return 0