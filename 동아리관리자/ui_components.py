import streamlit as st
import pandas as pd

class UIComponents:
    def __init__(self):
        pass
    
    def show_club_card(self, club_data):
        """Display a club information card"""
        st.markdown(f"""
        <div class="club-card">
            <h4>{club_data['icon']} {club_data['name']}</h4>
            <p>{club_data['description']}</p>
            <p><strong>회장:</strong> {club_data['president']}</p>
            <p><strong>최대 인원:</strong> {club_data['max_members']}명</p>
            <p><small>생성일: {club_data['created_date']}</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_post_card(self, post_data):
        """Display a post card"""
        st.markdown(f"""
        <div class="club-card">
            <h4>{post_data['title']}</h4>
            <p>{post_data['content'][:200]}{'...' if len(post_data['content']) > 200 else ''}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <small>👤 {post_data['author']} | 🏷️ {post_data['club']}</small>
                <small>📅 {post_data['timestamp']}</small>
            </div>
            <div style="margin-top: 10px;">
                <span style="background-color: #e3f2fd; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                    👍 {post_data['likes']} 좋아요
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_assignment_card(self, assignment_data):
        """Display an assignment card"""
        status_color = "#28a745" if assignment_data['status'] == 'active' else "#6c757d"
        status_text = "진행중" if assignment_data['status'] == 'active' else "완료"
        
        st.markdown(f"""
        <div class="club-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <h4>{assignment_data['title']}</h4>
                <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 12px;">
                    {status_text}
                </span>
            </div>
            <p>{assignment_data['description'][:150]}{'...' if len(assignment_data['description']) > 150 else ''}</p>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <p><strong>🏷️ 동아리:</strong> {assignment_data['club']}</p>
                <p><strong>📅 마감일:</strong> {assignment_data['due_date']}</p>
                <p><strong>👤 출제자:</strong> {assignment_data['creator']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_user_stats(self, username, data_manager):
        """Display user statistics"""
        points_df = data_manager.load_csv('points')
        posts_df = data_manager.load_csv('posts')
        submissions_df = data_manager.load_csv('submissions')
        user_clubs_df = data_manager.load_csv('user_clubs')
        
        # Calculate stats
        total_points = points_df[points_df['username'] == username]['points'].sum() if not points_df.empty else 0
        post_count = len(posts_df[posts_df['author'] == username]) if not posts_df.empty else 0
        submission_count = len(submissions_df[submissions_df['username'] == username]) if not submissions_df.empty else 0
        club_count = len(user_clubs_df[user_clubs_df['username'] == username]) if not user_clubs_df.empty else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 포인트", total_points)
        with col2:
            st.metric("작성 글", post_count)
        with col3:
            st.metric("과제 제출", submission_count)
        with col4:
            st.metric("소속 동아리", club_count)
    
    def show_notification(self, message, type="info"):
        """Display a notification"""
        colors = {
            "info": "#d1ecf1",
            "success": "#d4edda",
            "warning": "#fff3cd",
            "error": "#f8d7da"
        }
        
        color = colors.get(type, colors["info"])
        
        st.markdown(f"""
        <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 10px 0;">
            {message}
        </div>
        """, unsafe_allow_html=True)
    
    def show_role_badge(self, role):
        """Display a role badge"""
        role_colors = {
            "선생님": "#dc3545",
            "회장": "#fd7e14",
            "부회장": "#20c997",
            "총무": "#6f42c1",
            "기록부장": "#0dcaf0",
            "디자인담당": "#e83e8c",
            "동아리원": "#6c757d"
        }
        
        color = role_colors.get(role, "#6c757d")
        
        return f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{role}</span>'
    
    def show_club_member_list(self, club_name, data_manager):
        """Display club member list"""
        user_clubs_df = data_manager.load_csv('user_clubs')
        accounts_df = data_manager.load_csv('accounts')
        
        if user_clubs_df.empty or accounts_df.empty:
            st.info("회원 정보가 없습니다.")
            return
        
        club_members = user_clubs_df[user_clubs_df['club_name'] == club_name]
        member_details = club_members.merge(accounts_df, on='username', how='left')
        
        if member_details.empty:
            st.info("동아리 회원이 없습니다.")
            return
        
        st.markdown(f"#### {club_name} 회원 목록")
        
        for _, member in member_details.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin: 5px 0;">
                <div>
                    <strong>{member['name']}</strong> ({member['username']})
                </div>
                <div>
                    {self.show_role_badge(member['role'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_activity_timeline(self, username, data_manager, limit=10):
        """Display user activity timeline"""
        posts_df = data_manager.load_csv('posts')
        submissions_df = data_manager.load_csv('submissions')
        chat_logs_df = data_manager.load_csv('chat_logs')
        
        activities = []
        
        # Add posts
        if not posts_df.empty:
            user_posts = posts_df[posts_df['author'] == username]
            for _, post in user_posts.iterrows():
                activities.append({
                    'type': '게시글',
                    'title': post['title'],
                    'timestamp': post['timestamp'],
                    'icon': '📝'
                })
        
        # Add submissions
        if not submissions_df.empty:
            user_submissions = submissions_df[submissions_df['username'] == username]
            for _, submission in user_submissions.iterrows():
                activities.append({
                    'type': '과제 제출',
                    'title': f"과제 #{submission['assignment_id']} 제출",
                    'timestamp': submission['submitted_date'],
                    'icon': '📋'
                })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]
        
        if not activities:
            st.info("최근 활동이 없습니다.")
            return
        
        st.markdown("#### 📈 최근 활동")
        
        for activity in activities:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 8px; border-left: 3px solid #FF6B6B; margin: 5px 0; background-color: #f8f9fa;">
                <span style="margin-right: 10px; font-size: 18px;">{activity['icon']}</span>
                <div>
                    <strong>{activity['type']}</strong><br>
                    <small>{activity['title']} - {activity['timestamp']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
