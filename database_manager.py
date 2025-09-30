"""
Zero@Design - Veritabanı Yönetici Modülü
SQLite veritabanı ile etkileşim için yardımcı sınıflar
"""

import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "zero_design.db"):
        """
        Veritabanı yönetici sınıfı
        
        Args:
            db_path: SQLite veritabanı dosya yolu
        """
        self.db_path = db_path
    
    def get_connection(self):
        """Veritabanı bağlantısı oluşturur"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like access
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        SQL sorgusu çalıştırır ve sonuçları döndürür
        
        Args:
            query: SQL sorgusu
            params: Sorgu parametreleri
            
        Returns:
            Sorgu sonuçları listesi
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        INSERT sorgusu çalıştırır ve yeni kaydın ID'sini döndürür
        
        Args:
            query: INSERT sorgusu
            params: Sorgu parametreleri
            
        Returns:
            Yeni kaydın ID'si
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id
    
    # Bitmiş Ürün İşlemleri Sorguları
    def get_finished_product_operations(self, category: Optional[str] = None) -> List[Dict]:
        """
        Bitmiş ürün işlemlerini getirir
        
        Args:
            category: Kategori filtresi (opsiyonel)
            
        Returns:
            İşlem listesi
        """
        query = "SELECT * FROM finished_product_operations"
        params = ()
        
        if category:
            query += " WHERE category LIKE ?"
            params = (f"%{category}%",)
        
        query += " ORDER BY category, operation_type"
        return self.execute_query(query, params)
    
    def get_operations_by_product_group(self, product_group: str) -> List[Dict]:
        """
        Ürün grubuna göre işlemleri getirir
        
        Args:
            product_group: Ürün grubu adı
            
        Returns:
            İşlem listesi
        """
        query = """
            SELECT * FROM finished_product_operations 
            WHERE applicable_product_groups LIKE ?
            ORDER BY category, operation_type
        """
        return self.execute_query(query, (f"%{product_group}%",))
    
    # Konfeksiyon Süreçleri Sorguları
    def get_garment_processes(self, category: Optional[str] = None) -> List[Dict]:
        """
        Konfeksiyon süreçlerini getirir
        
        Args:
            category: Kategori filtresi (opsiyonel)
            
        Returns:
            Süreç listesi
        """
        query = "SELECT * FROM garment_processes"
        params = ()
        
        if category:
            query += " WHERE category LIKE ?"
            params = (f"%{category}%",)
        
        query += " ORDER BY category, process_step"
        return self.execute_query(query, params)
    
    # Master CO2 Verileri Sorguları
    def get_master_co2_data(self, category: Optional[str] = None, 
                           operation: Optional[str] = None) -> List[Dict]:
        """
        Master CO2 verilerini getirir
        
        Args:
            category: Kategori filtresi (opsiyonel)
            operation: İşlem filtresi (opsiyonel)
            
        Returns:
            CO2 veri listesi
        """
        query = "SELECT * FROM master_co2_data WHERE 1=1"
        params = []
        
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        
        if operation:
            query += " AND operation LIKE ?"
            params.append(f"%{operation}%")
        
        query += " ORDER BY upper_category, category, operation"
        return self.execute_query(query, tuple(params))
    
    # Ürün Kategorileri Sorguları
    def get_product_categories(self) -> List[Dict]:
        """
        Tüm ürün kategorilerini getirir
        
        Returns:
            Kategori listesi
        """
        query = "SELECT * FROM product_categories ORDER BY name"
        return self.execute_query(query)
    
    def search_categories(self, search_term: str) -> List[Dict]:
        """
        Kategori arama yapar
        
        Args:
            search_term: Arama terimi
            
        Returns:
            Bulunan kategoriler
        """
        query = "SELECT * FROM product_categories WHERE name LIKE ? ORDER BY name"
        return self.execute_query(query, (f"%{search_term}%",))
    
    # CO2 Hesaplama İşlemleri
    def calculate_product_co2(self, product_name: str, selected_operations: List[Dict]) -> Dict:
        """
        Ürün için CO2 hesaplaması yapar
        
        Args:
            product_name: Ürün adı
            selected_operations: Seçilen işlemler listesi
            
        Returns:
            Hesaplama sonucu
        """
        total_co2_min = 0
        total_co2_max = 0
        calculation_details = []
        
        for operation in selected_operations:
            co2_min = operation.get('co2_min', 0) or 0
            co2_max = operation.get('co2_max', 0) or 0
            
            total_co2_min += co2_min
            total_co2_max += co2_max
            
            calculation_details.append({
                'operation': operation.get('operation_type') or operation.get('process_step') or operation.get('operation'),
                'category': operation.get('category'),
                'co2_min': co2_min,
                'co2_max': co2_max
            })
        
        # Hesaplama sonucunu kaydet
        calculation_id = self.save_co2_calculation(
            product_name, 
            total_co2_min, 
            total_co2_max, 
            calculation_details
        )
        
        return {
            'calculation_id': calculation_id,
            'product_name': product_name,
            'total_co2_min': total_co2_min,
            'total_co2_max': total_co2_max,
            'total_co2_avg': (total_co2_min + total_co2_max) / 2,
            'operation_count': len(selected_operations),
            'calculation_details': calculation_details
        }
    
    def save_co2_calculation(self, product_name: str, co2_min: float, 
                           co2_max: float, details: List[Dict]) -> int:
        """
        CO2 hesaplama sonucunu kaydeder
        
        Args:
            product_name: Ürün adı
            co2_min: Minimum CO2 değeri
            co2_max: Maksimum CO2 değeri
            details: Hesaplama detayları
            
        Returns:
            Kayıt ID'si
        """
        total_co2 = (co2_min + co2_max) / 2
        details_json = json.dumps(details, ensure_ascii=False)
        
        query = """
            INSERT INTO co2_calculations 
            (product_name, total_co2, calculation_details)
            VALUES (?, ?, ?)
        """
        
        return self.execute_insert(query, (product_name, total_co2, details_json))
    
    def get_co2_calculations(self, limit: int = 50) -> List[Dict]:
        """
        CO2 hesaplama geçmişini getirir
        
        Args:
            limit: Maksimum kayıt sayısı
            
        Returns:
            Hesaplama geçmişi
        """
        query = """
            SELECT * FROM co2_calculations 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    # Arama ve Filtreleme
    def search_operations(self, search_term: str) -> Dict[str, List[Dict]]:
        """
        Tüm tablolarda işlem arama yapar
        
        Args:
            search_term: Arama terimi
            
        Returns:
            Arama sonuçları
        """
        results = {
            'finished_product_operations': [],
            'garment_processes': [],
            'master_co2_data': []
        }
        
        # Bitmiş ürün işlemleri arama
        query1 = """
            SELECT * FROM finished_product_operations 
            WHERE operation_type LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY category, operation_type
        """
        search_param = f"%{search_term}%"
        results['finished_product_operations'] = self.execute_query(
            query1, (search_param, search_param, search_param)
        )
        
        # Konfeksiyon süreçleri arama
        query2 = """
            SELECT * FROM garment_processes 
            WHERE process_step LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY category, process_step
        """
        results['garment_processes'] = self.execute_query(
            query2, (search_param, search_param, search_param)
        )
        
        # Master CO2 verileri arama
        query3 = """
            SELECT * FROM master_co2_data 
            WHERE operation LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY upper_category, category, operation
        """
        results['master_co2_data'] = self.execute_query(
            query3, (search_param, search_param, search_param)
        )
        
        return results
    
    # İstatistikler
    def get_database_stats(self) -> Dict:
        """
        Veritabanı istatistiklerini getirir
        
        Returns:
            İstatistik bilgileri
        """
        stats = {}
        
        tables = [
            'finished_product_operations',
            'garment_processes', 
            'master_co2_data',
            'product_categories',
            'co2_calculations'
        ]
        
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = self.execute_query(query)
            stats[table] = result[0]['count'] if result else 0
        
        # CO2 değer aralıkları
        co2_stats_query = """
            SELECT 
                MIN(co2_min) as min_co2,
                MAX(co2_max) as max_co2,
                AVG((co2_min + co2_max) / 2) as avg_co2
            FROM master_co2_data 
            WHERE co2_min IS NOT NULL AND co2_max IS NOT NULL
        """
        co2_stats = self.execute_query(co2_stats_query)
        if co2_stats:
            stats['co2_range'] = co2_stats[0]
        
        return stats
    
    def get_categories_by_table(self) -> Dict[str, List[str]]:
        """
        Her tablo için kategori listesini getirir
        
        Returns:
            Tablo bazında kategori listeleri
        """
        categories = {}
        
        # Bitmiş ürün işlemleri kategorileri
        query1 = "SELECT DISTINCT category FROM finished_product_operations ORDER BY category"
        categories['finished_product_operations'] = [
            row['category'] for row in self.execute_query(query1)
        ]
        
        # Konfeksiyon süreçleri kategorileri
        query2 = "SELECT DISTINCT category FROM garment_processes ORDER BY category"
        categories['garment_processes'] = [
            row['category'] for row in self.execute_query(query2)
        ]
        
        # Master CO2 kategorileri
        query3 = "SELECT DISTINCT category FROM master_co2_data ORDER BY category"
        categories['master_co2_data'] = [
            row['category'] for row in self.execute_query(query3)
        ]
        
        return categories
    
    def get_master_konfeksiyon_data(self, category: Optional[str] = None, 
                                   name: Optional[str] = None) -> List[Dict]:
        """
        Master konfeksiyon verilerini getirir
        
        Args:
            category: Kategori filtresi
            name: İsim filtresi
            
        Returns:
            Master konfeksiyon verileri listesi
        """
        query = "SELECT * FROM master_konfeksiyon WHERE 1=1"
        params = []
        
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
            
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
            
        query += " ORDER BY category, name"
        
        return self.execute_query(query, tuple(params))
    
    def get_product_fabric_co2_data(self, gender: Optional[str] = None,
                                   category: Optional[str] = None,
                                   product: Optional[str] = None,
                                   fabric_type: Optional[str] = None) -> List[Dict]:
        """
        Ürün kumaş CO2 verilerini getirir
        
        Args:
            gender: Cinsiyet filtresi
            category: Kategori filtresi  
            product: Ürün filtresi
            fabric_type: Kumaş tipi filtresi
            
        Returns:
            Ürün kumaş CO2 verileri listesi
        """
        query = "SELECT * FROM product_fabric_co2 WHERE 1=1"
        params = []
        
        if gender:
            query += " AND gender = ?"
            params.append(gender)
            
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
            
        if product:
            query += " AND product LIKE ?"
            params.append(f"%{product}%")
            
        if fabric_type:
            query += " AND fabric_type LIKE ?"
            params.append(f"%{fabric_type}%")
            
        query += " ORDER BY gender, category, product"
        
        return self.execute_query(query, tuple(params))
    
    def get_fabric_types(self) -> List[str]:
        """Tüm kumaş tiplerini getirir"""
        query = "SELECT DISTINCT fabric_type FROM product_fabric_co2 WHERE fabric_type IS NOT NULL ORDER BY fabric_type"
        results = self.execute_query(query)
        return [row['fabric_type'] for row in results]
    
    def get_compositions(self) -> List[str]:
        """Tüm kompozisyonları getirir"""
        query = "SELECT DISTINCT composition FROM product_fabric_co2 WHERE composition IS NOT NULL ORDER BY composition"
        results = self.execute_query(query)
        return [row['composition'] for row in results]
    
    def search_fabric_by_composition(self, composition_search: str) -> List[Dict]:
        """Kompozisyona göre kumaş arar"""
        query = """
            SELECT * FROM product_fabric_co2 
            WHERE composition LIKE ? 
            ORDER BY co2_kg_per_kg ASC
        """
        return self.execute_query(query, (f"%{composition_search}%",))
    
    def save_style_data(self, data):
        """Stil verilerini database'e kaydet"""
        try:
            # Stil bilgilerini kaydet
            style_query = """
                INSERT INTO styles (
                    style_code, product_name, collection, category, size, 
                    market, net_weight, packaging_weight, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            style_values = (
                data.get('styleCode', ''),
                data.get('productName', ''),
                data.get('collection', ''),
                data.get('category', ''),
                data.get('size', ''),
                data.get('market', ''),
                data.get('netWeight', 0),
                data.get('packagingWeight', 0),
                data.get('notes', '')
            )
            
            cursor = self.conn.cursor()
            cursor.execute(style_query, style_values)
            style_id = cursor.lastrowid
            
            # Lif kompozisyonunu kaydet
            if 'fibers' in data:
                for fiber in data['fibers']:
                    fiber_query = """
                        INSERT INTO style_fibers (
                            style_id, fiber_type, percentage, emission_factor
                        ) VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(fiber_query, (
                        style_id,
                        fiber.get('type', ''),
                        fiber.get('percentage', 0),
                        fiber.get('emissionFactor', 0)
                    ))
            
            # İşlemleri kaydet
            if 'processes' in data:
                for process in data['processes']:
                    process_query = """
                        INSERT INTO style_processes (
                            style_id, process_name, process_type, emission_factor, unit
                        ) VALUES (?, ?, ?, ?, ?)
                    """
                    cursor.execute(process_query, (
                        style_id,
                        process.get('name', ''),
                        process.get('type', ''),
                        process.get('factor', 0),
                        process.get('unit', '')
                    ))
            
            self.conn.commit()
            return style_id
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_style_data(self, style_code):
        """Stil verilerini getir"""
        try:
            # Ana stil bilgilerini getir
            style_query = """
                SELECT * FROM styles WHERE style_code = ?
            """
            style_data = self.execute_query(style_query, (style_code,))
            
            if not style_data:
                return None
            
            style = style_data[0]
            
            # Lif kompozisyonunu getir
            fiber_query = """
                SELECT * FROM style_fibers WHERE style_id = ?
            """
            fibers = self.execute_query(fiber_query, (style['id'],))
            
            # İşlemleri getir
            process_query = """
                SELECT * FROM style_processes WHERE style_id = ?
            """
            processes = self.execute_query(process_query, (style['id'],))
            
            return {
                'style': style,
                'fibers': fibers,
                'processes': processes
            }
            
        except Exception as e:
            raise e
    
    def get_all_styles(self):
        """Tüm stilleri listele"""
        try:
            query = """
                SELECT id, style_code, product_name, collection, category, 
                       created_at FROM styles ORDER BY created_at DESC
            """
            return self.execute_query(query)
            
        except Exception as e:
            raise e
    
    def get_co2_range_by_category(self, category: str) -> Dict:
        """Kategoriye göre CO2 aralığını getirir"""
        # Master konfeksiyon verilerinden
        query1 = """
            SELECT MIN(min_co2_kg) as min_co2, MAX(max_co2_kg) as max_co2, AVG(avg_co2_kg) as avg_co2
            FROM master_konfeksiyon 
            WHERE category LIKE ?
        """
        
        # Kumaş verilerinden
        query2 = """
            SELECT MIN(co2_kg_per_kg) as min_co2, MAX(co2_kg_per_kg) as max_co2, AVG(co2_kg_per_kg) as avg_co2
            FROM product_fabric_co2 
            WHERE category LIKE ?
        """
        
        konfeksiyon_data = self.execute_query(query1, (f"%{category}%",))
        fabric_data = self.execute_query(query2, (f"%{category}%",))
        
        return {
            'konfeksiyon': konfeksiyon_data[0] if konfeksiyon_data else {},
            'fabric': fabric_data[0] if fabric_data else {}
        }

# Singleton instance
db_manager = DatabaseManager()