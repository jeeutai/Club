import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

class GallerySystem:
    def __init__(self):
        pass
    
    def show_gallery_interface(self, user):
        st.markdown("### 🖼️ 작품 갤러리")
        
        tab1, tab2 = st.tabs(["🎨 갤러리", "📤 작품 업로드"])
        
        with tab1:
            self.show_gallery_list(user)
        
        with tab2:
            self.show_upload_interface(user)
    
    def show_gallery_list(self, user):
        st.markdown("#### 🎨 작품 갤러리")
        
        galleries_df = st.session_state.data_manager.load_csv('galleries')
        
        if galleries_df.empty:
            st.info("아직 업로드된 작품이 없습니다.")
            return
        
        # Filter by club if not teacher
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            galleries_df = galleries_df[galleries_df['club'].isin(user_club_names)]
        
        # Sort by creation date
        galleries_df = galleries_df.sort_values('created_date', ascending=False)
        
        # Show in grid layout
        cols = st.columns(3)
        
        for i, (_, artwork) in enumerate(galleries_df.iterrows()):
            with cols[i % 3]:
                self.show_artwork_card(artwork, user)
    
    def show_artwork_card(self, artwork, user):
        # Get comments count
        comments_df = st.session_state.data_manager.load_csv('gallery_comments')
        comments_count = len(comments_df[comments_df['gallery_id'] == artwork['id']])
        
        st.markdown(f"""
        <div class="club-card">
            <h4>🎨 {artwork['title']}</h4>
            <p>{artwork['description'][:100]}{'...' if len(artwork['description']) > 100 else ''}</p>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <p><strong>👤 작가:</strong> {artwork['author']}</p>
                <p><strong>🏷️ 동아리:</strong> {artwork['club']}</p>
                <p><strong>📅 작성일:</strong> {artwork['created_date']}</p>
                <p><strong>👍 좋아요:</strong> {artwork['likes']} | <strong>💬 댓글:</strong> {comments_count}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👁️ 상세보기", key=f"view_artwork_{artwork['id']}"):
                st.session_state[f'show_artwork_{artwork["id"]}'] = True
        
        with col2:
            if st.button("👍 좋아요", key=f"like_artwork_{artwork['id']}"):
                self.add_like(artwork['id'])
                st.rerun()
        
        # Show detailed view
        if st.session_state.get(f'show_artwork_{artwork["id"]}', False):
            self.show_artwork_detail(artwork, user)
    
    def show_artwork_detail(self, artwork, user):
        with st.expander("🎨 작품 상세보기", expanded=True):
            st.markdown(f"### {artwork['title']}")
            st.markdown(f"**작가:** {artwork['author']} | **동아리:** {artwork['club']}")
            st.markdown(f"**작성일:** {artwork['created_date']}")
            
            st.markdown("#### 📝 작품 설명")
            st.write(artwork['description'])
            
            # Show comments
            self.show_comments(artwork['id'], user)
            
            if st.button("닫기", key=f"close_artwork_{artwork['id']}"):
                st.session_state[f'show_artwork_{artwork["id"]}'] = False
                st.rerun()
    
    def show_comments(self, gallery_id, user):
        st.markdown("#### 💬 댓글")
        
        comments_df = st.session_state.data_manager.load_csv('gallery_comments')
        artwork_comments = comments_df[comments_df['gallery_id'] == gallery_id].sort_values('created_date')
        
        # Add new comment
        with st.form(f"add_comment_{gallery_id}"):
            comment_text = st.text_area("댓글 작성", height=80)
            if st.form_submit_button("💬 댓글 등록"):
                if comment_text.strip():
                    self.add_comment(gallery_id, user['username'], comment_text.strip())
                    st.success("댓글이 등록되었습니다!")
                    st.rerun()
        
        # Show existing comments
        if not artwork_comments.empty:
            for _, comment in artwork_comments.iterrows():
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #4ECDC4;">
                    <strong>{comment['username']}</strong> - {comment['created_date']}<br>
                    {comment['comment']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("아직 댓글이 없습니다. 첫 댓글을 작성해보세요!")
    
    def show_upload_interface(self, user):
        st.markdown("#### 📤 작품 업로드")
        
        with st.form("upload_artwork"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("작품 제목", placeholder="작품의 제목을 입력하세요")
                
                # Club selection
                if user['role'] == '선생님':
                    clubs_df = st.session_state.data_manager.load_csv('clubs')
                    club_options = ["전체"] + clubs_df['name'].tolist()
                else:
                    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                    club_options = user_clubs['club_name'].tolist()
                
                selected_club = st.selectbox("동아리", club_options)
            
            with col2:
                uploaded_file = st.file_uploader(
                    "작품 이미지",
                    type=['png', 'jpg', 'jpeg', 'gif'],
                    help="PNG, JPG, JPEG, GIF 파일을 업로드하세요"
                )
            
            description = st.text_area(
                "작품 설명",
                height=120,
                placeholder="작품에 대한 설명, 제작 과정, 사용한 재료 등을 자유롭게 작성해주세요..."
            )
            
            if st.form_submit_button("🎨 작품 업로드", use_container_width=True):
                if title and description and selected_club:
                    success = self.upload_artwork(
                        title, description, uploaded_file, user['username'], selected_club
                    )
                    
                    if success:
                        st.success("작품이 성공적으로 업로드되었습니다!")
                        st.rerun()
                    else:
                        st.error("작품 업로드 중 오류가 발생했습니다.")
                else:
                    st.error("제목, 설명, 동아리를 모두 입력해주세요.")
    
    def upload_artwork(self, title, description, uploaded_file, author, club):
        try:
            galleries_df = st.session_state.data_manager.load_csv('galleries')
            
            new_id = len(galleries_df) + 1
            image_path = ""
            
            if uploaded_file is not None:
                # In a real implementation, you would save the file
                image_path = f"uploads/gallery/{uploaded_file.name}"
            
            new_artwork = {
                'id': new_id,
                'title': title,
                'description': description,
                'image_path': image_path,
                'author': author,
                'club': club,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'likes': 0
            }
            
            galleries_df = pd.concat([galleries_df, pd.DataFrame([new_artwork])], ignore_index=True)
            return st.session_state.data_manager.save_csv('galleries', galleries_df)
        
        except Exception as e:
            print(f"Artwork upload error: {e}")
            return False
    
    def add_like(self, gallery_id):
        try:
            galleries_df = st.session_state.data_manager.load_csv('galleries')
            galleries_df.loc[galleries_df['id'] == gallery_id, 'likes'] += 1
            st.session_state.data_manager.save_csv('galleries', galleries_df)
        except Exception as e:
            print(f"Like add error: {e}")
    
    def add_comment(self, gallery_id, username, comment):
        try:
            comments_df = st.session_state.data_manager.load_csv('gallery_comments')
            
            new_id = len(comments_df) + 1
            new_comment = {
                'id': new_id,
                'gallery_id': gallery_id,
                'username': username,
                'comment': comment,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            comments_df = pd.concat([comments_df, pd.DataFrame([new_comment])], ignore_index=True)
            return st.session_state.data_manager.save_csv('gallery_comments', comments_df)
        
        except Exception as e:
            print(f"Comment add error: {e}")
            return False