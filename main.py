import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from utils import GithubSync, decrypt_token
import sys

# --- Stlite Patch ---
try:
    import pyodide_http
    pyodide_http.patch_all()
except ImportError:
    pass

# --- GÜVENLİ AYARLAR ---
# 1. 'encrypt_token_helper.py' scriptini çalıştırın.
# 2. Ürettiği şifreli metni aşağıya yapıştırın.
ENCRYPTED_GITHUB_TOKEN = "gAAAAABpP9qV1wz1WJafeG727Nt7n9tJtcWLws5e1xcs80fYnGVgta200c-mVrOXDUNqkf0uRvRMZoSrvXS1ueXZgivBrnQvv6F2iekR9n7_mPt12X3mkEK_znMatw5SQZMKKVygsv1ICRXjEf7Oul5znh8f995YIyPoU6g_KeKmuQzbogOm-iF-qgvi7hUDdW9BVmDY3mle" 
REPO_NAME = "edunya/derscalismaData" # Örn: kullaniciadi/repo-adi

# --- Sayfa ---
st.set_page_config(page_title="Study Space", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #fdfbf7 0%, #e8f5e9 100%); color: #2c3e50; }
    .css-card {
        background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .stButton>button {
        background: linear-gradient(90deg, #556B2F 0%, #7da453 100%);
        color: white; border: none; padding: 10px 24px; border-radius: 12px;
    }
    .stTextInput>div>div>input { background-color: rgba(255, 255, 255, 0.8); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- State ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'decrypted_token' not in st.session_state: st.session_state.decrypted_token = None
if 'study_data' not in st.session_state: st.session_state.study_data = []
if 'data_sha' not in st.session_state: st.session_state.data_sha = None

# --- Helpers ---
def init_github():
    token = st.session_state.decrypted_token
    # Repo ismi kodda yoksa sessiondan (manuel girişten) al
    repo = REPO_NAME if REPO_NAME else st.session_state.get('gh_repo', "")
    if token and repo:
        return GithubSync(token, repo)
    return None

def load_data():
    gh = init_github()
    if gh:
        with st.spinner('Bağlanılıyor...'):
            data, sha = gh.fetch_data()
            if data is not None:
                st.session_state.study_data = data
                st.session_state.data_sha = sha
                return True
    return False

def save_data():
    gh = init_github()
    if gh:
        success = gh.push_data(st.session_state.study_data, st.session_state.data_sha)
        if success:
            load_data() # Update SHA
            st.toast("✅ Kaydedildi")
        else:
            st.toast("❌ Hata")

# --- Pages ---
def login_page():
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.title("🌿 Study Space")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        username = st.text_input("Kullanıcı Adı", placeholder="Adınız")
        password = st.text_input("Grup Şifresi", type="password", placeholder="Tokenı şifrelerken kullandığın parola")
        
        # Manuel ayarlar (eğer kod boşsa)
        if not ENCRYPTED_GITHUB_TOKEN:
            with st.expander("Manuel Ayar (Kod Boşsa)"):
                st.text_input("Repo (user/repo)", key="gh_repo", value=REPO_NAME)
                # Buraya direkt token girilmesine izin vermiyoruz artık, güvenlik için helper kullanılmalı
                # veya kullanıcı kendi riskine manuel girebilir ama UI'ı sade tutuyoruz.

        if st.button("Giriş Yap", use_container_width=True):
            if not username or not password:
                st.warning("Ad ve Şifre gerekli.")
                return

            # 1. Token Çözme Denemesi
            token_to_use = None
            
            if ENCRYPTED_GITHUB_TOKEN:
                decrypted = decrypt_token(ENCRYPTED_GITHUB_TOKEN, password)
                if decrypted:
                    token_to_use = decrypted
                else:
                    st.error("Hatalı Şifre! Token çözülemedi.")
                    return
            else:
                # Kodda token yoksa, şifreyi direkt token gibi kullanmayı denesin (legacy mode)
                # veya kullanıcıya uyarı verelim.
                 st.error("Kod içinde ENCRYPTED_GITHUB_TOKEN tanımlı değil. Lütfen kurulumu yapın.")
                 return

            # 2. Başarılı ise login
            st.session_state.username = username
            st.session_state.decrypted_token = token_to_use
            
            if load_data():
                st.session_state.logged_in = True
                st.success("Giriş Başarılı!")
                st.rerun()
            else:
                st.error("GitHub'a bağlanılamadı. Token doğru çözüldü ama repo erişimi yok veya repo ismi yanlış.")
                
        st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    c1, c2 = st.columns([8, 1])
    c1.title(f"👋 {st.session_state.username}")
    if c2.button("Çıkış"):
        st.session_state.logged_in = False
        st.session_state.decrypted_token = None
        st.rerun()

    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        # Pomodoro
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("⏱️ Pomodoro")
        if 'time_left' not in st.session_state: st.session_state.time_left = 25*60
        if 'timer_active' not in st.session_state: st.session_state.timer_active = False
        sure = st.slider("Dakika", 5, 90, 25, 5)
        if st.button("Başlat"): 
            st.session_state.timer_active = True
            st.session_state.time_left = sure*60
        if st.button("Dur"): st.session_state.timer_active = False
        
        if st.session_state.timer_active:
             m, s = divmod(st.session_state.time_left, 60)
             st.markdown(f"<h2 style='text-align:center;color:#556B2F'>{m:02d}:{s:02d}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ekle
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Ekle")
        ders = st.text_input("Ders")
        dk = st.number_input("Süre", value=sure)
        if st.button("Kaydet"):
            st.session_state.study_data.append({
                "user": st.session_state.username,
                "ders": ders,
                "sure": dk,
                "tarih": str(datetime.now().date()),
                "timestamp": str(datetime.now())
            })
            save_data()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        # Grafik
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        my_data = [d for d in st.session_state.study_data if d['user'] == st.session_state.username]
        if my_data:
            df = pd.DataFrame(my_data)
            daily = df.groupby('tarih')['sure'].sum().reset_index()
            fig = px.bar(daily, x='tarih', y='sure', color='sure', title="Çalışmalarım", color_continuous_scale=['#dcedc8', '#33691e'])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Veri yok.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tablo
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        all_df = pd.DataFrame(st.session_state.study_data)
        if not all_df.empty:
            rank = all_df.groupby('user')['sure'].sum().reset_index().sort_values('sure', ascending=False)
            st.subheader("Skor Tablosu")
            st.dataframe(rank, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    main_app()
else:
    login_page()

