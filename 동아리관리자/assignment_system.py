import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

class AssignmentSystem:
    def __init__(self):
        pass
    
    def show_assignment_interface(self, user):
        st.markdown("### 📝 과제")
        
        if user['role'] in ['선생님', '회장', '부회장']:
            tab1, tab2, tab3 = st.tabs(["📋 과제 목록", "➕ 과제 생성", "📊 제출 현황"])
        else:
            tab1, tab2 = st.tabs(["📋 과제 목록", "📤 내 제출물"])
        
        with tab1:
            self.show_assignment_list(user)
        
        if user['role'] in ['선생님', '회장', '부회장']:
            with tab2:
                self.show_assignment_creation(user)
            
            with tab3:
                self.show_submission_status(user)
        else:
            with tab2:
                self.show_my_submissions(user)
    
    def show_assignment_list(self, user):
        st.markdown("#### 📋 과제 목록")
        
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        
        if assignments_df.empty:
            st.info("등록된 과제가 없습니다.")
            return
        
        # Filter assignments based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            assignments_df = assignments_df[
                (assignments_df['club'].isin(user_club_names)) |
                (assignments_df['creator'] == user['username'])
            ]
        
        # Sort by due date
        assignments_df['due_date'] = pd.to_datetime(assignments_df['due_date'])
        assignments_df = assignments_df.sort_values('due_date')
        
        for _, assignment in assignments_df.iterrows():
            self.show_assignment_card(assignment, user)
    
    def show_assignment_card(self, assignment, user):
        # Calculate days until due
        due_date = pd.to_datetime(assignment['due_date'])
        days_left = (due_date.date() - date.today()).days
        
        # Status styling
        if days_left < 0:
            status_color = "#dc3545"
            status_text = f"마감됨 ({abs(days_left)}일 전)"
        elif days_left == 0:
            status_color = "#fd7e14"
            status_text = "오늘 마감"
        elif days_left <= 3:
            status_color = "#ffc107"
            status_text = f"마감 {days_left}일 전"
        else:
            status_color = "#28a745"
            status_text = f"마감 {days_left}일 전"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="club-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <h4>{assignment['title']}</h4>
                        <span style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; white-space: nowrap;">
                            {status_text}
                        </span>
                    </div>
                    <p>{assignment['description'][:200]}{'...' if len(assignment['description']) > 200 else ''}</p>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p><strong>🏷️ 동아리:</strong> {assignment['club']}</p>
                        <p><strong>📅 마감일:</strong> {assignment['due_date'].strftime('%Y-%m-%d')}</p>
                        <p><strong>👤 출제자:</strong> {assignment['creator']}</p>
                        <p><strong>📊 상태:</strong> {assignment['status']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Check if user has submitted
                submissions_df = st.session_state.data_manager.load_csv('submissions')
                user_submission = submissions_df[
                    (submissions_df['assignment_id'] == assignment['id']) &
                    (submissions_df['username'] == user['username'])
                ]
                
                if not user_submission.empty:
                    st.success("✅ 제출완료")
                    if st.button("📝 수정", key=f"edit_submission_{assignment['id']}"):
                        st.session_state[f'edit_submission_{assignment["id"]}'] = True
                else:
                    if days_left >= 0:  # Not overdue
                        if st.button("📤 제출", key=f"submit_{assignment['id']}"):
                            st.session_state[f'show_submission_{assignment["id"]}'] = True
                    else:
                        st.error("⏰ 마감됨")
                
                # Admin controls
                if user['role'] in ['선생님', '회장'] or user['username'] == assignment['creator']:
                    if st.button("📊 현황", key=f"status_{assignment['id']}"):
                        st.session_state[f'show_status_{assignment["id"]}'] = True
            
            # Show submission form if requested
            if st.session_state.get(f'show_submission_{assignment["id"]}', False):
                self.show_submission_form(assignment, user)
            
            # Show edit form if requested
            if st.session_state.get(f'edit_submission_{assignment["id"]}', False):
                existing_submission = user_submission.iloc[0]
                self.show_submission_form(assignment, user, existing_submission)
            
            # Show status if requested
            if st.session_state.get(f'show_status_{assignment["id"]}', False):
                self.show_assignment_status(assignment, user)
    
    def show_submission_form(self, assignment, user, existing_submission=None):
        is_edit = existing_submission is not None
        form_title = "✏️ 제출물 수정" if is_edit else "📤 과제 제출"
        
        with st.expander(form_title, expanded=True):
            with st.form(f"submission_form_{assignment['id']}"):
                st.markdown(f"**과제:** {assignment['title']}")
                st.markdown(f"**마감일:** {assignment['due_date']}")
                
                # Pre-fill with existing data if editing
                default_content = existing_submission['content'] if is_edit else ""
                
                content = st.text_area(
                    "제출 내용", 
                    value=default_content,
                    height=150,
                    placeholder="과제 답안이나 설명을 작성해주세요..."
                )
                
                uploaded_file = st.file_uploader(
                    "파일 첨부 (선택사항)", 
                    type=['txt', 'pdf', 'doc', 'docx', 'jpg', 'png', 'zip']
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submit_text = "수정 완료" if is_edit else "제출하기"
                    if st.form_submit_button(submit_text, use_container_width=True):
                        if content.strip():
                            if is_edit:
                                success = self.update_submission(
                                    existing_submission['id'], content, uploaded_file
                                )
                            else:
                                success = self.create_submission(
                                    assignment['id'], user['username'], content, uploaded_file
                                )
                            
                            if success:
                                action = "수정" if is_edit else "제출"
                                st.success(f"과제가 성공적으로 {action}되었습니다!")
                                # Clear session state
                                key = f'edit_submission_{assignment["id"]}' if is_edit else f'show_submission_{assignment["id"]}'
                                st.session_state[key] = False
                                st.rerun()
                            else:
                                st.error("제출 중 오류가 발생했습니다.")
                        else:
                            st.error("제출 내용을 입력해주세요.")
                
                with col2:
                    if st.form_submit_button("취소", use_container_width=True):
                        key = f'edit_submission_{assignment["id"]}' if is_edit else f'show_submission_{assignment["id"]}'
                        st.session_state[key] = False
                        st.rerun()
    
    def create_submission(self, assignment_id, username, content, uploaded_file):
        try:
            file_path = None
            if uploaded_file is not None:
                # In a real implementation, you would save the file
                file_path = f"uploads/{uploaded_file.name}"
            
            return st.session_state.data_manager.add_submission(
                assignment_id, username, content, file_path
            )
        except Exception as e:
            print(f"Submission creation error: {e}")
            return False
    
    def update_submission(self, submission_id, content, uploaded_file):
        try:
            submissions_df = st.session_state.data_manager.load_csv('submissions')
            
            # Update the submission
            submissions_df.loc[submissions_df['id'] == submission_id, 'content'] = content
            submissions_df.loc[submissions_df['id'] == submission_id, 'submitted_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if uploaded_file is not None:
                file_path = f"uploads/{uploaded_file.name}"
                submissions_df.loc[submissions_df['id'] == submission_id, 'file_path'] = file_path
            
            return st.session_state.data_manager.save_csv('submissions', submissions_df)
        except Exception as e:
            print(f"Submission update error: {e}")
            return False
    
    def show_assignment_creation(self, user):
        st.markdown("#### ➕ 새 과제 생성")
        
        with st.form("create_assignment"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("과제 제목", placeholder="예: 첫 번째 코딩 과제")
                
                # Club selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist()
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist()
                
                selected_club = st.selectbox("대상 동아리", club_options)
            
            with col2:
                due_date = st.date_input(
                    "마감일", 
                    min_value=date.today(),
                    value=date.today() + timedelta(days=7)
                )
                
                assignment_type = st.selectbox("과제 유형", [
                    "개인 과제", "팀 과제", "프로젝트", "발표", "실습", "기타"
                ])
            
            description = st.text_area(
                "과제 설명", 
                height=150,
                placeholder="과제의 상세 내용과 요구사항을 작성해주세요..."
            )
            
            # Additional options
            col1, col2 = st.columns(2)
            
            with col1:
                allow_late = st.checkbox("늦은 제출 허용", value=False)
                max_score = st.number_input("만점", min_value=1, value=100)
            
            with col2:
                auto_grade = st.checkbox("자동 채점", value=False)
                difficulty = st.selectbox("난이도", ["쉬움", "보통", "어려움"])
            
            if st.form_submit_button("📝 과제 생성", use_container_width=True):
                if title and description and selected_club:
                    success = st.session_state.data_manager.add_assignment(
                        title, description, selected_club, due_date.strftime('%Y-%m-%d'), user['username']
                    )
                    
                    if success:
                        st.success("과제가 성공적으로 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("과제 생성 중 오류가 발생했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")
    
    def show_submission_status(self, user):
        st.markdown("#### 📊 제출 현황")
        
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        
        if assignments_df.empty:
            st.info("생성된 과제가 없습니다.")
            return
        
        # Filter assignments by user's authority
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            assignments_df = assignments_df[
                (assignments_df['club'].isin(user_club_names)) |
                (assignments_df['creator'] == user['username'])
            ]
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_assignments = len(assignments_df)
        total_submissions = len(submissions_df)
        unique_submitters = submissions_df['username'].nunique() if not submissions_df.empty else 0
        
        with col1:
            st.metric("총 과제 수", total_assignments)
        with col2:
            st.metric("총 제출물", total_submissions)
        with col3:
            st.metric("제출 학생 수", unique_submitters)
        with col4:
            avg_submissions = total_submissions / max(total_assignments, 1)
            st.metric("평균 제출률", f"{avg_submissions:.1f}")
        
        # Detailed assignment status
        st.markdown("##### 과제별 제출 현황")
        
        for _, assignment in assignments_df.iterrows():
            assignment_submissions = submissions_df[submissions_df['assignment_id'] == assignment['id']]
            submission_count = len(assignment_submissions)
            
            # Get potential submitters (club members)
            user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
            if assignment['club'] == "전체":
                potential_submitters = len(st.session_state.data_manager.load_csv('accounts'))
            else:
                potential_submitters = len(user_clubs_df[user_clubs_df['club_name'] == assignment['club']])
            
            submission_rate = (submission_count / max(potential_submitters, 1)) * 100
            
            with st.container():
                st.markdown(f"""
                <div class="club-card">
                    <h4>{assignment['title']}</h4>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span><strong>동아리:</strong> {assignment['club']}</span>
                        <span><strong>마감일:</strong> {assignment['due_date']}</span>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                        <p><strong>제출 현황:</strong> {submission_count}/{potential_submitters} ({submission_rate:.1f}%)</p>
                        <div style="background-color: #e9ecef; border-radius: 10px; height: 10px; overflow: hidden;">
                            <div style="background-color: #28a745; height: 100%; width: {submission_rate}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show submission details
                if st.button(f"📋 제출물 보기", key=f"view_submissions_{assignment['id']}"):
                    st.session_state[f'show_submissions_{assignment["id"]}'] = True
                
                if st.session_state.get(f'show_submissions_{assignment["id"]}', False):
                    self.show_assignment_submissions(assignment, assignment_submissions)
    
    def show_assignment_submissions(self, assignment, submissions):
        with st.expander(f"📋 {assignment['title']} 제출물", expanded=True):
            if submissions.empty:
                st.info("아직 제출된 과제가 없습니다.")
            else:
                for _, submission in submissions.iterrows():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;">
                                <strong>👤 {submission['username']}</strong><br>
                                <p>{submission['content'][:150]}{'...' if len(submission['content']) > 150 else ''}</p>
                                <small>📅 제출일: {submission['submitted_date']}</small>
                                {f"<br><small>📎 첨부파일: {submission['file_path']}</small>" if submission['file_path'] else ""}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            score = st.number_input(
                                "점수", 
                                min_value=0, 
                                max_value=100, 
                                value=int(submission['score']) if submission['score'] else 0,
                                key=f"score_{submission['id']}"
                            )
                            
                            if st.button("💾 저장", key=f"save_score_{submission['id']}"):
                                self.update_submission_score(submission['id'], score)
                                st.success("점수가 저장되었습니다!")
                                st.rerun()
            
            if st.button("닫기", key=f"close_submissions_{assignment['id']}"):
                st.session_state[f'show_submissions_{assignment["id"]}'] = False
                st.rerun()
    
    def update_submission_score(self, submission_id, score):
        try:
            submissions_df = st.session_state.data_manager.load_csv('submissions')
            submissions_df.loc[submissions_df['id'] == submission_id, 'score'] = score
            return st.session_state.data_manager.save_csv('submissions', submissions_df)
        except Exception as e:
            print(f"Score update error: {e}")
            return False
    
    def show_my_submissions(self, user):
        st.markdown("#### 📤 내 제출물")
        
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        my_submissions = submissions_df[submissions_df['username'] == user['username']]
        
        if my_submissions.empty:
            st.info("제출한 과제가 없습니다.")
            return
        
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        
        # Merge with assignment data
        submission_details = my_submissions.merge(
            assignments_df, 
            left_on='assignment_id', 
            right_on='id', 
            suffixes=('', '_assignment')
        )
        
        for _, submission in submission_details.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="club-card">
                    <h4>{submission['title']}</h4>
                    <p><strong>동아리:</strong> {submission['club']}</p>
                    <p><strong>제출일:</strong> {submission['submitted_date']}</p>
                    <p><strong>점수:</strong> {submission['score']}/100</p>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p><strong>제출 내용:</strong></p>
                        <p>{submission['content']}</p>
                        {f"<p><strong>첨부파일:</strong> {submission['file_path']}</p>" if submission['file_path'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def show_assignment_status(self, assignment, user):
        with st.expander(f"📊 {assignment['title']} 제출 현황", expanded=True):
            submissions_df = st.session_state.data_manager.load_csv('submissions')
            assignment_submissions = submissions_df[submissions_df['assignment_id'] == assignment['id']]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 제출물", len(assignment_submissions))
            
            with col2:
                avg_score = assignment_submissions['score'].mean() if not assignment_submissions.empty else 0
                st.metric("평균 점수", f"{avg_score:.1f}")
            
            with col3:
                graded_count = len(assignment_submissions[assignment_submissions['score'] > 0])
                st.metric("채점 완료", graded_count)
            
            if not assignment_submissions.empty:
                st.markdown("**제출자 목록:**")
                for username in assignment_submissions['username'].unique():
                    st.write(f"- {username}")
            
            if st.button("닫기", key=f"close_status_{assignment['id']}"):
                st.session_state[f'show_status_{assignment["id"]}'] = False
                st.rerun()
