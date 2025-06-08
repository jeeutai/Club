import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import random

class QuizSystem:
    def __init__(self):
        pass
    
    def show_quiz_interface(self, user):
        st.markdown("### 🧠 퀴즈 시스템")
        
        if user['role'] in ['선생님', '회장', '부회장']:
            tab1, tab2, tab3 = st.tabs(["🎯 퀴즈 참여", "➕ 퀴즈 생성", "📊 퀴즈 관리"])
            
            with tab1:
                self.show_quiz_list(user)
            
            with tab2:
                self.show_quiz_creation(user)
            
            with tab3:
                self.show_quiz_management(user)
        else:
            tab1, tab2 = st.tabs(["🎯 퀴즈 참여", "🏆 내 기록"])
            
            with tab1:
                self.show_quiz_list(user)
            
            with tab2:
                self.show_my_quiz_records(user)
    
    def show_quiz_list(self, user):
        st.markdown("#### 🎯 퀴즈 참여")
        
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        
        if quizzes_df.empty:
            st.info("아직 생성된 퀴즈가 없습니다.")
            return
        
        # Filter quizzes based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            quizzes_df = quizzes_df[quizzes_df['club'].isin(user_club_names)]
        
        # Sort by creation date
        quizzes_df = quizzes_df.sort_values('created_date', ascending=False)
        
        for _, quiz in quizzes_df.iterrows():
            self.show_quiz_card(quiz, user)
    
    def show_quiz_card(self, quiz, user):
        # Check if user has attempted this quiz
        quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
        user_attempt = quiz_attempts_df[
            (quiz_attempts_df['quiz_id'] == quiz['id']) &
            (quiz_attempts_df['username'] == user['username'])
        ]
        
        has_attempted = not user_attempt.empty
        best_score = user_attempt['score'].max() if has_attempted else 0
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                status_color = "#28a745" if not has_attempted else "#6c757d"
                status_text = "도전 가능" if not has_attempted else f"최고점: {best_score}점"
                
                st.markdown(f"""
                <div class="club-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <h4>🧠 {quiz['title']}</h4>
                        <span style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                            {status_text}
                        </span>
                    </div>
                    <p>{quiz['description']}</p>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p><strong>🏷️ 동아리:</strong> {quiz['club']}</p>
                        <p><strong>📊 난이도:</strong> {quiz['difficulty']}</p>
                        <p><strong>⏱️ 제한시간:</strong> {quiz['time_limit']}분</p>
                        <p><strong>👤 출제자:</strong> {quiz['creator']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🎯 도전", key=f"take_quiz_{quiz['id']}"):
                    st.session_state[f'taking_quiz_{quiz["id"]}'] = True
                
                if has_attempted and st.button("📊 기록", key=f"view_record_{quiz['id']}"):
                    st.session_state[f'show_record_{quiz["id"]}'] = True
            
            # Show quiz taking interface
            if st.session_state.get(f'taking_quiz_{quiz["id"]}', False):
                self.show_quiz_taking_interface(quiz, user)
            
            # Show quiz record
            if st.session_state.get(f'show_record_{quiz["id"]}', False):
                self.show_quiz_record(quiz, user)
    
    def show_quiz_taking_interface(self, quiz, user):
        with st.expander("🧠 퀴즈 도전", expanded=True):
            try:
                questions = json.loads(quiz['questions'])
                
                st.markdown(f"### {quiz['title']}")
                st.markdown(f"**제한시간:** {quiz['time_limit']}분")
                st.markdown("---")
                
                with st.form(f"quiz_form_{quiz['id']}"):
                    answers = {}
                    
                    for i, question in enumerate(questions):
                        st.markdown(f"**문제 {i+1}:** {question['question']}")
                        
                        if question['type'] == 'multiple_choice':
                            answers[i] = st.radio(
                                f"선택하세요 (문제 {i+1})",
                                question['options'],
                                key=f"q_{quiz['id']}_{i}"
                            )
                        elif question['type'] == 'short_answer':
                            answers[i] = st.text_input(
                                f"답안을 입력하세요 (문제 {i+1})",
                                key=f"q_{quiz['id']}_{i}"
                            )
                        
                        st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("📝 제출", use_container_width=True):
                            score = self.calculate_quiz_score(questions, answers)
                            self.save_quiz_attempt(quiz['id'], user['username'], answers, score)
                            
                            st.success(f"퀴즈 완료! 점수: {score}/{len(questions)}")
                            st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ 취소", use_container_width=True):
                            st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                            st.rerun()
            
            except Exception as e:
                st.error(f"퀴즈 로딩 중 오류가 발생했습니다: {e}")
    
    def calculate_quiz_score(self, questions, answers):
        score = 0
        for i, question in enumerate(questions):
            if i in answers:
                user_answer = answers[i]
                correct_answer = question['correct_answer']
                
                if question['type'] == 'multiple_choice':
                    if user_answer == correct_answer:
                        score += 1
                elif question['type'] == 'short_answer':
                    if user_answer.strip().lower() == correct_answer.strip().lower():
                        score += 1
        
        return score
    
    def save_quiz_attempt(self, quiz_id, username, answers, score):
        quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
        
        new_id = len(quiz_attempts_df) + 1
        new_attempt = {
            'id': new_id,
            'quiz_id': quiz_id,
            'username': username,
            'answers': json.dumps(answers),
            'score': score,
            'attempted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        quiz_attempts_df = pd.concat([quiz_attempts_df, pd.DataFrame([new_attempt])], ignore_index=True)
        st.session_state.data_manager.save_csv('quiz_attempts', quiz_attempts_df)
    
    def show_quiz_creation(self, user):
        st.markdown("#### ➕ 퀴즈 생성")
        
        with st.form("create_quiz"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("퀴즈 제목", placeholder="예: 코딩 기초 퀴즈")
                description = st.text_area("설명", placeholder="퀴즈에 대한 설명을 입력하세요")
                
                # Club selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist()
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist()
                
                selected_club = st.selectbox("대상 동아리", club_options)
            
            with col2:
                difficulty = st.selectbox("난이도", ["쉬움", "보통", "어려움"])
                time_limit = st.number_input("제한시간 (분)", min_value=1, value=10)
                num_questions = st.number_input("문제 수", min_value=1, max_value=20, value=5)
            
            st.markdown("#### 📝 문제 작성")
            
            questions = []
            for i in range(num_questions):
                st.markdown(f"**문제 {i+1}**")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    question_text = st.text_input(f"문제 {i+1}", key=f"question_{i}")
                
                with col2:
                    question_type = st.selectbox(f"유형", ["multiple_choice", "short_answer"], key=f"type_{i}")
                
                if question_type == "multiple_choice":
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        option1 = st.text_input(f"선택지 1", key=f"opt1_{i}")
                    with col2:
                        option2 = st.text_input(f"선택지 2", key=f"opt2_{i}")
                    with col3:
                        option3 = st.text_input(f"선택지 3", key=f"opt3_{i}")
                    with col4:
                        option4 = st.text_input(f"선택지 4", key=f"opt4_{i}")
                    
                    options = [opt for opt in [option1, option2, option3, option4] if opt]
                    correct_answer = st.selectbox(f"정답", options, key=f"correct_{i}")
                    
                    if question_text and len(options) >= 2:
                        questions.append({
                            'question': question_text,
                            'type': question_type,
                            'options': options,
                            'correct_answer': correct_answer
                        })
                
                elif question_type == "short_answer":
                    correct_answer = st.text_input(f"정답", key=f"answer_{i}")
                    
                    if question_text and correct_answer:
                        questions.append({
                            'question': question_text,
                            'type': question_type,
                            'correct_answer': correct_answer
                        })
                
                st.markdown("---")
            
            if st.form_submit_button("🧠 퀴즈 생성", use_container_width=True):
                if title and description and questions:
                    success = self.create_quiz(
                        title, description, selected_club, difficulty,
                        time_limit, questions, user['username']
                    )
                    
                    if success:
                        st.success("퀴즈가 성공적으로 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("퀴즈 생성 중 오류가 발생했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")
    
    def create_quiz(self, title, description, club, difficulty, time_limit, questions, creator):
        try:
            quizzes_df = st.session_state.data_manager.load_csv('quizzes')
            
            new_id = len(quizzes_df) + 1
            new_quiz = {
                'id': new_id,
                'title': title,
                'description': description,
                'club': club,
                'difficulty': difficulty,
                'time_limit': time_limit,
                'questions': json.dumps(questions),
                'creator': creator,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            quizzes_df = pd.concat([quizzes_df, pd.DataFrame([new_quiz])], ignore_index=True)
            return st.session_state.data_manager.save_csv('quizzes', quizzes_df)
        
        except Exception as e:
            print(f"Quiz creation error: {e}")
            return False
    
    def show_quiz_management(self, user):
        st.markdown("#### 📊 퀴즈 관리")
        
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
        
        if quizzes_df.empty:
            st.info("생성된 퀴즈가 없습니다.")
            return
        
        # Filter quizzes by user's authority
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            quizzes_df = quizzes_df[
                (quizzes_df['club'].isin(user_club_names)) |
                (quizzes_df['creator'] == user['username'])
            ]
        
        # Quiz statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_quizzes = len(quizzes_df)
        total_attempts = len(quiz_attempts_df)
        unique_participants = quiz_attempts_df['username'].nunique() if not quiz_attempts_df.empty else 0
        
        with col1:
            st.metric("총 퀴즈", total_quizzes)
        with col2:
            st.metric("총 시도", total_attempts)
        with col3:
            st.metric("참여자", unique_participants)
        with col4:
            avg_score = quiz_attempts_df['score'].mean() if not quiz_attempts_df.empty else 0
            st.metric("평균 점수", f"{avg_score:.1f}")
        
        # Quiz list with management options
        st.markdown("##### 퀴즈 목록")
        
        for _, quiz in quizzes_df.iterrows():
            quiz_attempts = quiz_attempts_df[quiz_attempts_df['quiz_id'] == quiz['id']]
            attempt_count = len(quiz_attempts)
            avg_score = quiz_attempts['score'].mean() if not quiz_attempts.empty else 0
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="club-card">
                        <h4>🧠 {quiz['title']}</h4>
                        <p>{quiz['description']}</p>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span><strong>동아리:</strong> {quiz['club']}</span>
                            <span><strong>난이도:</strong> {quiz['difficulty']}</span>
                            <span><strong>시도:</strong> {attempt_count}회</span>
                            <span><strong>평균:</strong> {avg_score:.1f}점</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📊 상세", key=f"detail_quiz_{quiz['id']}"):
                        st.session_state[f'show_quiz_detail_{quiz["id"]}'] = True
                    
                    if user['role'] == '선생님' or quiz['creator'] == user['username']:
                        if st.button("🗑️ 삭제", key=f"delete_quiz_{quiz['id']}"):
                            self.delete_quiz(quiz['id'])
                            st.success("퀴즈가 삭제되었습니다!")
                            st.rerun()
                
                # Show quiz details
                if st.session_state.get(f'show_quiz_detail_{quiz["id"]}', False):
                    with st.expander("퀴즈 상세 정보", expanded=True):
                        self.show_quiz_details(quiz, quiz_attempts)
                        if st.button("닫기", key=f"close_detail_{quiz['id']}"):
                            st.session_state[f'show_quiz_detail_{quiz["id"]}'] = False
                            st.rerun()
    
    def show_quiz_details(self, quiz, attempts):
        st.markdown(f"### {quiz['title']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**동아리:** {quiz['club']}")
        with col2:
            st.info(f"**난이도:** {quiz['difficulty']}")
        with col3:
            st.info(f"**제한시간:** {quiz['time_limit']}분")
        
        # Attempt statistics
        if not attempts.empty:
            st.markdown("#### 📊 시도 통계")
            
            # Score distribution
            score_counts = attempts['score'].value_counts().sort_index()
            st.bar_chart(score_counts)
            
            # Recent attempts
            st.markdown("#### 📋 최근 시도")
            recent_attempts = attempts.sort_values('attempted_date', ascending=False).head(10)
            
            for _, attempt in recent_attempts.iterrows():
                st.markdown(f"- **{attempt['username']}**: {attempt['score']}점 ({attempt['attempted_date']})")
        else:
            st.info("아직 시도한 사용자가 없습니다.")
    
    def show_quiz_record(self, quiz, user):
        with st.expander("📊 퀴즈 기록", expanded=True):
            quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
            user_attempts = quiz_attempts_df[
                (quiz_attempts_df['quiz_id'] == quiz['id']) &
                (quiz_attempts_df['username'] == user['username'])
            ].sort_values('attempted_date', ascending=False)
            
            if not user_attempts.empty:
                st.markdown(f"### {quiz['title']} - 내 기록")
                
                best_score = user_attempts['score'].max()
                attempt_count = len(user_attempts)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("최고 점수", f"{best_score}점")
                with col2:
                    st.metric("시도 횟수", f"{attempt_count}회")
                
                st.markdown("#### 📋 시도 기록")
                for _, attempt in user_attempts.iterrows():
                    st.markdown(f"- **{attempt['score']}점** - {attempt['attempted_date']}")
            
            if st.button("닫기", key=f"close_record_{quiz['id']}"):
                st.session_state[f'show_record_{quiz["id"]}'] = False
                st.rerun()
    
    def show_my_quiz_records(self, user):
        st.markdown("#### 🏆 내 퀴즈 기록")
        
        quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        
        my_attempts = quiz_attempts_df[quiz_attempts_df['username'] == user['username']]
        
        if my_attempts.empty:
            st.info("아직 참여한 퀴즈가 없습니다.")
            return
        
        # Overall statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("참여 퀴즈", my_attempts['quiz_id'].nunique())
        with col2:
            st.metric("총 시도", len(my_attempts))
        with col3:
            avg_score = my_attempts['score'].mean()
            st.metric("평균 점수", f"{avg_score:.1f}")
        
        # Quiz-wise records
        st.markdown("##### 퀴즈별 기록")
        
        for quiz_id in my_attempts['quiz_id'].unique():
            quiz_info = quizzes_df[quizzes_df['id'] == quiz_id].iloc[0]
            quiz_attempts = my_attempts[my_attempts['quiz_id'] == quiz_id]
            
            best_score = quiz_attempts['score'].max()
            attempt_count = len(quiz_attempts)
            
            st.markdown(f"""
            <div class="club-card">
                <h4>🧠 {quiz_info['title']}</h4>
                <p><strong>최고 점수:</strong> {best_score}점 | <strong>시도 횟수:</strong> {attempt_count}회</p>
                <p><strong>동아리:</strong> {quiz_info['club']} | <strong>난이도:</strong> {quiz_info['difficulty']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def delete_quiz(self, quiz_id):
        try:
            # Delete quiz
            quizzes_df = st.session_state.data_manager.load_csv('quizzes')
            quizzes_df = quizzes_df[quizzes_df['id'] != quiz_id]
            st.session_state.data_manager.save_csv('quizzes', quizzes_df)
            
            # Delete related attempts
            quiz_attempts_df = st.session_state.data_manager.load_csv('quiz_attempts')
            quiz_attempts_df = quiz_attempts_df[quiz_attempts_df['quiz_id'] != quiz_id]
            st.session_state.data_manager.save_csv('quiz_attempts', quiz_attempts_df)
            
            return True
        except Exception as e:
            print(f"Quiz deletion error: {e}")
            return False