import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from auth import AuthManager
from data_manager import DataManager
from ui_components import UIComponents
from report_generator import ReportGenerator
from chat_system import ChatSystem
from assignment_system import AssignmentSystem
from quiz_system import QuizSystem
from vote_system import VoteSystem
from gallery_system import GallerySystem
from attendance_system import AttendanceSystem
from notification_system import NotificationSystem
from search_system import SearchSystem

# Configure page
st.set_page_config(
    page_title="폴라리스반 동아리 관리 시스템",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-first design
st.markdown("""
<style>
    .main > div {
        padding-top: 0.5rem;
    }
    
    /* Modern Chrome-style tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 4px;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #6c757d;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 16px;
        min-width: 80px;
        transition: all 0.2s ease;
        border: none;
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #495057;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #FF6B6B;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        border-bottom: 3px solid #FF6B6B;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 0;
    }
    
    .big-button {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 15px 25px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 12px;
        width: 100%;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .big-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    .club-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        margin: 12px 0;
        border-left: 6px solid #FF6B6B;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .club-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .role-badge {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
    
    .notification {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(255, 227, 173, 0.3);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .chat-message-own {
        background: linear-gradient(135deg, #FF6B6B, #ff8a80);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 3px 12px rgba(255, 107, 107, 0.3);
    }
    
    .chat-message-other {
        background: #f8f9fa;
        color: #333;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 70%;
        margin-right: auto;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    }
    
    /* Hide sidebar completely */
    .css-1d391kg, [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .css-18e3th9 {
        padding-top: 0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 11px;
            padding: 0 8px;
            min-width: 60px;
        }
        
        .club-card {
            padding: 16px;
            margin: 8px 0;
        }
        
        .big-button {
            padding: 12px 20px;
            font-size: 14px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'ui_components' not in st.session_state:
    st.session_state.ui_components = UIComponents()
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()
if 'chat_system' not in st.session_state:
    st.session_state.chat_system = ChatSystem()
if 'assignment_system' not in st.session_state:
    st.session_state.assignment_system = AssignmentSystem()
if 'quiz_system' not in st.session_state:
    st.session_state.quiz_system = QuizSystem()
if 'vote_system' not in st.session_state:
    st.session_state.vote_system = VoteSystem()
if 'gallery_system' not in st.session_state:
    st.session_state.gallery_system = GallerySystem()
if 'attendance_system' not in st.session_state:
    st.session_state.attendance_system = AttendanceSystem()
if 'notification_system' not in st.session_state:
    st.session_state.notification_system = NotificationSystem()
if 'search_system' not in st.session_state:
    st.session_state.search_system = SearchSystem()

def main():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🌟 폴라리스반 동아리 관리 시스템</h1>
        <p style="color: white; margin: 5px 0 0 0;">6학년 폴라리스반의 모든 동아리를 한 곳에서!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.get('logged_in', False):
        show_login()
    else:
        show_main_app()

def show_login():
    st.markdown("<h2 style='text-align: center;'>🔐 로그인</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("아이디", placeholder="아이디를 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        
        if st.button("로그인", use_container_width=True):
            user = st.session_state.auth_manager.login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.success(f"환영합니다, {user['name']}님!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")

def show_main_app():
    user = st.session_state.current_user
    
    # User info header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"""
        <div style="background-color: #e8f4fd; padding: 10px; border-radius: 8px;">
            <strong>👋 {user['name']}님</strong><br>
            <span class="role-badge">{user['role']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("로그아웃"):
            for key in list(st.session_state.keys()):
                if key not in ['auth_manager', 'data_manager', 'ui_components', 'report_generator', 'chat_system', 'assignment_system', 'quiz_system', 'vote_system', 'gallery_system', 'attendance_system', 'notification_system', 'search_system']:
                    del st.session_state[key]
            st.rerun()
    
    # Main navigation tabs
    tabs = get_user_tabs(user['role'])
    selected_tab = st.tabs(tabs)
    
    # Tab content
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            show_tab_content(tab_name, user)

def get_user_tabs(role):
    base_tabs = ["🏠 홈", "📋 게시판", "💬 채팅", "📅 일정"]
    
    if role == "선생님":
        return base_tabs + ["📝 과제", "🧠 퀴즈", "🗳️ 투표", "🖼️ 갤러리", "📅 출석", "🔔 알림", "🔍 검색", "📄 보고서", "📊 관리", "⚙️ 설정"]
    elif role in ["회장", "부회장"]:
        return base_tabs + ["📝 과제", "🧠 퀴즈", "🗳️ 투표", "🖼️ 갤러리", "📅 출석", "🔔 알림", "🔍 검색", "📄 보고서", "👥 관리"]
    elif role in ["총무", "기록부장", "디자인담당"]:
        return base_tabs + ["📝 과제", "🧠 퀴즈", "🗳️ 투표", "🖼️ 갤러리", "📅 출석", "🔔 알림", "🔍 검색", "🎯 전문"]
    else:
        return base_tabs + ["📝 과제", "🧠 퀴즈", "🗳️ 투표", "🖼️ 갤러리", "📅 출석", "🔔 알림", "🔍 검색", "👤 마이페이지"]

def show_tab_content(tab_name, user):
    if tab_name == "🏠 홈":
        show_home_tab(user)
    elif tab_name == "📋 게시판":
        show_board_tab(user)
    elif tab_name == "💬 채팅":
        show_chat_tab(user)
    elif tab_name == "📅 일정":
        show_schedule_tab(user)
    elif tab_name == "📝 과제":
        show_assignment_tab(user)
    elif tab_name == "🧠 퀴즈":
        st.session_state.quiz_system.show_quiz_interface(user)
    elif tab_name == "🗳️ 투표":
        st.session_state.vote_system.show_vote_interface(user)
    elif tab_name == "🖼️ 갤러리":
        st.session_state.gallery_system.show_gallery_interface(user)
    elif tab_name == "📅 출석":
        st.session_state.attendance_system.show_attendance_interface(user)
    elif tab_name == "🔔 알림":
        st.session_state.notification_system.show_notification_interface(user)
    elif tab_name == "🔍 검색":
        st.session_state.search_system.show_search_interface(user)
    elif tab_name == "📄 보고서":
        show_report_tab(user)
    elif tab_name == "📊 관리":
        show_admin_tab(user)
    elif tab_name == "👥 관리":
        show_management_tab(user)
    elif tab_name == "🎯 전문":
        show_specialty_tab(user)
    elif tab_name == "👤 마이페이지":
        show_mypage_tab(user)
    elif tab_name == "⚙️ 설정":
        show_settings_tab(user)

def show_home_tab(user):
    st.markdown("### 📢 공지사항")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    clubs_df = st.session_state.data_manager.load_csv('clubs')
    assignments_df = st.session_state.data_manager.load_csv('assignments')
    user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FF6B6B; margin: 0;">{len(clubs_df)}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">전체 동아리</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        my_clubs = user_clubs_df[user_clubs_df['username'] == user['username']]
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #4ECDC4; margin: 0;">{len(my_clubs)}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">내 동아리</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending_assignments = len(assignments_df[assignments_df['status'] == 'active']) if not assignments_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FFA726; margin: 0;">{pending_assignments}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">진행중 과제</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        points_df = st.session_state.data_manager.load_csv('points')
        my_points = points_df[points_df['username'] == user['username']]['points'].sum() if not points_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #AB47BC; margin: 0;">{my_points}</h2>
            <p style="margin: 5px 0 0 0; color: #666;">내 포인트</p>
        </div>
        """, unsafe_allow_html=True)
    
    # My clubs
    st.markdown("### 🎪 내 동아리")
    my_clubs_data = st.session_state.data_manager.get_user_clubs(user['username'])
    
    if my_clubs_data.empty:
        st.info("아직 가입한 동아리가 없습니다.")
    else:
        for _, club in my_clubs_data.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="club-card">
                    <h4>{club['icon']} {club['name']}</h4>
                    <p>{club['description']}</p>
                    <p><strong>회장:</strong> {club['president']}</p>
                </div>
                """, unsafe_allow_html=True)

def show_board_tab(user):
    st.markdown("### 📋 게시판")
    
    # Post creation
    if st.button("📝 새 글 작성"):
        st.session_state.show_post_form = True
    
    if st.session_state.get('show_post_form', False):
        with st.form("new_post"):
            title = st.text_input("제목")
            content = st.text_area("내용")
            club_options = ["전체"] + st.session_state.data_manager.get_user_clubs(user['username'])['club_name'].tolist()
            selected_club = st.selectbox("동아리 선택", club_options)
            
            if st.form_submit_button("게시"):
                if title and content:
                    st.session_state.data_manager.add_post(
                        user['username'], title, content, selected_club
                    )
                    st.success("글이 게시되었습니다!")
                    st.session_state.show_post_form = False
                    st.rerun()
    
    # Display posts
    posts_df = st.session_state.data_manager.load_csv('posts')
    if not posts_df.empty:
        posts_df = posts_df.sort_values('timestamp', ascending=False)
        
        for _, post in posts_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="club-card">
                    <h4>{post['title']}</h4>
                    <p>{post['content'][:200]}{'...' if len(post['content']) > 200 else ''}</p>
                    <small>👤 {post['author']} | 📅 {post['timestamp']} | 🏷️ {post['club']}</small>
                </div>
                """, unsafe_allow_html=True)

def show_chat_tab(user):
    st.session_state.chat_system.show_chat_interface(user)

def show_schedule_tab(user):
    st.markdown("### 📅 일정표")
    
    # Add schedule (for authorized users)
    if user['role'] in ['선생님', '회장', '부회장']:
        with st.expander("➕ 새 일정 추가"):
            with st.form("add_schedule"):
                title = st.text_input("일정 제목")
                description = st.text_area("설명")
                schedule_date = st.date_input("날짜")
                club_options = ["전체"] + st.session_state.data_manager.load_csv('clubs')['name'].tolist()
                selected_club = st.selectbox("대상 동아리", club_options)
                
                if st.form_submit_button("일정 추가"):
                    if title and schedule_date:
                        st.session_state.data_manager.add_schedule(
                            title, description, schedule_date, selected_club, user['username']
                        )
                        st.success("일정이 추가되었습니다!")
                        st.rerun()
    
    # Display schedule
    schedule_df = st.session_state.data_manager.load_csv('schedule')
    if not schedule_df.empty:
        schedule_df['date'] = pd.to_datetime(schedule_df['date'])
        schedule_df = schedule_df.sort_values('date')
        
        for _, event in schedule_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="club-card">
                    <h4>📅 {event['title']}</h4>
                    <p>{event['description']}</p>
                    <p><strong>날짜:</strong> {event['date'].strftime('%Y-%m-%d')}</p>
                    <p><strong>동아리:</strong> {event['club']}</p>
                </div>
                """, unsafe_allow_html=True)

def show_assignment_tab(user):
    st.session_state.assignment_system.show_assignment_interface(user)

def show_report_tab(user):
    if user['role'] in ['선생님', '회장']:
        st.session_state.report_generator.show_report_interface(user)
    else:
        st.warning("보고서 작성 권한이 없습니다.")

def show_admin_tab(user):
    if user['role'] != '선생님':
        st.warning("관리자 권한이 필요합니다.")
        return
    
    st.markdown("### 📊 관리자 대시보드")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    accounts_df = st.session_state.data_manager.load_csv('accounts')
    clubs_df = st.session_state.data_manager.load_csv('clubs')
    posts_df = st.session_state.data_manager.load_csv('posts')
    assignments_df = st.session_state.data_manager.load_csv('assignments')
    
    with col1:
        st.metric("전체 사용자", len(accounts_df))
    with col2:
        st.metric("전체 동아리", len(clubs_df))
    with col3:
        st.metric("전체 게시글", len(posts_df))
    with col4:
        st.metric("전체 과제", len(assignments_df))
    
    # Management sections
    tab1, tab2, tab3, tab4 = st.tabs(["👥 계정 관리", "🎪 동아리 관리", "📊 통계", "💾 데이터"])
    
    with tab1:
        show_account_management()
    
    with tab2:
        show_club_management()
    
    with tab3:
        show_statistics()
    
    with tab4:
        show_data_management()

def show_account_management():
    st.markdown("#### 계정 생성")
    
    with st.form("create_account"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("아이디")
            password = st.text_input("비밀번호")
            name = st.text_input("이름")
        
        with col2:
            roles = ["동아리원", "회장", "부회장", "총무", "기록부장", "디자인담당", "선생님"]
            role = st.selectbox("직급", roles)
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            club_options = clubs_df['name'].tolist() if not clubs_df.empty else []
            selected_clubs = st.multiselect("소속 동아리", club_options)
        
        if st.form_submit_button("계정 생성"):
            if username and password and name:
                success = st.session_state.data_manager.create_account(
                    username, password, name, role
                )
                if success:
                    for club in selected_clubs:
                        st.session_state.data_manager.add_user_to_club(username, club)
                    st.success(f"계정 '{username}' 생성 완료!")
                    st.rerun()
                else:
                    st.error("이미 존재하는 아이디입니다.")

    # 기존 계정 표시 및 편집
    st.markdown("#### 기존 계정")
    accounts_df = st.session_state.data_manager.load_csv('accounts')
    user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')

    if not accounts_df.empty:
        st.markdown("**계정 정보**")
        edited_accounts_df = st.data_editor(
            accounts_df[['username', 'name', 'role', 'created_date', 'password']],
            use_container_width=True,
            num_rows="dynamic",
            key="edit_accounts"
        )

        st.markdown("**소속 동아리**")
        edited_user_clubs_df = st.data_editor(
            user_clubs_df[['username', 'club_name']],
            use_container_width=True,
            num_rows="dynamic",
            key="edit_user_clubs"
        )

        if st.button("변경사항 저장"):
            st.session_state.data_manager.save_csv('accounts', edited_accounts_df)
            st.session_state.data_manager.save_csv('user_clubs', edited_user_clubs_df)
            st.success("변경사항이 저장되었습니다.")

def show_club_management():
    st.markdown("#### 동아리 생성")
    
    with st.form("create_club"):
        col1, col2 = st.columns(2)
        with col1:
            club_name = st.text_input("동아리명")
            club_icon = st.text_input("아이콘 (이모지)", value="🎯")
            description = st.text_area("설명")
        
        with col2:
            accounts_df = st.session_state.data_manager.load_csv('accounts')
            president_options = accounts_df[accounts_df['role'].isin(['회장', '선생님'])]['username'].tolist()
            president = st.selectbox("회장", president_options)
            max_members = st.number_input("최대 인원", min_value=1, value=20)
        
        if st.form_submit_button("동아리 생성"):
            if club_name and president:
                success = st.session_state.data_manager.create_club(
                    club_name, club_icon, description, president, max_members
                )
                if success:
                    st.success(f"동아리 '{club_name}' 생성 완료!")
                    st.rerun()
                else:
                    st.error("이미 존재하는 동아리명입니다.")
    
    # Club list
    st.markdown("#### 기존 동아리")
    clubs_df = st.session_state.data_manager.load_csv('clubs')
    if not clubs_df.empty:
        for _, club in clubs_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="club-card">
                        <h4>{club['icon']} {club['name']}</h4>
                        <p>{club['description']}</p>
                        <p><strong>회장:</strong> {club['president']} | <strong>최대인원:</strong> {club['max_members']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"삭제", key=f"delete_club_{club['name']}"):
                        st.session_state.data_manager.delete_club(club['name'])
                        st.success(f"동아리 '{club['name']}' 삭제 완료!")
                        st.rerun()

def show_statistics():
    st.markdown("#### 📊 활동 통계")
    
    # User activity stats
    posts_df = st.session_state.data_manager.load_csv('posts')
    if not posts_df.empty:
        post_counts = posts_df['author'].value_counts()
        st.markdown("**게시글 작성 순위**")
        st.bar_chart(post_counts.head(10))
    
    # Club member distribution
    user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
    if not user_clubs_df.empty:
        club_counts = user_clubs_df['club_name'].value_counts()
        st.markdown("**동아리별 회원 수**")
        st.bar_chart(club_counts)

def show_data_management():
    st.markdown("#### 💾 데이터 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**데이터 내보내기**")
        csv_files = [
            "accounts.csv", "clubs.csv", "user_clubs.csv", "posts.csv",
            "chat_logs.csv", "assignments.csv", "submissions.csv",
            "attendance.csv", "schedule.csv", "badges.csv", "points.csv"
        ]
        
        for csv_file in csv_files:
            if st.button(f"📁 {csv_file} 다운로드", key=f"download_{csv_file}"):
                df = st.session_state.data_manager.load_csv(csv_file.replace('.csv', ''))
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"다운로드 {csv_file}",
                    data=csv,
                    file_name=csv_file,
                    mime='text/csv',
                    key=f"dl_btn_{csv_file}"
                )
    
    with col2:
        st.markdown("**시스템 정보**")
        st.info(f"""
        - 데이터 저장 위치: ./data/
        - 총 CSV 파일 수: {len(csv_files)}
        - 백업 권장: 매주
        """)

def show_management_tab(user):
    if user['role'] not in ['회장', '부회장']:
        st.warning("관리 권한이 없습니다.")
        return
    
    st.markdown("### 👥 동아리 관리")
    
    # Get user's clubs
    my_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
    
    if my_clubs.empty:
        st.info("관리할 동아리가 없습니다.")
        return
    
    selected_club = st.selectbox("관리할 동아리 선택", my_clubs['club_name'].tolist())
    
    if selected_club:
        tab1, tab2, tab3 = st.tabs(["📊 현황", "👥 회원", "📋 활동"])
        
        with tab1:
            show_club_status(selected_club)
        
        with tab2:
            show_club_members(selected_club)
        
        with tab3:
            show_club_activities(selected_club)

def show_club_status(club_name):
    st.markdown(f"#### {club_name} 현황")
    
    # Member count
    user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
    member_count = len(user_clubs_df[user_clubs_df['club_name'] == club_name])
    
    # Posts count
    posts_df = st.session_state.data_manager.load_csv('posts')
    club_posts = len(posts_df[posts_df['club'] == club_name])
    
    # Assignments count
    assignments_df = st.session_state.data_manager.load_csv('assignments')
    club_assignments = len(assignments_df[assignments_df['club'] == club_name])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("회원 수", member_count)
    with col2:
        st.metric("게시글 수", club_posts)
    with col3:
        st.metric("과제 수", club_assignments)

def show_club_members(club_name):
    st.markdown(f"#### {club_name} 회원 관리")
    
    user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
    club_members = user_clubs_df[user_clubs_df['club_name'] == club_name]
    
    if not club_members.empty:
        accounts_df = st.session_state.data_manager.load_csv('accounts')
        member_details = club_members.merge(accounts_df, on='username')
        st.dataframe(member_details[['username', 'name', 'role']], use_container_width=True)

def show_club_activities(club_name):
    st.markdown(f"#### {club_name} 활동 관리")
    
    # Recent posts
    posts_df = st.session_state.data_manager.load_csv('posts')
    club_posts = posts_df[posts_df['club'] == club_name].sort_values('timestamp', ascending=False)
    
    if not club_posts.empty:
        st.markdown("**최근 게시글**")
        for _, post in club_posts.head(5).iterrows():
            st.markdown(f"- **{post['title']}** by {post['author']} ({post['timestamp']})")

def show_specialty_tab(user):
    st.markdown("### 🎯 전문 기능")
    
    if user['role'] == '총무':
        show_treasurer_functions()
    elif user['role'] == '기록부장':
        show_recorder_functions()
    elif user['role'] == '디자인담당':
        show_designer_functions()

def show_treasurer_functions():
    st.markdown("#### 💰 총무 전용 기능")
    
    tab1, tab2, tab3 = st.tabs(["📊 예산", "🎯 포인트", "📈 통계"])
    
    with tab1:
        st.markdown("**예산 관리**")
        st.info("예산 관리 기능 개발 예정")
    
    with tab2:
        st.markdown("**포인트 관리**")
        with st.form("award_points"):
            accounts_df = st.session_state.data_manager.load_csv('accounts')
            username = st.selectbox("대상 사용자", accounts_df['username'].tolist())
            points = st.number_input("포인트", min_value=1, value=10)
            reason = st.text_input("사유")
            
            if st.form_submit_button("포인트 지급"):
                if username and reason:
                    st.session_state.data_manager.add_points(username, points, reason)
                    st.success(f"{username}님에게 {points}포인트를 지급했습니다!")
                    st.rerun()
    
    with tab3:
        st.markdown("**포인트 통계**")
        points_df = st.session_state.data_manager.load_csv('points')
        if not points_df.empty:
            user_points = points_df.groupby('username')['points'].sum().sort_values(ascending=False)
            st.bar_chart(user_points.head(10))

def show_recorder_functions():
    st.markdown("#### 📸 기록부장 전용 기능")
    
    tab1, tab2 = st.tabs(["📷 갤러리", "📝 기록"])
    
    with tab1:
        st.markdown("**작품 갤러리**")
        st.info("갤러리 기능 개발 예정")
    
    with tab2:
        st.markdown("**활동 기록**")
        st.info("기록 관리 기능 개발 예정")

def show_designer_functions():
    st.markdown("#### 🎨 디자인담당 전용 기능")
    
    tab1, tab2 = st.tabs(["🎨 테마", "🏅 배지"])
    
    with tab1:
        st.markdown("**테마 관리**")
        st.info("테마 설정 기능 개발 예정")
    
    with tab2:
        st.markdown("**배지 디자인**")
        st.info("배지 디자인 기능 개발 예정")

def show_mypage_tab(user):
    st.markdown("### 👤 마이페이지")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="club-card">
            <h3>👤 {user['name']}</h3>
            <p><strong>아이디:</strong> {user['username']}</p>
            <p><strong>직급:</strong> {user['role']}</p>
            <p><strong>가입일:</strong> {user['created_date']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # My points
        points_df = st.session_state.data_manager.load_csv('points')
        my_points = points_df[points_df['username'] == user['username']]['points'].sum() if not points_df.empty else 0
        
        # My clubs
        my_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        
        # My posts
        posts_df = st.session_state.data_manager.load_csv('posts')
        my_posts = len(posts_df[posts_df['author'] == user['username']]) if not posts_df.empty else 0
        
        st.metric("총 포인트", my_points)
        st.metric("소속 동아리", len(my_clubs))
        st.metric("작성 게시글", my_posts)
    
    # Recent activity
    st.markdown("#### 📋 최근 활동")
    
    # My recent posts
    if not posts_df.empty:
        my_recent_posts = posts_df[posts_df['author'] == user['username']].sort_values('timestamp', ascending=False).head(5)
        if not my_recent_posts.empty:
            st.markdown("**최근 게시글**")
            for _, post in my_recent_posts.iterrows():
                st.markdown(f"- **{post['title']}** ({post['timestamp']})")

def show_settings_tab(user):
    if user['role'] != '선생님':
        st.warning("설정 권한이 없습니다.")
        return
    
    st.markdown("### ⚙️ 시스템 설정")
    
    tab1, tab2, tab3 = st.tabs(["🎨 테마", "🔔 알림", "🔐 보안"])
    
    with tab1:
        st.markdown("#### 테마 설정")
        st.info("테마 설정 기능 개발 예정")
    
    with tab2:
        st.markdown("#### 알림 설정")
        st.info("알림 설정 기능 개발 예정")
    
    with tab3:
        st.markdown("#### 보안 설정")
        st.info("보안 설정 기능 개발 예정")

if __name__ == "__main__":
    main()
