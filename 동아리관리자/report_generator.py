import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
from io import BytesIO

class ReportGenerator:
    def __init__(self):
        pass
    
    def show_report_interface(self, user):
        st.markdown("### 📄 보고서 생성")
        
        tab1, tab2, tab3 = st.tabs(["📝 새 보고서", "📋 보고서 목록", "📊 통계 보고서"])
        
        with tab1:
            self.show_report_creation_form(user)
        
        with tab2:
            self.show_report_list(user)
        
        with tab3:
            self.show_statistics_report(user)
    
    def show_report_creation_form(self, user):
        st.markdown("#### 새 활동 보고서 작성")
        
        with st.form("create_report"):
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input("보고서 제목", placeholder="예: 2024년 1월 코딩 동아리 활동 보고서")
                report_date = st.date_input("활동 일자", value=date.today())
                
                # Get user's clubs for selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist()
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist()
                
                selected_club = st.selectbox("대상 동아리", club_options)
            
            with col2:
                participants_count = st.number_input("참가자 수", min_value=0, value=1)
                activity_type = st.selectbox("활동 유형", [
                    "정규 활동", "특별 활동", "발표회", "대회", "체험 활동", "기타"
                ])
                activity_location = st.text_input("활동 장소", placeholder="예: 컴퓨터실, 다목적실")
            
            st.markdown("#### 📝 활동 내용")
            
            # Main activity content
            main_activity = st.text_area("주요 활동 내용", height=150, 
                                       placeholder="오늘 진행한 주요 활동을 상세히 기록해주세요.")
            
            # Materials used
            materials = st.text_area("사용한 재료/도구", height=100,
                                   placeholder="활동에 사용한 재료나 도구를 나열해주세요.")
            
            # Achievement and evaluation
            col1, col2 = st.columns(2)
            with col1:
                achievements = st.text_area("성과 및 잘한 점", height=120,
                                          placeholder="학생들이 잘한 점이나 성과를 기록해주세요.")
            
            with col2:
                improvements = st.text_area("개선점 및 피드백", height=120,
                                          placeholder="다음 활동을 위한 개선점을 기록해주세요.")
            
            # Next activity plan
            next_plan = st.text_area("다음 활동 계획", height=100,
                                   placeholder="다음 시간에 진행할 활동 계획을 간단히 적어주세요.")
            
            # Additional notes
            additional_notes = st.text_area("특이사항 및 기타", height=80,
                                          placeholder="기타 특이사항이나 전달사항이 있다면 적어주세요.")
            
            # File upload for images
            uploaded_files = st.file_uploader("활동 사진 첨부", accept_multiple_files=True, 
                                            type=['png', 'jpg', 'jpeg'])
            
            # Submit button
            if st.form_submit_button("📄 보고서 생성", use_container_width=True):
                if report_title and main_activity:
                    report_data = {
                        'title': report_title,
                        'date': report_date.strftime('%Y-%m-%d'),
                        'club': selected_club,
                        'participants_count': participants_count,
                        'activity_type': activity_type,
                        'location': activity_location,
                        'main_activity': main_activity,
                        'materials': materials,
                        'achievements': achievements,
                        'improvements': improvements,
                        'next_plan': next_plan,
                        'additional_notes': additional_notes,
                        'creator': user['username'],
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save report
                    if self.save_report(report_data):
                        st.success("✅ 보고서가 성공적으로 생성되었습니다!")
                        
                        # Generate PDF preview
                        self.generate_report_preview(report_data)
                        
                        st.rerun()
                    else:
                        st.error("❌ 보고서 저장 중 오류가 발생했습니다.")
                else:
                    st.error("제목과 주요 활동 내용은 필수 입력 사항입니다.")
    
    def save_report(self, report_data):
        try:
            reports_df = st.session_state.data_manager.load_csv('reports')
            
            new_id = len(reports_df) + 1
            report_data['id'] = new_id
            
            # Convert dict to string for content storage
            content = {
                'participants_count': report_data['participants_count'],
                'activity_type': report_data['activity_type'],
                'location': report_data['location'],
                'main_activity': report_data['main_activity'],
                'materials': report_data['materials'],
                'achievements': report_data['achievements'],
                'improvements': report_data['improvements'],
                'next_plan': report_data['next_plan'],
                'additional_notes': report_data['additional_notes']
            }
            
            new_report = {
                'id': new_id,
                'title': report_data['title'],
                'content': str(content),
                'creator': report_data['creator'],
                'club': report_data['club'],
                'report_date': report_data['date'],
                'created_date': report_data['created_date']
            }
            
            reports_df = pd.concat([reports_df, pd.DataFrame([new_report])], ignore_index=True)
            return st.session_state.data_manager.save_csv('reports', reports_df)
        
        except Exception as e:
            print(f"Report save error: {e}")
            return False
    
    def show_report_list(self, user):
        st.markdown("#### 📋 기존 보고서 목록")
        
        reports_df = st.session_state.data_manager.load_csv('reports')
        
        if reports_df.empty:
            st.info("아직 작성된 보고서가 없습니다.")
            return
        
        # Filter reports based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            reports_df = reports_df[
                (reports_df['creator'] == user['username']) | 
                (reports_df['club'].isin(user_club_names))
            ]
        
        # Sort by creation date
        reports_df = reports_df.sort_values('created_date', ascending=False)
        
        for _, report in reports_df.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="club-card">
                        <h4>📄 {report['title']}</h4>
                        <p><strong>동아리:</strong> {report['club']}</p>
                        <p><strong>활동일:</strong> {report['report_date']}</p>
                        <p><strong>작성자:</strong> {report['creator']}</p>
                        <p><strong>작성일:</strong> {report['created_date']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📥 다운로드", key=f"download_report_{report['id']}"):
                        self.download_report(report)
                    
                    if st.button("👁️ 미리보기", key=f"preview_report_{report['id']}"):
                        st.session_state[f'show_preview_{report["id"]}'] = True
                
                # Show preview if requested
                if st.session_state.get(f'show_preview_{report["id"]}', False):
                    with st.expander("보고서 미리보기", expanded=True):
                        self.show_report_preview(report)
                        if st.button("닫기", key=f"close_preview_{report['id']}"):
                            st.session_state[f'show_preview_{report["id"]}'] = False
                            st.rerun()
    
    def show_report_preview(self, report):
        st.markdown(f"### 📄 {report['title']}")
        st.markdown(f"**활동일:** {report['report_date']} | **동아리:** {report['club']} | **작성자:** {report['creator']}")
        
        try:
            # Parse content from string
            content = eval(report['content'])
            
            st.markdown("#### 📍 활동 정보")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**참가자 수:** {content.get('participants_count', 'N/A')}")
            with col2:
                st.info(f"**활동 유형:** {content.get('activity_type', 'N/A')}")
            with col3:
                st.info(f"**활동 장소:** {content.get('location', 'N/A')}")
            
            st.markdown("#### 📝 주요 활동 내용")
            st.write(content.get('main_activity', ''))
            
            if content.get('materials'):
                st.markdown("#### 🛠️ 사용 재료/도구")
                st.write(content.get('materials', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                if content.get('achievements'):
                    st.markdown("#### ✅ 성과 및 잘한 점")
                    st.write(content.get('achievements', ''))
            
            with col2:
                if content.get('improvements'):
                    st.markdown("#### 🔄 개선점 및 피드백")
                    st.write(content.get('improvements', ''))
            
            if content.get('next_plan'):
                st.markdown("#### 📅 다음 활동 계획")
                st.write(content.get('next_plan', ''))
            
            if content.get('additional_notes'):
                st.markdown("#### 📌 특이사항 및 기타")
                st.write(content.get('additional_notes', ''))
        
        except Exception as e:
            st.error(f"보고서 내용을 불러오는 중 오류가 발생했습니다: {e}")
    
    def generate_report_preview(self, report_data):
        st.markdown("---")
        st.markdown("### 📄 보고서 미리보기")
        
        # Header
        st.markdown(f"""
        <div style="text-align: center; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2>{report_data['title']}</h2>
            <p>폴라리스반 동아리 활동 보고서</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**활동일:** {report_data['date']}")
        with col2:
            st.info(f"**동아리:** {report_data['club']}")
        with col3:
            st.info(f"**참가자 수:** {report_data['participants_count']}명")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**활동 유형:** {report_data['activity_type']}")
        with col2:
            st.info(f"**활동 장소:** {report_data['location']}")
        with col3:
            st.info(f"**작성자:** {report_data['creator']}")
        
        # Main content
        st.markdown("#### 📝 주요 활동 내용")
        st.write(report_data['main_activity'])
        
        if report_data['materials']:
            st.markdown("#### 🛠️ 사용 재료/도구")
            st.write(report_data['materials'])
        
        col1, col2 = st.columns(2)
        with col1:
            if report_data['achievements']:
                st.markdown("#### ✅ 성과 및 잘한 점")
                st.write(report_data['achievements'])
        
        with col2:
            if report_data['improvements']:
                st.markdown("#### 🔄 개선점 및 피드백")
                st.write(report_data['improvements'])
        
        if report_data['next_plan']:
            st.markdown("#### 📅 다음 활동 계획")
            st.write(report_data['next_plan'])
        
        if report_data['additional_notes']:
            st.markdown("#### 📌 특이사항 및 기타")
            st.write(report_data['additional_notes'])
        
        # Footer
        st.markdown(f"""
        <div style="text-align: center; margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 10px;">
            <p><strong>작성일:</strong> {report_data['created_date']}</p>
            <p><strong>6학년 폴라리스반 동아리 관리 시스템</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    def download_report(self, report):
        try:
            # Generate text version of the report
            content = eval(report['content'])
            
            report_text = f"""
폴라리스반 동아리 활동 보고서

제목: {report['title']}
활동일: {report['report_date']}
동아리: {report['club']}
작성자: {report['creator']}
참가자 수: {content.get('participants_count', 'N/A')}명
활동 유형: {content.get('activity_type', 'N/A')}
활동 장소: {content.get('location', 'N/A')}

=== 주요 활동 내용 ===
{content.get('main_activity', '')}

=== 사용 재료/도구 ===
{content.get('materials', '')}

=== 성과 및 잘한 점 ===
{content.get('achievements', '')}

=== 개선점 및 피드백 ===
{content.get('improvements', '')}

=== 다음 활동 계획 ===
{content.get('next_plan', '')}

=== 특이사항 및 기타 ===
{content.get('additional_notes', '')}

작성일: {report['created_date']}
6학년 폴라리스반 동아리 관리 시스템
            """
            
            # Encode as bytes
            report_bytes = report_text.encode('utf-8-sig')
            
            # Create download button
            st.download_button(
                label="📄 텍스트 파일로 다운로드",
                data=report_bytes,
                file_name=f"{report['title']}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"다운로드 중 오류가 발생했습니다: {e}")
    
    def show_statistics_report(self, user):
        st.markdown("#### 📊 통계 보고서")
        
        # Get data
        reports_df = st.session_state.data_manager.load_csv('reports')
        clubs_df = st.session_state.data_manager.load_csv('clubs')
        user_clubs_df = st.session_state.data_manager.load_csv('user_clubs')
        
        if reports_df.empty:
            st.info("통계를 생성할 보고서가 없습니다.")
            return
        
        # Reports by club
        club_report_counts = reports_df['club'].value_counts()
        st.markdown("##### 동아리별 보고서 수")
        st.bar_chart(club_report_counts)
        
        # Reports by creator
        creator_report_counts = reports_df['creator'].value_counts()
        st.markdown("##### 작성자별 보고서 수")
        st.bar_chart(creator_report_counts)
        
        # Monthly report trend
        if not reports_df.empty:
            reports_df['report_month'] = pd.to_datetime(reports_df['report_date']).dt.to_period('M')
            monthly_counts = reports_df['report_month'].value_counts().sort_index()
            
            st.markdown("##### 월별 보고서 작성 추이")
            st.line_chart(monthly_counts)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 보고서 수", len(reports_df))
        with col2:
            st.metric("총 동아리 수", len(clubs_df))
        with col3:
            unique_creators = reports_df['creator'].nunique()
            st.metric("보고서 작성자 수", unique_creators)
        with col4:
            avg_reports = len(reports_df) / max(unique_creators, 1)
            st.metric("평균 보고서/작성자", f"{avg_reports:.1f}")
