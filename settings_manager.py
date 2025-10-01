"""
Settings Manager - Sistem ayarlarını yönetmek için servis
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

class SettingsManager:
    def __init__(self, db_path: str = "zero_design.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """
        Belirli bir ayar değerini getir
        
        Args:
            key: Ayar anahtarı
            default_value: Bulunamazsa döndürülecek varsayılan değer
            
        Returns:
            Ayar değeri (tip dönüşümü yapılmış)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, data_type FROM settings WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                value, data_type = result
                return self._convert_value(value, data_type)
            else:
                return default_value
                
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default_value
    
    def set_setting(self, key: str, value: Any, description: str = None, data_type: str = None, is_public: bool = False) -> bool:
        """
        Ayar değerini güncelle veya oluştur
        
        Args:
            key: Ayar anahtarı
            value: Yeni değer
            description: Açıklama (opsiyonel)
            data_type: Veri tipi (opsiyonel, otomatik tespit edilir)
            is_public: Genel erişime açık mı
            
        Returns:
            İşlem başarılı mı
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Veri tipini otomatik tespit et
            if data_type is None:
                data_type = self._detect_data_type(value)
            
            # Değeri string'e çevir
            str_value = self._value_to_string(value)
            
            # Mevcut ayarı kontrol et
            cursor.execute('SELECT id FROM settings WHERE key = ?', (key,))
            exists = cursor.fetchone()
            
            if exists:
                # Güncelle
                cursor.execute('''
                    UPDATE settings 
                    SET value = ?, data_type = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                ''', (str_value, data_type, key))
            else:
                # Yeni oluştur
                cursor.execute('''
                    INSERT INTO settings (key, value, description, data_type, is_public)
                    VALUES (?, ?, ?, ?, ?)
                ''', (key, str_value, description, data_type, is_public))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting {key}: {e}")
            return False
    
    def get_all_settings(self, public_only: bool = False) -> Dict[str, Any]:
        """
        Tüm ayarları getir
        
        Args:
            public_only: Sadece genel erişime açık ayarları getir
            
        Returns:
            Ayarlar sözlüğü
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT key, value, data_type FROM settings'
            if public_only:
                query += ' WHERE is_public = 1'
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            settings = {}
            for key, value, data_type in results:
                settings[key] = self._convert_value(value, data_type)
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error getting all settings: {e}")
            return {}
    
    def get_co2_threshold(self) -> float:
        """CO₂ eşik değerini getir"""
        return float(self.get_setting('co2_threshold', 1000))
    
    def set_co2_threshold(self, threshold: float) -> bool:
        """CO₂ eşik değerini ayarla"""
        return self.set_setting('co2_threshold', threshold, 
                               'CO₂ emission threshold in kg', 'number', True)
    
    def get_alert_color(self) -> str:
        """Alert rengi getir"""
        return self.get_setting('alert_color', '#D51635')
    
    def is_threshold_exceeded(self, co2_value: float) -> bool:
        """CO₂ değeri eşiği aşıyor mu kontrol et"""
        threshold = self.get_co2_threshold()
        return co2_value > threshold
    
    def _convert_value(self, value: str, data_type: str) -> Any:
        """String değeri belirtilen tipe çevir"""
        try:
            if data_type == 'number':
                return float(value) if '.' in value else int(value)
            elif data_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif data_type == 'json':
                return json.loads(value)
            else:
                return value
        except:
            return value
    
    def _value_to_string(self, value: Any) -> str:
        """Değeri string'e çevir"""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            return str(value)
    
    def _detect_data_type(self, value: Any) -> str:
        """Değerin tipini tespit et"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı tercihlerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0])
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting user preferences for user {user_id}: {e}")
            return {}
    
    def set_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Kullanıcı tercihlerini ayarla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            preferences_json = json.dumps(preferences)
            cursor.execute('''
                UPDATE users 
                SET preferences = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (preferences_json, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting user preferences for user {user_id}: {e}")
            return False