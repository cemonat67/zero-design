"""
Zero@Design - Veritabanı Kurulum ve CSV Import Modülü
CSV dosyalarından SQLite veritabanı oluşturur ve verileri import eder
"""

import sqlite3
import pandas as pd
import os
import re
from typing import Dict, List, Tuple, Optional

class DatabaseSetup:
    def __init__(self, db_path: str = "zero_design.db"):
        """
        Veritabanı kurulum sınıfı
        
        Args:
            db_path: SQLite veritabanı dosya yolu
        """
        self.db_path = db_path
        self.csv_dir = os.path.join(os.path.dirname(__file__), 'templates', 'csv_files')
        
    def create_database(self):
        """Veritabanını oluştur ve tabloları tanımla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bitmiş Ürün İşlemleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finished_product_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                description TEXT,
                applicable_product_groups TEXT,
                co2_min REAL,
                co2_max REAL,
                co2_unit TEXT DEFAULT 'kgCO2e/ürün',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Konfeksiyon Süreçleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS garment_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                process_step TEXT NOT NULL,
                description TEXT,
                applicable_product_groups TEXT,
                co2_min REAL,
                co2_max REAL,
                co2_unit TEXT DEFAULT 'kgCO2e/ürün',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hazır Giyim Master CO2 tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_co2_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upper_category TEXT,
                category TEXT NOT NULL,
                operation TEXT NOT NULL,
                description TEXT,
                applicable_product_groups TEXT,
                co2_range TEXT,
                co2_min REAL,
                co2_max REAL,
                co2_unit TEXT DEFAULT 'kgCO2e/ürün',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ürün Kategorileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CO2 Hesaplama Geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS co2_calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category TEXT,
                total_co2 REAL,
                calculation_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Master Konfeksiyon tablosu (Final_Dosyalar'dan)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_konfeksiyon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT,
                unit TEXT,
                stage TEXT,
                description TEXT,
                min_co2_kg REAL,
                max_co2_kg REAL,
                avg_co2_kg REAL,
                source TEXT,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ürün Kumaş CO2 tablosu (Final_Dosyalar'dan)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_fabric_co2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gender TEXT,
                category TEXT,
                product TEXT,
                fabric_type TEXT,
                composition TEXT,
                usage_hint TEXT,
                co2_kg_per_kg REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Veritabanı tabloları başarıyla oluşturuldu!")
        
    def parse_co2_range(self, co2_value: str) -> Tuple[Optional[float], Optional[float]]:
        """
        CO2 değer aralığını parse eder
        
        Args:
            co2_value: "0.35-0.50" formatındaki string
            
        Returns:
            Tuple[min_value, max_value]
        """
        if pd.isna(co2_value) or not co2_value:
            return None, None
            
        co2_str = str(co2_value).strip()
        
        # Aralık formatı: "0.35-0.50"
        if '-' in co2_str:
            try:
                parts = co2_str.split('-')
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return min_val, max_val
            except (ValueError, IndexError):
                return None, None
        
        # Tek değer
        try:
            val = float(co2_str)
            return val, val
        except ValueError:
            return None, None
    
    def import_finished_product_operations(self):
        """Bitmiş ürün işlemleri CSV'sini import eder"""
        csv_path = os.path.join(self.csv_dir, 'bitmis_urun_islemleri_co2.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dosya bulunamadı: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                co2_min, co2_max = self.parse_co2_range(row.get('CO2 (kgCO2e/ürün)', ''))
                
                cursor.execute('''
                    INSERT INTO finished_product_operations 
                    (category, operation_type, description, applicable_product_groups, 
                     co2_min, co2_max, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Kategori', ''),
                    row.get('İşlem Türü', ''),
                    row.get('Açıklama', ''),
                    row.get('Uygulanan Ürün Grupları', ''),
                    co2_min,
                    co2_max,
                    row.get('Not', '')
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Bitmiş ürün işlemleri import edildi: {len(df)} kayıt")
            
        except Exception as e:
            print(f"❌ Bitmiş ürün işlemleri import hatası: {e}")
    
    def import_garment_processes(self):
        """Konfeksiyon süreçleri CSV'sini import eder"""
        csv_path = os.path.join(self.csv_dir, 'konfeksiyon_surecleri_co2.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dosya bulunamadı: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                co2_min, co2_max = self.parse_co2_range(row.get('CO2 (kgCO2e/ürün)', ''))
                
                cursor.execute('''
                    INSERT INTO garment_processes 
                    (category, process_step, description, applicable_product_groups, 
                     co2_min, co2_max, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Kategori', ''),
                    row.get('İşlem Adımı', ''),
                    row.get('Açıklama', ''),
                    row.get('Uygulanan Ürün Grupları', ''),
                    co2_min,
                    co2_max,
                    row.get('Not', '')
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Konfeksiyon süreçleri import edildi: {len(df)} kayıt")
            
        except Exception as e:
            print(f"❌ Konfeksiyon süreçleri import hatası: {e}")
    
    def import_master_co2_data(self):
        """Master CO2 verilerini import eder"""
        csv_path = os.path.join(self.csv_dir, 'hazir_giyim_master_co2.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dosya bulunamadı: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                co2_range = row.get('CO2 (kgCO2e/ürün)', '')
                co2_min, co2_max = self.parse_co2_range(co2_range)
                
                cursor.execute('''
                    INSERT INTO master_co2_data 
                    (upper_category, category, operation, description, applicable_product_groups, 
                     co2_range, co2_min, co2_max, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Üst Kategori', ''),
                    row.get('Kategori', ''),
                    row.get('İşlem', ''),
                    row.get('Açıklama', ''),
                    row.get('Uygulanan Ürün Grupları', ''),
                    co2_range,
                    co2_min,
                    co2_max,
                    row.get('Not', '')
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Master CO2 verileri import edildi: {len(df)} kayıt")
            
        except Exception as e:
            print(f"❌ Master CO2 verileri import hatası: {e}")
    
    def extract_and_import_categories(self):
        """Tüm CSV dosyalarından ürün kategorilerini çıkarır ve kategoriler tablosuna ekler"""
        categories = set()
        
        # Tüm CSV dosyalarından kategorileri topla
        csv_files = [
            'bitmis_urun_islemleri_co2.csv',
            'konfeksiyon_surecleri_co2.csv',
            'hazir_giyim_master_co2.csv'
        ]
        
        for csv_file in csv_files:
            csv_path = os.path.join(self.csv_dir, csv_file)
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8')
                    
                    # Farklı sütun isimlerini kontrol et
                    category_columns = ['Kategori', 'Üst Kategori', 'category']
                    for col in category_columns:
                        if col in df.columns:
                            categories.update(df[col].dropna().unique())
                            
                    # Ürün gruplarından da kategoriler çıkar
                    if 'Uygulanan Ürün Grupları' in df.columns:
                        for groups in df['Uygulanan Ürün Grupları'].dropna():
                            if isinstance(groups, str):
                                # Virgülle ayrılmış grupları ayır
                                group_list = [g.strip() for g in groups.split(',')]
                                categories.update(group_list)
                                
                except Exception as e:
                    print(f"❌ Kategori çıkarma hatası ({csv_file}): {e}")
        
        # Kategorileri veritabanına ekle
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for category in categories:
            if category and category.strip():
                cursor.execute('''
                    INSERT OR IGNORE INTO product_categories (name)
                    VALUES (?)
                ''', (category.strip(),))
        
        conn.commit()
        conn.close()
        print(f"✅ Ürün kategorileri çıkarıldı: {len(categories)} kategori")
    
    def create_styles_tables(self):
        """Stil verilerini saklamak için tablolar oluştur"""
        try:
            # Ana stil tablosu
            styles_table = """
                CREATE TABLE IF NOT EXISTS styles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    style_code TEXT UNIQUE NOT NULL,
                    product_name TEXT,
                    collection TEXT,
                    category TEXT,
                    size TEXT,
                    market TEXT,
                    net_weight REAL,
                    packaging_weight REAL,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            # Stil lif kompozisyonu tablosu
            style_fibers_table = """
                CREATE TABLE IF NOT EXISTS style_fibers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    style_id INTEGER,
                    fiber_type TEXT,
                    percentage REAL,
                    emission_factor REAL,
                    FOREIGN KEY (style_id) REFERENCES styles (id) ON DELETE CASCADE
                )
            """
            
            # Stil işlemleri tablosu
            style_processes_table = """
                CREATE TABLE IF NOT EXISTS style_processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    style_id INTEGER,
                    process_name TEXT,
                    process_type TEXT,
                    emission_factor REAL,
                    unit TEXT,
                    FOREIGN KEY (style_id) REFERENCES styles (id) ON DELETE CASCADE
                )
            """
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(styles_table)
            cursor.execute(style_fibers_table)
            cursor.execute(style_processes_table)
            conn.commit()
            conn.close()
            
            print("✓ Stil tabloları oluşturuldu")
            
        except Exception as e:
            print(f"✗ Stil tabloları oluşturulurken hata: {e}")
            raise e
    
    def setup_complete_database(self):
        """Tam veritabanı kurulumunu gerçekleştirir"""
        print("🚀 Zero@Design Veritabanı Kurulumu Başlıyor...")
        
        # 1. Veritabanı ve tabloları oluştur
        self.create_database()
        
        # 2. Stil tablolarını oluştur
        self.create_styles_tables()
        
        # 3. CSV dosyalarını import et
        self.import_finished_product_operations()
        self.import_garment_processes()
        self.import_master_co2_data()
        
        # 4. Final_Dosyalar'dan yeni CSV'leri import et
        self.import_master_konfeksiyon()
        self.import_product_fabric_co2()
        
        # 5. Kategorileri çıkar ve ekle
        self.extract_and_import_categories()
        
        print("🎉 Veritabanı kurulumu tamamlandı!")
    
    def import_master_konfeksiyon(self):
        """Master Konfeksiyon CSV'sini import eder"""
        csv_path = os.path.join(self.csv_dir, 'Final_Dosyalar', 'Master_Konfeksiyon copy.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dosya bulunamadı: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Önce tabloyu temizle
            cursor.execute('DELETE FROM master_konfeksiyon')
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO master_konfeksiyon 
                    (category, name, type, unit, stage, description, 
                     min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('category', ''),
                    row.get('name', ''),
                    row.get('type', ''),
                    row.get('unit', ''),
                    row.get('stage', ''),
                    row.get('description', ''),
                    row.get('min_co2_kg', None),
                    row.get('max_co2_kg', None),
                    row.get('avg_co2_kg', None),
                    row.get('source', ''),
                    row.get('source_file', '')
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Master Konfeksiyon import edildi: {len(df)} kayıt")
            
        except Exception as e:
            print(f"❌ Master Konfeksiyon import hatası: {e}")
    
    def import_product_fabric_co2(self):
        """Ürün Kumaş CO2 CSV'sini import eder"""
        csv_path = os.path.join(self.csv_dir, 'Final_Dosyalar', 'Urun_Kumas_CO2_Listesi.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dosya bulunamadı: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', delimiter=';')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Önce tabloyu temizle
            cursor.execute('DELETE FROM product_fabric_co2')
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO product_fabric_co2 
                    (gender, category, product, fabric_type, composition, 
                     usage_hint, co2_kg_per_kg)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('gender', ''),
                    row.get('category', ''),
                    row.get('product', ''),
                    row.get('fabric_type', ''),
                    row.get('composition', ''),
                    row.get('usage_hint', ''),
                    row.get('co2_kg_per_kg', None)
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Ürün Kumaş CO2 import edildi: {len(df)} kayıt")
            
        except Exception as e:
            print(f"❌ Ürün Kumaş CO2 import hatası: {e}")
        self.show_database_stats()
    
    def show_database_stats(self):
        """Veritabanı istatistiklerini gösterir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = [
            ('finished_product_operations', 'Bitmiş Ürün İşlemleri'),
            ('garment_processes', 'Konfeksiyon Süreçleri'),
            ('master_co2_data', 'Master CO2 Verileri'),
            ('product_categories', 'Ürün Kategorileri')
        ]
        
        print("\n📊 Veritabanı İstatistikleri:")
        print("-" * 40)
        
        for table_name, display_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{display_name}: {count} kayıt")
        
        conn.close()

if __name__ == "__main__":
    # Veritabanı kurulumunu çalıştır
    db_setup = DatabaseSetup()
    db_setup.setup_complete_database()