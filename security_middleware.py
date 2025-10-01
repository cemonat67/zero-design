"""
Zero@Design - Security Middleware
Session yönetimi ve güvenlik katmanı
"""

from functools import wraps
from flask import session, request, jsonify, redirect, url_for
import time
import hashlib
import secrets
from datetime import datetime, timedelta

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.session_timeout = 3600  # 1 saat
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 dakika
        self.failed_attempts = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask uygulamasını başlat"""
        self.app = app
        
        # Session konfigürasyonu
        app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS için
        app.config['SESSION_COOKIE_HTTPONLY'] = True  # XSS koruması
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF koruması
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=self.session_timeout)
        
        # Her request öncesi güvenlik kontrolü
        app.before_request(self.before_request)
    
    def before_request(self):
        """Her request öncesi çalışan güvenlik kontrolü"""
        # Session timeout kontrolü
        if 'user_id' in session:
            if 'last_activity' in session:
                last_activity = session['last_activity']
                if time.time() - last_activity > self.session_timeout:
                    session.clear()
                    if request.is_json:
                        return jsonify({'error': 'Session süresi doldu', 'redirect': '/signin'}), 401
                    else:
                        return redirect(url_for('signin'))
            
            # Son aktivite zamanını güncelle
            session['last_activity'] = time.time()
        
        # Rate limiting kontrolü
        client_ip = self.get_client_ip()
        if self.is_rate_limited(client_ip):
            return jsonify({'error': 'Çok fazla istek. Lütfen daha sonra tekrar deneyin.'}), 429
    
    def get_client_ip(self):
        """İstemci IP adresini al"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_rate_limited(self, ip):
        """Rate limiting kontrolü"""
        current_time = time.time()
        
        # Eski kayıtları temizle
        if ip in self.failed_attempts:
            self.failed_attempts[ip] = [
                attempt for attempt in self.failed_attempts[ip]
                if current_time - attempt < self.lockout_duration
            ]
        
        # Başarısız giriş sayısını kontrol et
        if ip in self.failed_attempts:
            return len(self.failed_attempts[ip]) >= self.max_login_attempts
        
        return False
    
    def record_failed_attempt(self, ip):
        """Başarısız giriş denemesini kaydet"""
        current_time = time.time()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        self.failed_attempts[ip].append(current_time)
    
    def clear_failed_attempts(self, ip):
        """Başarılı giriş sonrası başarısız denemeleri temizle"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
    
    def generate_csrf_token(self):
        """CSRF token oluştur"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']
    
    def validate_csrf_token(self, token):
        """CSRF token doğrula"""
        return token and session.get('csrf_token') == token
    
    def hash_password(self, password, salt=None):
        """Şifreyi hash'le"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # PBKDF2 ile güvenli hash
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterasyon
        )
        
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password, hashed_password):
        """Şifreyi doğrula"""
        try:
            salt, password_hash = hashed_password.split(':')
            
            # Aynı salt ile hash'le ve karşılaştır
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return new_hash.hex() == password_hash
        except:
            return False
    
    def create_session(self, user_id, user_email, user_name):
        """Güvenli session oluştur"""
        session.permanent = True
        session['user_id'] = user_id
        session['user_email'] = user_email
        session['user_name'] = user_name
        session['login_time'] = time.time()
        session['last_activity'] = time.time()
        session['session_id'] = secrets.token_hex(32)
        
        # CSRF token oluştur
        self.generate_csrf_token()
    
    def destroy_session(self):
        """Session'ı güvenli şekilde yok et"""
        session.clear()
    
    def is_authenticated(self):
        """Kullanıcının giriş yapıp yapmadığını kontrol et"""
        return 'user_id' in session and 'session_id' in session
    
    def get_current_user_id(self):
        """Mevcut kullanıcının ID'sini al"""
        return session.get('user_id')
    
    def sanitize_input(self, input_string):
        """Kullanıcı girdilerini temizle"""
        if not isinstance(input_string, str):
            return input_string
        
        # HTML karakterlerini escape et
        import html
        return html.escape(input_string.strip())
    
    def validate_email_format(self, email):
        """E-posta formatını doğrula"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password_strength(self, password):
        """Şifre gücünü kontrol et"""
        if len(password) < 6:
            return False, "Şifre en az 6 karakter olmalıdır"
        
        if len(password) < 8:
            return False, "Güvenlik için en az 8 karakter önerilir"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        score = sum([has_upper, has_lower, has_digit, has_special])
        
        if score < 2:
            return False, "Şifre büyük harf, küçük harf, rakam ve özel karakter içermelidir"
        
        return True, "Şifre güçlü"

def require_auth(f):
    """Authentication gerektiren route'lar için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Giriş yapmanız gerekiyor', 'redirect': '/signin'}), 401
            else:
                return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

def require_csrf(f):
    """CSRF koruması gerektiren route'lar için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not token or session.get('csrf_token') != token:
                return jsonify({'error': 'CSRF token geçersiz'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Admin yetkisi gerektiren route'lar için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Giriş yapmanız gerekiyor'}), 401
            else:
                return redirect(url_for('signin'))
        
        # Admin kontrolü (bu örnekte basit bir kontrol)
        # Gerçek uygulamada veritabanından kullanıcı rolü kontrol edilir
        user_email = session.get('user_email', '')
        if not user_email.endswith('@admin.com'):  # Örnek admin kontrolü
            return jsonify({'error': 'Admin yetkisi gerekiyor'}), 403
        
        return f(*args, **kwargs)
    return decorated_function