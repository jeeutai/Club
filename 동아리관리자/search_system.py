import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

class SearchSystem:
    def __init__(self):
        pass
    
    def show_search_interface(self, user):
        st.markdown("### 🔍 통합 검색")
        
        # Search input
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔍 검색어를 입력하세요", placeholder="게시글, 과제, 채팅, 일정 등을 검색할 수 있습니다")
        
        with col2:
            search_type = st.selectbox("검색 범위", ["전체", "게시판", "채팅", "과제", "일정", "갤러리"])
        
        if search_query:
            # Advanced search options
            with st.expander("🔧 고급 검색 옵션"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    date_filter = st.checkbox("날짜 범위 필터")
                    if date_filter:
                        start_date = st.date_input("시작 날짜")
                        end_date = st.date_input("종료 날짜")
                
                with col2:
                    club_filter = st.checkbox("동아리 필터")
                    if club_filter:
                        clubs_df = st.session_state.data_manager.load_csv('clubs')
                        selected_clubs = st.multiselect("동아리 선택", clubs_df['name'].tolist())
                
                with col3:
                    author_filter = st.checkbox("작성자 필터")
                    if author_filter:
                        accounts_df = st.session_state.data_manager.load_csv('accounts')
                        selected_authors = st.multiselect("작성자 선택", accounts_df['username'].tolist())
            
            # Perform search
            results = self.perform_search(search_query, search_type, user)
            
            if results:
                st.markdown(f"### 검색 결과 ({len(results)}개)")
                
                # Filter results based on advanced options
                if 'date_filter' in locals() and date_filter:
                    results = self.filter_by_date(results, start_date, end_date)
                
                if 'club_filter' in locals() and club_filter and selected_clubs:
                    results = self.filter_by_club(results, selected_clubs)
                
                if 'author_filter' in locals() and author_filter and selected_authors:
                    results = self.filter_by_author(results, selected_authors)
                
                # Display results
                self.display_search_results(results, search_query)
            else:
                st.info("검색 결과가 없습니다.")
    
    def perform_search(self, query, search_type, user):
        results = []
        
        # Search in posts
        if search_type in ["전체", "게시판"]:
            posts_results = self.search_posts(query, user)
            results.extend(posts_results)
        
        # Search in chat
        if search_type in ["전체", "채팅"]:
            chat_results = self.search_chat(query, user)
            results.extend(chat_results)
        
        # Search in assignments
        if search_type in ["전체", "과제"]:
            assignment_results = self.search_assignments(query, user)
            results.extend(assignment_results)
        
        # Search in schedule
        if search_type in ["전체", "일정"]:
            schedule_results = self.search_schedule(query, user)
            results.extend(schedule_results)
        
        # Search in gallery
        if search_type in ["전체", "갤러리"]:
            gallery_results = self.search_gallery(query, user)
            results.extend(gallery_results)
        
        return results
    
    def search_posts(self, query, user):
        posts_df = st.session_state.data_manager.load_csv('posts')
        results = []
        
        if posts_df.empty:
            return results
        
        # Filter by user's club access
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            posts_df = posts_df[posts_df['club'].isin(user_club_names)]
        
        # Search in title and content
        for _, post in posts_df.iterrows():
            if (query.lower() in post['title'].lower() or 
                query.lower() in post['content'].lower()):
                
                results.append({
                    'type': '게시글',
                    'title': post['title'],
                    'content': post['content'][:100] + '...' if len(post['content']) > 100 else post['content'],
                    'author': post['author'],
                    'club': post['club'],
                    'date': post['timestamp'],
                    'icon': '📝'
                })
        
        return results
    
    def search_chat(self, query, user):
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        results = []
        
        if chat_df.empty:
            return results
        
        # Filter by user's club access
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            chat_df = chat_df[chat_df['club'].isin(user_club_names)]
        
        # Filter out deleted messages for non-admins
        if user['role'] != '선생님':
            chat_df = chat_df[chat_df['deleted'] == False]
        
        # Search in messages
        for _, message in chat_df.iterrows():
            if query.lower() in message['message'].lower():
                results.append({
                    'type': '채팅',
                    'title': f"채팅 메시지 - {message['club']}",
                    'content': message['message'],
                    'author': message['username'],
                    'club': message['club'],
                    'date': message['timestamp'],
                    'icon': '💬'
                })
        
        return results
    
    def search_assignments(self, query, user):
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        results = []
        
        if assignments_df.empty:
            return results
        
        # Filter by user's club access
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            assignments_df = assignments_df[assignments_df['club'].isin(user_club_names)]
        
        # Search in title and description
        for _, assignment in assignments_df.iterrows():
            if (query.lower() in assignment['title'].lower() or 
                query.lower() in assignment['description'].lower()):
                
                results.append({
                    'type': '과제',
                    'title': assignment['title'],
                    'content': assignment['description'][:100] + '...' if len(assignment['description']) > 100 else assignment['description'],
                    'author': assignment['creator'],
                    'club': assignment['club'],
                    'date': assignment['created_date'],
                    'icon': '📝'
                })
        
        return results
    
    def search_schedule(self, query, user):
        schedule_df = st.session_state.data_manager.load_csv('schedule')
        results = []
        
        if schedule_df.empty:
            return results
        
        # Filter by user's club access
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            schedule_df = schedule_df[schedule_df['club'].isin(user_club_names)]
        
        # Search in title and description
        for _, event in schedule_df.iterrows():
            if (query.lower() in event['title'].lower() or 
                query.lower() in str(event['description']).lower()):
                
                results.append({
                    'type': '일정',
                    'title': event['title'],
                    'content': str(event['description']),
                    'author': event['creator'],
                    'club': event['club'],
                    'date': event['date'],
                    'icon': '📅'
                })
        
        return results
    
    def search_gallery(self, query, user):
        gallery_df = st.session_state.data_manager.load_csv('galleries')
        results = []
        
        if gallery_df.empty:
            return results
        
        # Filter by user's club access
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            gallery_df = gallery_df[gallery_df['club'].isin(user_club_names)]
        
        # Search in title and description
        for _, artwork in gallery_df.iterrows():
            if (query.lower() in artwork['title'].lower() or 
                query.lower() in artwork['description'].lower()):
                
                results.append({
                    'type': '갤러리',
                    'title': artwork['title'],
                    'content': artwork['description'][:100] + '...' if len(artwork['description']) > 100 else artwork['description'],
                    'author': artwork['author'],
                    'club': artwork['club'],
                    'date': artwork['created_date'],
                    'icon': '🖼️'
                })
        
        return results
    
    def filter_by_date(self, results, start_date, end_date):
        filtered_results = []
        
        for result in results:
            try:
                # Try to parse the date
                if isinstance(result['date'], str):
                    result_date = pd.to_datetime(result['date']).date()
                else:
                    result_date = result['date']
                
                if start_date <= result_date <= end_date:
                    filtered_results.append(result)
            except:
                # If date parsing fails, include the result
                filtered_results.append(result)
        
        return filtered_results
    
    def filter_by_club(self, results, selected_clubs):
        return [result for result in results if result['club'] in selected_clubs]
    
    def filter_by_author(self, results, selected_authors):
        return [result for result in results if result['author'] in selected_authors]
    
    def display_search_results(self, results, query):
        if not results:
            st.info("필터링된 결과가 없습니다.")
            return
        
        # Group results by type
        grouped_results = {}
        for result in results:
            result_type = result['type']
            if result_type not in grouped_results:
                grouped_results[result_type] = []
            grouped_results[result_type].append(result)
        
        # Display results by type
        for result_type, type_results in grouped_results.items():
            st.markdown(f"#### {result_type} ({len(type_results)}개)")
            
            for result in type_results:
                with st.container():
                    # Highlight search terms
                    highlighted_title = self.highlight_search_terms(result['title'], query)
                    highlighted_content = self.highlight_search_terms(result['content'], query)
                    
                    st.markdown(f"""
                    <div class="club-card">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 18px; margin-right: 10px;">{result['icon']}</span>
                            <h4 style="margin: 0;">{highlighted_title}</h4>
                        </div>
                        <p>{highlighted_content}</p>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <small>👤 {result['author']} | 🏷️ {result['club']}</small>
                            <small>📅 {result['date']}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def highlight_search_terms(self, text, query):
        """Highlight search terms in text"""
        if not query or not text:
            return text
        
        # Simple highlighting - wrap matching terms in bold
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(f'<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">{query}</mark>', text)
        return highlighted