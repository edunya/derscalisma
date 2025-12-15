import json
import base64
import requests
import datetime
import streamlit as st
from cryptography.fernet import Fernet
import hashlib

# --- Şifreleme Helperları ---
def get_key_from_password(password):
    """Paroladan 32-byte Fernet anahtarı üretir."""
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def decrypt_token(encrypted_token, password):
    """Şifreli tokenı parolayı kullanarak çözer."""
    try:
        key = get_key_from_password(password)
        f = Fernet(key)
        return f.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        return None

# --- GitHub Sync Sınıfı ---
class GithubSync:
    def __init__(self, token, repo_name, file_path="data.json"):
        self.token = token
        self.repo_name = repo_name
        self.file_path = file_path
        self.base_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_data(self):
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                content = response.json()
                decoded_content = base64.b64decode(content['content']).decode('utf-8')
                return json.loads(decoded_content), content['sha']
            elif response.status_code == 404:
                return [], None
            else:
                st.error(f"Veri çekme hatası: {response.status_code}")
                return [], None
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
            return [], None

    def push_data(self, data, sha=None):
        try:
            json_data = json.dumps(data, indent=4, ensure_ascii=False)
            message = f"Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            payload = {
                "message": message,
                "content": base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(self.base_url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            st.error(f"Yükleme hatası: {e}")
            return False
