"""
Zero@Design - Authentication Manager
Kullanıcı kayıt, giriş ve şifre yönetimi modülü
"""

import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import re

class AuthManager:
    def __init__(self, db_path: str = "zero_design.db"):
        """
        Authentication Manager sınıfı
        
        Args:
            db_path: SQLite veritabanı dosya yolu
        """
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı al"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Şifreyi doğrula"""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return stored_hash == password_hash_check.hex()
        except:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Email formatını doğrula"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Şifre güvenliğini kontrol et"""
        if len(password) < 8:
            return False, "Şifre en az 8 karakter olmalıdır"
        
        if not re.search(r'[A-Z]', password):
            return False, "Şifre en az bir büyük harf içermelidir"
        
        if not re.search(r'[a-z]', password):
            return False, "Şifre en az bir küçük harf içermelidir"
        
        if not re.search(r'\d', password):
            return False, "Şifre en az bir rakam içermelidir"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Şifre en az bir özel karakter içermelidir"
        
        return True, "Şifre geçerli"
    
    def register_user(self, username: str, email: str, password: str, 
                     first_name: str = "", last_name: str = "", 
                     company: str = "", phone: str = "") -> Dict[str, any]:
        """
        Yeni kullanıcı kaydet
        
        Returns:
            Dict with success, message, and user_id
        """
        try:
            # Email formatını kontrol et
            if not self._validate_email(email):
                return {"success": False, "error": "Geçersiz email formatı"}
            
            # Şifre güvenliğini kontrol et
            is_valid, message = self._validate_password(password)
            if not is_valid:
                return {"success": False, "error": message}
            
            # Username kontrolü
            if len(username) < 3:
                return {"success": False, "error": "Kullanıcı adı en az 3 karakter olmalıdır"}
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Kullanıcı adı ve email kontrolü
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Bu kullanıcı adı veya email zaten kullanılıyor"}
            
            # Şifreyi hash'le
            password_hash = self._hash_password(password)
            
            # Kullanıcıyı kaydet
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, last_name, company, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, first_name, last_name, company, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Kullanıcı başarıyla kaydedildi", "user_id": user_id}
            
        except Exception as e:
            return {"success": False, "error": f"Kayıt sırasında hata: {str(e)}"}
    
    def login_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Kullanıcı girişi
        
        Returns:
            (success, message, user_data)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Kullanıcıyı bul (username veya email ile)
            cursor.execute('''
                SELECT id, username, email, password_hash, first_name, last_name, 
                       company, phone, is_active, is_verified
                FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            if not user:
                conn.close()
                return False, "Kullanıcı bulunamadı veya hesap deaktif", None
            
            # Şifreyi kontrol et
            if not self._verify_password(password, user['password_hash']):
                conn.close()
                return False, "Hatalı şifre", None
            
            # Son giriş zamanını güncelle
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            conn.close()
            
            # Kullanıcı bilgilerini döndür
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'company': user['company'],
                'phone': user['phone'],
                'is_verified': user['is_verified']
            }
            
            return True, "Giriş başarılı", user_data
            
        except Exception as e:
            return False, f"Giriş sırasında hata: {str(e)}", None
    
    def create_password_reset_token(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Şifre sıfırlama token'ı oluştur
        
        Returns:
            (success, message, token)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Kullanıcıyı bul
            cursor.execute("SELECT id FROM users WHERE email = ? AND is_active = 1", (email,))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return False, "Bu email adresi ile kayıtlı kullanıcı bulunamadı", None
            
            # Eski token'ları temizle
            cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (user['id'],))
            
            # Yeni token oluştur
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)  # 1 saat geçerli
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user['id'], token, expires_at))
            
            conn.commit()
            conn.close()
            
            return True, "Şifre sıfırlama token'ı oluşturuldu", token
            
        except Exception as e:
            return False, f"Token oluşturma hatası: {str(e)}", None
    
    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Token ile şifre sıfırla
        
        Returns:
            (success, message)
        """
        try:
            # Şifre güvenliğini kontrol et
            is_valid, message = self._validate_password(new_password)
            if not is_valid:
                return False, message
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Token'ı kontrol et
            cursor.execute('''
                SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND expires_at > CURRENT_TIMESTAMP AND used = 0
            ''', (token,))
            
            token_data = cursor.fetchone()
            if not token_data:
                conn.close()
                return False, "Geçersiz veya süresi dolmuş token"
            
            # Şifreyi güncelle
            password_hash = self._hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (password_hash, token_data['user_id']))
            
            # Token'ı kullanıldı olarak işaretle
            cursor.execute('''
                UPDATE password_reset_tokens SET used = 1 WHERE token = ?
            ''', (token,))
            
            conn.commit()
            conn.close()
            
            return True, "Şifre başarıyla güncellendi"
            
        except Exception as e:
            return False, f"Şifre sıfırlama hatası: {str(e)}"
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı bilgilerini al"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, first_name, last_name, company, phone, 
                       is_active, is_verified, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            print(f"Kullanıcı bilgisi alma hatası: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: int, first_name: str, last_name: str, email: str) -> Dict[str, any]:
        """Kullanıcı profil bilgilerini güncelle"""
        try:
            # E-posta formatını kontrol et
            if not self._validate_email(email):
                return {'success': False, 'message': 'Geçersiz e-posta formatı'}
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # E-posta başka kullanıcı tarafından kullanılıyor mu kontrol et
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'Bu e-posta adresi zaten kullanılıyor'}
            
            # Profil bilgilerini güncelle
            cursor.execute('''
                UPDATE users SET 
                    first_name = ?, 
                    last_name = ?, 
                    email = ?, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (first_name, last_name, email, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Profil başarıyla güncellendi'}
            
        except Exception as e:
            return {'success': False, 'message': f'Profil güncelleme hatası: {str(e)}'}

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, any]:
        """
        Mevcut şifreyi değiştir
        
        Returns:
            Dict with success status and message
        """
        try:
            # Yeni şifre güvenliğini kontrol et
            is_valid, message = self._validate_password(new_password)
            if not is_valid:
                return {'success': False, 'message': message}
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Mevcut şifreyi kontrol et
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return {'success': False, 'message': 'Kullanıcı bulunamadı'}
            
            if not self._verify_password(old_password, user['password_hash']):
                conn.close()
                return {'success': False, 'message': 'Mevcut şifre hatalı'}
            
            # Yeni şifreyi kaydet
            password_hash = self._hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Şifre başarıyla değiştirildi'}
            
        except Exception as e:
            return {'success': False, 'message': f'Şifre değiştirme hatası: {str(e)}'}