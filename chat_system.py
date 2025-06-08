import streamlit as st
import pandas as pd
from datetime import datetime

class ChatSystem:
    def __init__(self):
        pass
    
    def show_chat_interface(self, user):
        st.markdown("### 💬 채팅")
        
        # Get user's clubs for chat room selection
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            available_clubs = ["전체"] + clubs_df['name'].tolist()
        else:
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            available_clubs = ["전체"] + user_clubs['club_name'].tolist()
        
        # Chat room selection
        selected_club = st.selectbox("채팅방 선택", available_clubs)
        
        # Chat display area
        chat_container = st.container()
        
        with chat_container:
            self.display_chat_messages(selected_club, user)
        
        # Message input
        st.markdown("---")
        with st.form("chat_input", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                message = st.text_area("메시지 입력", height=80, placeholder="메시지를 입력하세요...")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                send_button = st.form_submit_button("전송", use_container_width=True)
            
            if send_button and message.strip():
                self.send_message(user['username'], message.strip(), selected_club)
                st.rerun()
    
    def display_chat_messages(self, club, user):
        chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
        
        if chat_logs_df.empty:
            st.info("아직 채팅 메시지가 없습니다. 첫 메시지를 보내보세요!")
            return
        
        # Filter messages by club
        if club == "전체":
            # Show all messages user has access to
            if user['role'] == '선생님':
                filtered_messages = chat_logs_df
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                filtered_messages = chat_logs_df[chat_logs_df['club'].isin(user_club_names)]
        else:
            filtered_messages = chat_logs_df[chat_logs_df['club'] == club]
        
        # Filter out deleted messages (except for admins)
        if user['role'] != '선생님':
            filtered_messages = filtered_messages[filtered_messages['deleted'] == False]
        
        # Sort by timestamp
        filtered_messages = filtered_messages.sort_values('timestamp')
        
        if filtered_messages.empty:
            st.info(f"{club} 채팅방에 메시지가 없습니다.")
            return
        
        # Display messages
        for _, message in filtered_messages.iterrows():
            self.display_message(message, user)
    
    def display_message(self, message, current_user):
        is_own_message = message['username'] == current_user['username']
        is_deleted = message['deleted']
        
        # Message container styling
        if is_own_message:
            alignment = "flex-end"
            bg_color = "#FF6B6B"
            text_color = "white"
        else:
            alignment = "flex-start"
            bg_color = "#f1f3f4"
            text_color = "#333"
        
        # Show deleted message only to admins
        if is_deleted and current_user['role'] != '선생님':
            return
        
        deleted_indicator = " 🗑️ (삭제된 메시지)" if is_deleted else ""
        
        st.markdown(f"""
        <div style="display: flex; justify-content: {alignment}; margin: 10px 0;">
            <div style="max-width: 70%; background-color: {bg_color}; color: {text_color}; 
                        padding: 10px 15px; border-radius: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <div style="font-weight: bold; font-size: 12px; margin-bottom: 5px;">
                    {message['username']}{deleted_indicator}
                </div>
                <div style="word-wrap: break-word;">
                    {message['message']}
                </div>
                <div style="font-size: 10px; opacity: 0.7; margin-top: 5px; text-align: right;">
                    {message['timestamp']} | 🏷️ {message['club']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Admin controls
        if current_user['role'] == '선생님' and not is_deleted:
            col1, col2, col3 = st.columns([6, 1, 1])
            with col2:
                if st.button("🗑️", key=f"delete_msg_{message['id']}", help="메시지 삭제"):
                    self.delete_message(message['id'])
                    st.rerun()
    
    def send_message(self, username, message, club):
        success = st.session_state.data_manager.add_chat_message(username, message, club)
        if success:
            st.success("메시지가 전송되었습니다!")
        else:
            st.error("메시지 전송에 실패했습니다.")
    
    def delete_message(self, message_id):
        try:
            chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
            
            # Mark message as deleted instead of actually deleting
            chat_logs_df.loc[chat_logs_df['id'] == message_id, 'deleted'] = True
            
            success = st.session_state.data_manager.save_csv('chat_logs', chat_logs_df)
            
            if success:
                st.success("메시지가 삭제되었습니다.")
            else:
                st.error("메시지 삭제에 실패했습니다.")
                
        except Exception as e:
            st.error(f"메시지 삭제 중 오류가 발생했습니다: {e}")
    
    def show_chat_management(self, user):
        """Admin-only chat management interface"""
        if user['role'] != '선생님':
            st.warning("채팅 관리 권한이 없습니다.")
            return
        
        st.markdown("#### 💬 채팅 관리")
        
        tab1, tab2, tab3 = st.tabs(["📊 통계", "🗑️ 삭제된 메시지", "🔍 검색"])
        
        with tab1:
            self.show_chat_statistics()
        
        with tab2:
            self.show_deleted_messages()
        
        with tab3:
            self.show_chat_search()
    
    def show_chat_statistics(self):
        chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
        
        if chat_logs_df.empty:
            st.info("채팅 통계가 없습니다.")
            return
        
        # Message count by user
        user_message_counts = chat_logs_df['username'].value_counts()
        st.markdown("##### 사용자별 메시지 수")
        st.bar_chart(user_message_counts.head(10))
        
        # Message count by club
        club_message_counts = chat_logs_df['club'].value_counts()
        st.markdown("##### 동아리별 메시지 수")
        st.bar_chart(club_message_counts)
        
        # Daily activity
        chat_logs_df['date'] = pd.to_datetime(chat_logs_df['timestamp']).dt.date
        daily_counts = chat_logs_df['date'].value_counts().sort_index()
        st.markdown("##### 일별 채팅 활동")
        st.line_chart(daily_counts)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_messages = len(chat_logs_df)
            st.metric("총 메시지", total_messages)
        
        with col2:
            active_users = chat_logs_df['username'].nunique()
            st.metric("활성 사용자", active_users)
        
        with col3:
            deleted_messages = len(chat_logs_df[chat_logs_df['deleted'] == True])
            st.metric("삭제된 메시지", deleted_messages)
        
        with col4:
            avg_daily = daily_counts.mean() if not daily_counts.empty else 0
            st.metric("일평균 메시지", f"{avg_daily:.1f}")
    
    def show_deleted_messages(self):
        chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
        deleted_messages = chat_logs_df[chat_logs_df['deleted'] == True]
        
        if deleted_messages.empty:
            st.info("삭제된 메시지가 없습니다.")
            return
        
        st.markdown("##### 🗑️ 삭제된 메시지 목록")
        
        for _, message in deleted_messages.iterrows():
            with st.container():
                st.markdown(f"""
                <div style="background-color: #ffe6e6; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #ff4444;">
                    <strong>{message['username']}</strong> in {message['club']}<br>
                    <em>{message['message']}</em><br>
                    <small>삭제됨: {message['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("복구", key=f"restore_msg_{message['id']}"):
                    self.restore_message(message['id'])
                    st.rerun()
    
    def show_chat_search(self):
        st.markdown("##### 🔍 채팅 검색")
        
        search_term = st.text_input("검색어를 입력하세요")
        
        if search_term:
            chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
            
            # Search in messages
            search_results = chat_logs_df[
                chat_logs_df['message'].str.contains(search_term, case=False, na=False)
            ]
            
            if not search_results.empty:
                st.markdown(f"**'{search_term}' 검색 결과: {len(search_results)}개**")
                
                for _, result in search_results.iterrows():
                    deleted_indicator = " (삭제됨)" if result['deleted'] else ""
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <strong>{result['username']}</strong> in {result['club']}{deleted_indicator}<br>
                        {result['message']}<br>
                        <small>{result['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"'{search_term}'에 대한 검색 결과가 없습니다.")
    
    def restore_message(self, message_id):
        try:
            chat_logs_df = st.session_state.data_manager.load_csv('chat_logs')
            chat_logs_df.loc[chat_logs_df['id'] == message_id, 'deleted'] = False
            
            success = st.session_state.data_manager.save_csv('chat_logs', chat_logs_df)
            
            if success:
                st.success("메시지가 복구되었습니다.")
            else:
                st.error("메시지 복구에 실패했습니다.")
                
        except Exception as e:
            st.error(f"메시지 복구 중 오류가 발생했습니다: {e}")
