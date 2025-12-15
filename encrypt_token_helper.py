from cryptography.fernet import Fernet
import base64
import hashlib
import getpass

def generate_key(password):
    # Basit bir parola bazl anahtar türetme (KDF)
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_token():
    print("=== GitHub Token Şifreleyici ===")
    print("Bu araç, token'ınızı main.py dosyasına güvenle koyabilmeniz için şifreler.")
    
    token = getpass.getpass("GitHub Token'ınızı yapıştırın (görünmez): ").strip()
    password = getpass.getpass("Bu token için bir şifre belirleyin: ").strip()
    
    if not token or not password:
        print("Hata: Token veya şifre boş olamaz.")
        return

    key = generate_key(password)
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode()).decode()
    
    print("\n" + "="*50)
    print(f"ŞİFRELENMİŞ TOKEN:\n{encrypted_token}")
    print("="*50)
    print("\nYukarıdaki uzun metni kopyalayıp main.py dosyasındaki 'ENCRYPTED_GITHUB_TOKEN' kısmına yapıştırın.")
    print(f"Siteye girerken belirlediğiniz şifreyi ('{password}') kullanacaksınız.")

if __name__ == "__main__":
    encrypt_token()
