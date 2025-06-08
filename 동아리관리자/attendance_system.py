import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

class AttendanceSystem:
    def __init__(self):
        pass
    
    def show_attendance_interface(self, user):
        st.markdown("### 📅 출석 관리")
        
        if user['role'] in ['선생님', '회장', '부회장', '총무']:
            tab1, tab2, tab3 = st.tabs(["📋 출석 체크", "📊 출석 현황", "📈 출석 통계"])
            
            with tab1:
                self.show_attendance_check(user)
            
            with tab2:
                self.show_attendance_status(user)
            
            with tab3:
                self.show_attendance_statistics(user)
        else:
            tab1, tab2 = st.tabs(["📋 내 출석", "📊 출석 현황"])
            
            with tab1:
                self.show_my_attendance(user)
            
            with tab2:
                self.show_attendance_status(user)
    
    def show_attendance_check(self, user):
        st.markdown("#### 📋 출석 체크")
        
        # Get user's clubs for attendance management
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            club_options = clubs_df['name'].tolist()
        else:
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            club_options = user_clubs['club_name'].tolist()
        
        if not club_options:
            st.info("관리할 동아리가 없습니다.")
            return
        
        selected_club = st.selectbox("동아리 선택", club_options)
        selected_date = st.date_input("출석 날짜", value=date.today())
        
        if selected_club:
            # Get club members
            user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
            club_members = user_clubs_df[user_clubs_df['club_name'] == selected_club]
            
            if club_members.empty:
                st.info(f"{selected_club} 동아리에 회원이 없습니다.")
                return
            
            # Get accounts for member details
            accounts_df = st.session_state.data_manager.load_csv('accounts')
            member_details = club_members.merge(accounts_df, on='username')
            
            # Check existing attendance
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            existing_attendance = attendance_df[
                (attendance_df['club'] == selected_club) & 
                (attendance_df['date'] == selected_date.strftime('%Y-%m-%d'))
            ]
            
            st.markdown(f"##### {selected_club} - {selected_date} 출석 체크")
            
            with st.form("attendance_form"):
                attendance_data = {}
                
                for _, member in member_details.iterrows():
                    existing_record = existing_attendance[existing_attendance['username'] == member['username']]
                    current_status = existing_record['status'].iloc[0] if not existing_record.empty else '출석'
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**{member['name']}** ({member['username']})")
                    with col2:
                        attendance_data[member['username']] = st.selectbox(
                            f"상태",
                            ['출석', '지각', '결석', '병결'],
                            index=['출석', '지각', '결석', '병결'].index(current_status),
                            key=f"attendance_{member['username']}"
                        )
                
                if st.form_submit_button("📝 출석 저장", use_container_width=True):
                    success_count = 0
                    for username, status in attendance_data.items():
                        if self.save_attendance(username, selected_club, selected_date, status, user['username']):
                            success_count += 1
                    
                    st.success(f"{success_count}명의 출석이 저장되었습니다!")
                    st.rerun()
    
    def save_attendance(self, username, club, date, status, recorder):
        try:
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            
            # Check if record exists
            existing_record = attendance_df[
                (attendance_df['username'] == username) & 
                (attendance_df['club'] == club) & 
                (attendance_df['date'] == date.strftime('%Y-%m-%d'))
            ]
            
            if not existing_record.empty:
                # Update existing record
                attendance_df.loc[
                    (attendance_df['username'] == username) & 
                    (attendance_df['club'] == club) & 
                    (attendance_df['date'] == date.strftime('%Y-%m-%d')),
                    'status'
                ] = status
                attendance_df.loc[
                    (attendance_df['username'] == username) & 
                    (attendance_df['club'] == club) & 
                    (attendance_df['date'] == date.strftime('%Y-%m-%d')),
                    'recorder'
                ] = recorder
            else:
                # Create new record
                new_id = len(attendance_df) + 1
                new_record = {
                    'id': new_id,
                    'username': username,
                    'club': club,
                    'date': date.strftime('%Y-%m-%d'),
                    'status': status,
                    'recorder': recorder
                }
                
                attendance_df = pd.concat([attendance_df, pd.DataFrame([new_record])], ignore_index=True)
            
            return st.session_state.data_manager.save_csv('attendance', attendance_df)
        
        except Exception as e:
            print(f"Attendance save error: {e}")
            return False
    
    def show_attendance_status(self, user):
        st.markdown("#### 📊 출석 현황")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작 날짜", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("종료 날짜", value=date.today())
        
        # Club selection
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            club_options = ["전체"] + clubs_df['name'].tolist()
        else:
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            club_options = ["전체"] + user_clubs['club_name'].tolist()
        
        selected_club = st.selectbox("동아리", club_options)
        
        # Get attendance data
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        
        if attendance_df.empty:
            st.info("출석 데이터가 없습니다.")
            return
        
        # Filter by date range
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
        filtered_attendance = attendance_df[
            (attendance_df['date'] >= pd.to_datetime(start_date)) &
            (attendance_df['date'] <= pd.to_datetime(end_date))
        ]
        
        # Filter by club
        if selected_club != "전체":
            filtered_attendance = filtered_attendance[filtered_attendance['club'] == selected_club]
        
        if filtered_attendance.empty:
            st.info("선택한 조건에 해당하는 출석 데이터가 없습니다.")
            return
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_records = len(filtered_attendance)
        present_count = len(filtered_attendance[filtered_attendance['status'] == '출석'])
        late_count = len(filtered_attendance[filtered_attendance['status'] == '지각'])
        absent_count = len(filtered_attendance[filtered_attendance['status'] == '결석'])
        
        with col1:
            st.metric("총 기록", total_records)
        with col2:
            present_rate = (present_count / total_records * 100) if total_records > 0 else 0
            st.metric("출석률", f"{present_rate:.1f}%")
        with col3:
            st.metric("지각", late_count)
        with col4:
            st.metric("결석", absent_count)
        
        # Detailed attendance table
        st.markdown("##### 상세 출석 기록")
        
        # Get user names
        accounts_df = st.session_state.data_manager.load_csv('accounts')
        attendance_with_names = filtered_attendance.merge(
            accounts_df[['username', 'name']], on='username', how='left'
        )
        
        # Display table
        display_df = attendance_with_names[['name', 'club', 'date', 'status', 'recorder']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df.columns = ['이름', '동아리', '날짜', '상태', '기록자']
        
        st.dataframe(display_df, use_container_width=True)
    
    def show_attendance_statistics(self, user):
        st.markdown("#### 📈 출석 통계")
        
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        
        if attendance_df.empty:
            st.info("출석 통계를 생성할 데이터가 없습니다.")
            return
        
        # Filter by user's authority
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            attendance_df = attendance_df[attendance_df['club'].isin(user_club_names)]
        
        # Monthly attendance trend
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
        attendance_df['month'] = attendance_df['date'].dt.to_period('M')
        
        monthly_stats = attendance_df.groupby(['month', 'status']).size().unstack(fill_value=0)
        
        if not monthly_stats.empty:
            st.markdown("##### 월별 출석 현황")
            st.bar_chart(monthly_stats)
        
        # Club-wise attendance rate
        club_stats = attendance_df.groupby(['club', 'status']).size().unstack(fill_value=0)
        
        if not club_stats.empty:
            # Calculate attendance rates
            club_stats['총계'] = club_stats.sum(axis=1)
            club_stats['출석률'] = (club_stats.get('출석', 0) / club_stats['총계'] * 100).round(1)
            
            st.markdown("##### 동아리별 출석률")
            
            for club in club_stats.index:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{club}**")
                with col2:
                    st.metric("출석률", f"{club_stats.loc[club, '출석률']}%")
                with col3:
                    st.metric("총 기록", club_stats.loc[club, '총계'])
        
        # Individual attendance summary
        user_stats = attendance_df.groupby(['username', 'status']).size().unstack(fill_value=0)
        
        if not user_stats.empty:
            accounts_df = st.session_state.data_manager.load_csv('accounts')
            user_stats_with_names = user_stats.reset_index().merge(
                accounts_df[['username', 'name']], on='username'
            )
            
            user_stats_with_names['총계'] = user_stats_with_names[['출석', '지각', '결석', '병결']].sum(axis=1)
            user_stats_with_names['출석률'] = (
                user_stats_with_names.get('출석', 0) / user_stats_with_names['총계'] * 100
            ).round(1)
            
            # Sort by attendance rate
            user_stats_with_names = user_stats_with_names.sort_values('출석률', ascending=False)
            
            st.markdown("##### 개인별 출석률 랭킹")
            
            for _, user_stat in user_stats_with_names.head(10).iterrows():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**{user_stat['name']}**")
                with col2:
                    st.metric("출석률", f"{user_stat['출석률']}%")
                with col3:
                    st.metric("출석", user_stat.get('출석', 0))
                with col4:
                    st.metric("총계", user_stat['총계'])
    
    def show_my_attendance(self, user):
        st.markdown("#### 📋 내 출석 기록")
        
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        my_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        if my_attendance.empty:
            st.info("출석 기록이 없습니다.")
            return
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_days = len(my_attendance)
        present_days = len(my_attendance[my_attendance['status'] == '출석'])
        late_days = len(my_attendance[my_attendance['status'] == '지각'])
        absent_days = len(my_attendance[my_attendance['status'] == '결석'])
        
        present_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        with col1:
            st.metric("총 출석일", total_days)
        with col2:
            st.metric("출석률", f"{present_rate:.1f}%")
        with col3:
            st.metric("지각", late_days)
        with col4:
            st.metric("결석", absent_days)
        
        # Monthly calendar view
        st.markdown("##### 📅 출석 캘린더")
        
        current_month = st.selectbox(
            "월 선택",
            options=list(range(1, 13)),
            index=datetime.now().month - 1,
            format_func=lambda x: f"{x}월"
        )
        
        current_year = datetime.now().year
        
        # Filter attendance for selected month
        my_attendance['date'] = pd.to_datetime(my_attendance['date'])
        month_attendance = my_attendance[
            (my_attendance['date'].dt.year == current_year) &
            (my_attendance['date'].dt.month == current_month)
        ]
        
        # Create calendar display
        cal = calendar.monthcalendar(current_year, current_month)
        
        st.markdown(f"#### {current_year}년 {current_month}월")
        
        # Calendar header
        st.markdown("| 월 | 화 | 수 | 목 | 금 | 토 | 일 |")
        st.markdown("|---|---|---|---|---|---|---|")
        
        for week in cal:
            week_display = []
            for day in week:
                if day == 0:
                    week_display.append(" ")
                else:
                    day_date = date(current_year, current_month, day)
                    day_attendance = month_attendance[
                        month_attendance['date'].dt.date == day_date
                    ]
                    
                    if not day_attendance.empty:
                        status = day_attendance['status'].iloc[0]
                        if status == '출석':
                            week_display.append(f"✅ {day}")
                        elif status == '지각':
                            week_display.append(f"🟡 {day}")
                        elif status == '결석':
                            week_display.append(f"❌ {day}")
                        elif status == '병결':
                            week_display.append(f"🏥 {day}")
                        else:
                            week_display.append(str(day))
                    else:
                        week_display.append(str(day))
            
            st.markdown("| " + " | ".join(week_display) + " |")
        
        # Legend
        st.markdown("""
        **범례:**
        - ✅ 출석
        - 🟡 지각  
        - ❌ 결석
        - 🏥 병결
        """)
        
        # Recent attendance records
        st.markdown("##### 📋 최근 출석 기록")
        
        recent_attendance = my_attendance.sort_values('date', ascending=False).head(10)
        
        for _, record in recent_attendance.iterrows():
            status_emoji = {
                '출석': '✅',
                '지각': '🟡',
                '결석': '❌',
                '병결': '🏥'
            }.get(record['status'], '❓')
            
            st.markdown(f"""
            <div class="club-card">
                <p><strong>{record['date'].strftime('%Y-%m-%d')}</strong> - {record['club']}</p>
                <p>{status_emoji} {record['status']}</p>
            </div>
            """, unsafe_allow_html=True)