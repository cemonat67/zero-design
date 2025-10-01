"""
Zero@Design CO₂ Hesaplama Modülü
Kullanıcının seçtiği kumaş, aksesuar ve işlemlere göre toplam CO₂ değerini hesaplar.
"""

import logging
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CO2Calculator:
    """CO₂ hesaplama servisi"""
    
    def __init__(self):
        """Veritabanı bağlantısını başlat"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'zero_design'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123')
        }
    
    def get_db_connection(self):
        """Veritabanı bağlantısı oluştur"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    def get_fabric_co2(self, fabric_id: str, quantity_kg: float = 1.0) -> Dict:
        """
        Kumaş CO₂ değerini getir
        
        Args:
            fabric_id: Kumaş UUID'si
            quantity_kg: Kumaş miktarı (kg)
            
        Returns:
            Dict: CO₂ değeri ve detayları
        """
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            id,
                            fabric_type,
                            composition,
                            co2_kg_per_kg,
                            gender,
                            category,
                            product
                        FROM fabrics 
                        WHERE id = %s
                    """, (fabric_id,))
                    
                    fabric = cursor.fetchone()
                    
                    if not fabric:
                        return {
                            'error': f'Kumaş bulunamadı: {fabric_id}',
                            'co2_kg': 0,
                            'details': {}
                        }
                    
                    co2_per_kg = fabric['co2_kg_per_kg'] or 0
                    total_co2 = float(co2_per_kg) * quantity_kg
                    
                    return {
                        'co2_kg': round(total_co2, 4),
                        'details': {
                            'fabric_type': fabric['fabric_type'],
                            'composition': fabric['composition'],
                            'co2_per_kg': float(co2_per_kg),
                            'quantity_kg': quantity_kg,
                            'gender': fabric['gender'],
                            'category': fabric['category'],
                            'product': fabric['product']
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Kumaş CO₂ hesaplama hatası: {e}")
            return {
                'error': str(e),
                'co2_kg': 0,
                'details': {}
            }
    
    def get_accessories_co2(self, accessory_ids: List[str], quantities: List[float] = None) -> Dict:
        """
        Aksesuar CO₂ değerlerini getir
        
        Args:
            accessory_ids: Aksesuar UUID listesi
            quantities: Her aksesuar için miktar listesi (kg)
            
        Returns:
            Dict: Toplam CO₂ değeri ve detayları
        """
        if not accessory_ids:
            return {
                'co2_kg': 0,
                'details': [],
                'total_accessories': 0
            }
        
        if quantities is None:
            quantities = [1.0] * len(accessory_ids)
        
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # IN clause için placeholder oluştur
                    placeholders = ','.join(['%s'] * len(accessory_ids))
                    
                    cursor.execute(f"""
                        SELECT 
                            id,
                            accessory_name,
                            material,
                            composition,
                            co2_kg_per_kg,
                            gender,
                            category,
                            product,
                            unit
                        FROM accessories 
                        WHERE id IN ({placeholders})
                    """, accessory_ids)
                    
                    accessories = cursor.fetchall()
                    
                    total_co2 = 0
                    details = []
                    
                    for i, accessory in enumerate(accessories):
                        quantity = quantities[i] if i < len(quantities) else 1.0
                        co2_per_kg = accessory['co2_kg_per_kg'] or 0
                        accessory_co2 = float(co2_per_kg) * quantity
                        total_co2 += accessory_co2
                        
                        details.append({
                            'id': str(accessory['id']),
                            'name': accessory['accessory_name'],
                            'material': accessory['material'],
                            'composition': accessory['composition'],
                            'co2_per_kg': float(co2_per_kg),
                            'quantity_kg': quantity,
                            'co2_total': round(accessory_co2, 4),
                            'gender': accessory['gender'],
                            'category': accessory['category'],
                            'product': accessory['product'],
                            'unit': accessory['unit']
                        })
                    
                    return {
                        'co2_kg': round(total_co2, 4),
                        'details': details,
                        'total_accessories': len(accessories)
                    }
                    
        except Exception as e:
            logger.error(f"Aksesuar CO₂ hesaplama hatası: {e}")
            return {
                'error': str(e),
                'co2_kg': 0,
                'details': [],
                'total_accessories': 0
            }
    
    def get_processes_co2(self, process_ids: List[str]) -> Dict:
        """
        İşlem CO₂ değerlerini getir
        
        Args:
            process_ids: İşlem UUID listesi
            
        Returns:
            Dict: Toplam CO₂ değeri ve detayları
        """
        if not process_ids:
            return {
                'co2_kg': 0,
                'details': [],
                'total_processes': 0
            }
        
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Önce processes tablosundan işlem detaylarını al
                    placeholders = ','.join(['%s'] * len(process_ids))
                    
                    cursor.execute(f"""
                        SELECT 
                            p.id,
                            p.category,
                            p.stage_group,
                            p.stage,
                            p.process_name,
                            p.unit,
                            p.description,
                            p.applied_products,
                            e.min_co2_kg,
                            e.max_co2_kg,
                            e.avg_co2_kg,
                            e.source,
                            e.notes
                        FROM processes p
                        LEFT JOIN emissions e ON p.id = e.process_id
                        WHERE p.id IN ({placeholders})
                    """, process_ids)
                    
                    processes = cursor.fetchall()
                    
                    # Eğer processes tablosunda bulunamazsa lifecycle_master'dan dene
                    if not processes:
                        cursor.execute(f"""
                            SELECT 
                                id,
                                upper_category,
                                category,
                                stage_group,
                                stage,
                                process_name,
                                input_material,
                                unit,
                                description,
                                applied_products,
                                min_co2_kg,
                                max_co2_kg,
                                avg_co2_kg,
                                notes,
                                source
                            FROM lifecycle_master
                            WHERE id IN ({placeholders})
                        """, process_ids)
                        
                        processes = cursor.fetchall()
                    
                    total_co2 = 0
                    details = []
                    
                    for process in processes:
                        avg_co2 = process.get('avg_co2_kg', 0) or 0
                        total_co2 += float(avg_co2)
                        
                        details.append({
                            'id': str(process['id']),
                            'name': process['process_name'],
                            'category': process['category'],
                            'stage_group': process.get('stage_group'),
                            'stage': process.get('stage'),
                            'unit': process.get('unit'),
                            'description': process.get('description'),
                            'applied_products': process.get('applied_products'),
                            'min_co2_kg': float(process.get('min_co2_kg', 0) or 0),
                            'max_co2_kg': float(process.get('max_co2_kg', 0) or 0),
                            'avg_co2_kg': float(avg_co2),
                            'source': process.get('source'),
                            'notes': process.get('notes')
                        })
                    
                    return {
                        'co2_kg': round(total_co2, 4),
                        'details': details,
                        'total_processes': len(processes)
                    }
                    
        except Exception as e:
            logger.error(f"İşlem CO₂ hesaplama hatası: {e}")
            return {
                'error': str(e),
                'co2_kg': 0,
                'details': [],
                'total_processes': 0
            }
    
    def calculate_total_co2(self, 
                           fabric_id: Optional[str] = None,
                           fabric_quantity_kg: float = 1.0,
                           accessory_ids: List[str] = None,
                           accessory_quantities: List[float] = None,
                           process_ids: List[str] = None) -> Dict:
        """
        Toplam CO₂ değerini hesapla
        
        Args:
            fabric_id: Kumaş UUID'si
            fabric_quantity_kg: Kumaş miktarı (kg)
            accessory_ids: Aksesuar UUID listesi
            accessory_quantities: Aksesuar miktar listesi (kg)
            process_ids: İşlem UUID listesi
            
        Returns:
            Dict: Toplam CO₂ ve detaylı breakdown
        """
        try:
            # Kumaş CO₂
            fabric_result = {'co2_kg': 0, 'details': {}}
            if fabric_id:
                fabric_result = self.get_fabric_co2(fabric_id, fabric_quantity_kg)
            
            # Aksesuar CO₂
            accessories_result = self.get_accessories_co2(accessory_ids or [], accessory_quantities)
            
            # İşlem CO₂
            processes_result = self.get_processes_co2(process_ids or [])
            
            # Toplam hesaplama
            total_co2 = (
                fabric_result.get('co2_kg', 0) +
                accessories_result.get('co2_kg', 0) +
                processes_result.get('co2_kg', 0)
            )
            
            # Detaylı breakdown
            breakdown = {
                'total_co2_kg': round(total_co2, 4),
                'fabric': fabric_result,
                'accessories': accessories_result,
                'processes': processes_result,
                'calculation_date': datetime.now().isoformat(),
                'summary': {
                    'fabric_co2': fabric_result.get('co2_kg', 0),
                    'accessories_co2': accessories_result.get('co2_kg', 0),
                    'processes_co2': processes_result.get('co2_kg', 0),
                    'total_items': (
                        (1 if fabric_id else 0) +
                        accessories_result.get('total_accessories', 0) +
                        processes_result.get('total_processes', 0)
                    )
                }
            }
            
            # Hata kontrolü
            errors = []
            if 'error' in fabric_result:
                errors.append(f"Kumaş: {fabric_result['error']}")
            if 'error' in accessories_result:
                errors.append(f"Aksesuar: {accessories_result['error']}")
            if 'error' in processes_result:
                errors.append(f"İşlem: {processes_result['error']}")
            
            if errors:
                breakdown['errors'] = errors
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Toplam CO₂ hesaplama hatası: {e}")
            return {
                'error': str(e),
                'total_co2_kg': 0,
                'fabric': {'co2_kg': 0, 'details': {}},
                'accessories': {'co2_kg': 0, 'details': [], 'total_accessories': 0},
                'processes': {'co2_kg': 0, 'details': [], 'total_processes': 0}
            }
    
    def get_available_items(self) -> Dict:
        """
        Mevcut kumaş, aksesuar ve işlemleri listele
        
        Returns:
            Dict: Mevcut öğelerin listesi
        """
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Kumaşlar
                    cursor.execute("""
                        SELECT id, fabric_type, composition, co2_kg_per_kg, gender, category, product
                        FROM fabrics 
                        WHERE co2_kg_per_kg IS NOT NULL
                        ORDER BY fabric_type
                    """)
                    fabrics = cursor.fetchall()
                    
                    # Aksesuarlar
                    cursor.execute("""
                        SELECT id, accessory_name, material, co2_kg_per_kg, gender, category, product
                        FROM accessories 
                        WHERE co2_kg_per_kg IS NOT NULL
                        ORDER BY accessory_name
                    """)
                    accessories = cursor.fetchall()
                    
                    # İşlemler
                    cursor.execute("""
                        SELECT p.id, p.process_name, p.category, p.stage_group, e.avg_co2_kg
                        FROM processes p
                        LEFT JOIN emissions e ON p.id = e.process_id
                        WHERE e.avg_co2_kg IS NOT NULL
                        ORDER BY p.category, p.process_name
                    """)
                    processes = cursor.fetchall()
                    
                    return {
                        'fabrics': [dict(fabric) for fabric in fabrics],
                        'accessories': [dict(accessory) for accessory in accessories],
                        'processes': [dict(process) for process in processes],
                        'total_items': len(fabrics) + len(accessories) + len(processes)
                    }
                    
        except Exception as e:
            logger.error(f"Mevcut öğeleri getirme hatası: {e}")
            return {
                'error': str(e),
                'fabrics': [],
                'accessories': [],
                'processes': [],
                'total_items': 0
            }

# Singleton instance
co2_calculator = CO2Calculator()