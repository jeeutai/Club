import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json

class VoteSystem:
    def __init__(self):
        pass
    
    def show_vote_interface(self, user):
        st.markdown("### 🗳️ 투표 시스템")
        
        if user['role'] in ['선생님', '회장', '부회장']:
            tab1, tab2, tab3 = st.tabs(["🗳️ 투표 참여", "➕ 투표 생성", "📊 투표 관리"])
            
            with tab1:
                self.show_vote_list(user)
            
            with tab2:
                self.show_vote_creation(user)
            
            with tab3:
                self.show_vote_management(user)
        else:
            tab1, tab2 = st.tabs(["🗳️ 투표 참여", "📋 내 투표 기록"])
            
            with tab1:
                self.show_vote_list(user)
            
            with tab2:
                self.show_my_vote_records(user)
    
    def show_vote_list(self, user):
        st.markdown("#### 🗳️ 참여 가능한 투표")
        
        votes_df = st.session_state.data_manager.load_csv('votes')
        
        if votes_df.empty:
            st.info("진행 중인 투표가 없습니다.")
            return
        
        # Filter votes based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            votes_df = votes_df[votes_df['club'].isin(user_club_names)]
        
        # Show only active votes
        current_date = datetime.now().date()
        active_votes = []
        
        for _, vote in votes_df.iterrows():
            end_date = datetime.strptime(vote['end_date'], '%Y-%m-%d').date()
            if end_date >= current_date:
                active_votes.append(vote)
        
        if not active_votes:
            st.info("현재 진행 중인 투표가 없습니다.")
            return
        
        for vote in active_votes:
            self.show_vote_card(vote, user)
    
    def show_vote_card(self, vote, user):
        # Check if user has voted
        vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
        user_vote = vote_responses_df[
            (vote_responses_df['vote_id'] == vote['id']) &
            (vote_responses_df['username'] == user['username'])
        ]
        
        has_voted = not user_vote.empty
        
        # Calculate days left
        end_date = datetime.strptime(vote['end_date'], '%Y-%m-%d').date()
        days_left = (end_date - date.today()).days
        
        status_color = "#28a745" if not has_voted else "#6c757d"
        status_text = "투표 가능" if not has_voted else "투표 완료"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="club-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <h4>🗳️ {vote['title']}</h4>
                        <span style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                            {status_text}
                        </span>
                    </div>
                    <p>{vote.get('description', '설명이 없습니다.')}</p>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p><strong>🏷️ 동아리:</strong> {vote['club']}</p>
                        <p><strong>📅 마감일:</strong> {vote['end_date']} ({days_left}일 남음)</p>
                        <p><strong>👤 생성자:</strong> {vote['creator']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not has_voted and days_left >= 0:
                    if st.button("🗳️ 투표", key=f"vote_{vote['id']}"):
                        st.session_state[f'voting_{vote["id"]}'] = True
                elif has_voted:
                    if st.button("📊 결과", key=f"result_{vote['id']}"):
                        st.session_state[f'show_result_{vote["id"]}'] = True
                else:
                    st.error("⏰ 마감됨")
            
            # Show voting interface
            if st.session_state.get(f'voting_{vote["id"]}', False):
                self.show_voting_interface(vote, user)
            
            # Show results
            if st.session_state.get(f'show_result_{vote["id"]}', False):
                self.show_vote_results(vote)
    
    def show_voting_interface(self, vote, user):
        with st.expander("🗳️ 투표하기", expanded=True):
            try:
                options = json.loads(vote['options'])
                
                st.markdown(f"### {vote['title']}")
                st.markdown(vote.get('description', ''))
                st.markdown("---")
                
                with st.form(f"vote_form_{vote['id']}"):
                    selected_option = st.radio(
                        "선택하세요:",
                        options,
                        key=f"vote_option_{vote['id']}"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("🗳️ 투표하기", use_container_width=True):
                            if selected_option:
                                success = self.save_vote_response(vote['id'], user['username'], selected_option)
                                if success:
                                    st.success("투표가 완료되었습니다!")
                                    st.session_state[f'voting_{vote["id"]}'] = False
                                    st.rerun()
                                else:
                                    st.error("투표 저장 중 오류가 발생했습니다.")
                    
                    with col2:
                        if st.form_submit_button("❌ 취소", use_container_width=True):
                            st.session_state[f'voting_{vote["id"]}'] = False
                            st.rerun()
            
            except Exception as e:
                st.error(f"투표 로딩 중 오류가 발생했습니다: {e}")
    
    def save_vote_response(self, vote_id, username, selected_option):
        try:
            vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
            
            new_id = len(vote_responses_df) + 1
            new_response = {
                'id': new_id,
                'vote_id': vote_id,
                'username': username,
                'selected_option': selected_option,
                'voted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            vote_responses_df = pd.concat([vote_responses_df, pd.DataFrame([new_response])], ignore_index=True)
            return st.session_state.data_manager.save_csv('vote_responses', vote_responses_df)
        
        except Exception as e:
            print(f"Vote response save error: {e}")
            return False
    
    def show_vote_creation(self, user):
        st.markdown("#### ➕ 새 투표 생성")
        
        with st.form("create_vote"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("투표 제목", placeholder="예: 다음 활동 선택")
                description = st.text_area("설명", placeholder="투표에 대한 설명을 입력하세요")
                
                # Club selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist()
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist()
                
                selected_club = st.selectbox("대상 동아리", club_options)
            
            with col2:
                end_date = st.date_input(
                    "마감일",
                    min_value=date.today(),
                    value=date.today() + timedelta(days=7)
                )
                
                num_options = st.number_input("선택지 수", min_value=2, max_value=10, value=3)
            
            st.markdown("#### 📝 선택지 작성")
            
            options = []
            for i in range(num_options):
                option = st.text_input(f"선택지 {i+1}", key=f"option_{i}")
                if option:
                    options.append(option)
            
            if st.form_submit_button("🗳️ 투표 생성", use_container_width=True):
                if title and len(options) >= 2:
                    success = self.create_vote(
                        title, description, selected_club, options, 
                        end_date.strftime('%Y-%m-%d'), user['username']
                    )
                    
                    if success:
                        st.success("투표가 성공적으로 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("투표 생성 중 오류가 발생했습니다.")
                else:
                    st.error("제목과 최소 2개의 선택지를 입력해주세요.")
    
    def create_vote(self, title, description, club, options, end_date, creator):
        try:
            votes_df = st.session_state.data_manager.load_csv('votes')
            
            new_id = len(votes_df) + 1
            new_vote = {
                'id': new_id,
                'title': title,
                'description': description,
                'options': json.dumps(options),
                'creator': creator,
                'club': club,
                'end_date': end_date,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            votes_df = pd.concat([votes_df, pd.DataFrame([new_vote])], ignore_index=True)
            return st.session_state.data_manager.save_csv('votes', votes_df)
        
        except Exception as e:
            print(f"Vote creation error: {e}")
            return False
    
    def show_vote_management(self, user):
        st.markdown("#### 📊 투표 관리")
        
        votes_df = st.session_state.data_manager.load_csv('votes')
        vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
        
        if votes_df.empty:
            st.info("생성된 투표가 없습니다.")
            return
        
        # Filter votes by user's authority
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            votes_df = votes_df[
                (votes_df['club'].isin(user_club_names)) |
                (votes_df['creator'] == user['username'])
            ]
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_votes = len(votes_df)
        total_responses = len(vote_responses_df)
        unique_voters = vote_responses_df['username'].nunique() if not vote_responses_df.empty else 0
        
        with col1:
            st.metric("총 투표", total_votes)
        with col2:
            st.metric("총 응답", total_responses)
        with col3:
            st.metric("참여자", unique_voters)
        with col4:
            avg_participation = total_responses / max(total_votes, 1)
            st.metric("평균 참여", f"{avg_participation:.1f}")
        
        # Vote list with management options
        st.markdown("##### 투표 목록")
        
        for _, vote in votes_df.iterrows():
            vote_responses = vote_responses_df[vote_responses_df['vote_id'] == vote['id']]
            response_count = len(vote_responses)
            
            # Check if vote is active
            end_date = datetime.strptime(vote['end_date'], '%Y-%m-%d').date()
            is_active = end_date >= date.today()
            status = "진행중" if is_active else "마감됨"
            status_color = "#28a745" if is_active else "#6c757d"
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="club-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <h4>🗳️ {vote['title']}</h4>
                            <span style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                                {status}
                            </span>
                        </div>
                        <p>{vote.get('description', '설명이 없습니다.')}</p>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span><strong>동아리:</strong> {vote['club']}</span>
                            <span><strong>마감일:</strong> {vote['end_date']}</span>
                            <span><strong>응답:</strong> {response_count}개</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📊 결과", key=f"manage_result_{vote['id']}"):
                        st.session_state[f'show_manage_result_{vote["id"]}'] = True
                    
                    if user['role'] == '선생님' or vote['creator'] == user['username']:
                        if st.button("🗑️ 삭제", key=f"delete_vote_{vote['id']}"):
                            self.delete_vote(vote['id'])
                            st.success("투표가 삭제되었습니다!")
                            st.rerun()
                
                # Show detailed results
                if st.session_state.get(f'show_manage_result_{vote["id"]}', False):
                    with st.expander("투표 결과 상세", expanded=True):
                        self.show_detailed_vote_results(vote, vote_responses)
                        if st.button("닫기", key=f"close_manage_result_{vote['id']}"):
                            st.session_state[f'show_manage_result_{vote["id"]}'] = False
                            st.rerun()
    
    def show_vote_results(self, vote):
        with st.expander("📊 투표 결과", expanded=True):
            vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
            vote_responses = vote_responses_df[vote_responses_df['vote_id'] == vote['id']]
            
            if vote_responses.empty:
                st.info("아직 투표 결과가 없습니다.")
            else:
                try:
                    options = json.loads(vote['options'])
                    result_counts = vote_responses['selected_option'].value_counts()
                    
                    st.markdown(f"### {vote['title']} 결과")
                    st.markdown(f"**총 투표 수:** {len(vote_responses)}명")
                    
                    # Show results as chart
                    st.bar_chart(result_counts)
                    
                    # Show percentage breakdown
                    total_votes = len(vote_responses)
                    for option in options:
                        count = result_counts.get(option, 0)
                        percentage = (count / total_votes * 100) if total_votes > 0 else 0
                        st.markdown(f"**{option}:** {count}표 ({percentage:.1f}%)")
                
                except Exception as e:
                    st.error(f"결과 표시 중 오류가 발생했습니다: {e}")
            
            if st.button("닫기", key=f"close_result_{vote['id']}"):
                st.session_state[f'show_result_{vote["id"]}'] = False
                st.rerun()
    
    def show_detailed_vote_results(self, vote, responses):
        st.markdown(f"### {vote['title']} - 상세 결과")
        
        if responses.empty:
            st.info("아직 투표 결과가 없습니다.")
            return
        
        try:
            options = json.loads(vote['options'])
            result_counts = responses['selected_option'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 투표 결과")
                total_votes = len(responses)
                
                for option in options:
                    count = result_counts.get(option, 0)
                    percentage = (count / total_votes * 100) if total_votes > 0 else 0
                    st.markdown(f"**{option}:** {count}표 ({percentage:.1f}%)")
                
                # Chart
                st.bar_chart(result_counts)
            
            with col2:
                st.markdown("#### 📋 투표자 목록")
                for _, response in responses.sort_values('voted_date').iterrows():
                    st.markdown(f"- **{response['username']}**: {response['selected_option']} ({response['voted_date']})")
        
        except Exception as e:
            st.error(f"상세 결과 표시 중 오류가 발생했습니다: {e}")
    
    def show_my_vote_records(self, user):
        st.markdown("#### 📋 내 투표 기록")
        
        vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
        votes_df = st.session_state.data_manager.load_csv('votes')
        
        my_responses = vote_responses_df[vote_responses_df['username'] == user['username']]
        
        if my_responses.empty:
            st.info("참여한 투표가 없습니다.")
            return
        
        # Overall statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("참여 투표", len(my_responses))
        with col2:
            latest_vote = my_responses['voted_date'].max()
            st.metric("마지막 투표", latest_vote.split()[0] if latest_vote else "없음")
        with col3:
            this_month_votes = len(my_responses[my_responses['voted_date'].str.startswith(datetime.now().strftime('%Y-%m'))])
            st.metric("이번 달", f"{this_month_votes}회")
        
        # Vote history
        st.markdown("##### 투표 기록")
        
        for _, response in my_responses.sort_values('voted_date', ascending=False).iterrows():
            vote_info = votes_df[votes_df['id'] == response['vote_id']]
            
            if not vote_info.empty:
                vote = vote_info.iloc[0]
                
                st.markdown(f"""
                <div class="club-card">
                    <h4>🗳️ {vote['title']}</h4>
                    <p><strong>내 선택:</strong> {response['selected_option']}</p>
                    <p><strong>투표일:</strong> {response['voted_date']} | <strong>동아리:</strong> {vote['club']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def delete_vote(self, vote_id):
        try:
            # Delete vote
            votes_df = st.session_state.data_manager.load_csv('votes')
            votes_df = votes_df[votes_df['id'] != vote_id]
            st.session_state.data_manager.save_csv('votes', votes_df)
            
            # Delete related responses
            vote_responses_df = st.session_state.data_manager.load_csv('vote_responses')
            vote_responses_df = vote_responses_df[vote_responses_df['vote_id'] != vote_id]
            st.session_state.data_manager.save_csv('vote_responses', vote_responses_df)
            
            return True
        except Exception as e:
            print(f"Vote deletion error: {e}")
            return False