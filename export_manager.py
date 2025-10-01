"""
Export Manager - CSV ve PDF export işlemleri için yardımcı sınıf
Zero@Design Eco-Design Platform
"""

import pandas as pd
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from database_setup import DatabaseSetup
import logging

class ExportManager:
    def __init__(self):
        self.db = DatabaseSetup()
        self.logger = logging.getLogger(__name__)
    
    def export_to_csv(self, data, filename_prefix="export"):
        """
        Veriyi CSV formatında export et
        
        Args:
            data: Export edilecek veri (list of dict veya pandas DataFrame)
            filename_prefix: Dosya adı öneki
            
        Returns:
            tuple: (csv_content, filename)
        """
        try:
            # Veriyi DataFrame'e çevir
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError("Desteklenmeyen veri formatı")
            
            if df.empty:
                raise ValueError("Export edilecek veri bulunamadı")
            
            # CSV içeriğini oluştur
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue()
            
            # Dosya adını oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.csv"
            
            return csv_content, filename
            
        except Exception as e:
            self.logger.error(f"CSV export hatası: {str(e)}")
            raise
    
    def export_to_pdf(self, data, title="Export Raporu", filename_prefix="export"):
        """
        Veriyi PDF formatında export et
        
        Args:
            data: Export edilecek veri (list of dict)
            title: PDF başlığı
            filename_prefix: Dosya adı öneki
            
        Returns:
            tuple: (pdf_content, filename)
        """
        try:
            if not data:
                raise ValueError("Export edilecek veri bulunamadı")
            
            # PDF buffer oluştur
            pdf_buffer = io.BytesIO()
            
            # PDF dokümanını oluştur
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Stil tanımlamaları
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            # PDF içeriğini oluştur
            story = []
            
            # Başlık ekle
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Tarih bilgisi ekle
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            story.append(Paragraph(f"Rapor Tarihi: {date_str}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Veriyi tablo olarak ekle
            if isinstance(data, list) and len(data) > 0:
                # Sütun başlıklarını al
                headers = list(data[0].keys())
                
                # Tablo verilerini hazırla
                table_data = [headers]  # Başlık satırı
                
                for row in data:
                    table_row = []
                    for header in headers:
                        value = row.get(header, '')
                        # Değeri string'e çevir ve uzun metinleri kısalt
                        str_value = str(value)
                        if len(str_value) > 50:
                            str_value = str_value[:47] + "..."
                        table_row.append(str_value)
                    table_data.append(table_row)
                
                # Tablo oluştur
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            # Özet bilgiler ekle
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Toplam Kayıt Sayısı: {len(data)}", styles['Normal']))
            
            # PDF'i oluştur
            doc.build(story)
            
            # PDF içeriğini al
            pdf_content = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            # Dosya adını oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.pdf"
            
            return pdf_content, filename
            
        except Exception as e:
            self.logger.error(f"PDF export hatası: {str(e)}")
            raise
    
    def get_dashboard_data_for_export(self, user_id=None, filters=None):
        """
        Dashboard verilerini export için hazırla
        
        Args:
            user_id: Kullanıcı ID'si (opsiyonel)
            filters: Filtre parametreleri (opsiyonel)
            
        Returns:
            list: Export edilecek veri listesi
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Temel sorgu
            query = """
            SELECT 
                f.name as fabric_name,
                f.avg_co2_kg as fabric_co2,
                a.name as accessory_name,
                a.avg_co2_kg as accessory_co2,
                p.name as process_name,
                p.avg_co2_kg as process_co2,
                (f.avg_co2_kg + COALESCE(a.avg_co2_kg, 0) + COALESCE(p.avg_co2_kg, 0)) as total_co2
            FROM fabrics f
            LEFT JOIN accessories a ON 1=1  -- Tüm kombinasyonlar için
            LEFT JOIN processes p ON 1=1    -- Tüm kombinasyonlar için
            WHERE f.is_active = true
            AND (a.is_active = true OR a.is_active IS NULL)
            AND (p.is_active = true OR p.is_active IS NULL)
            """
            
            # Filtreleri uygula
            params = []
            if filters:
                if filters.get('fabric_id'):
                    query += " AND f.id = %s"
                    params.append(filters['fabric_id'])
                
                if filters.get('min_co2'):
                    query += " AND (f.avg_co2_kg + COALESCE(a.avg_co2_kg, 0) + COALESCE(p.avg_co2_kg, 0)) >= %s"
                    params.append(filters['min_co2'])
                
                if filters.get('max_co2'):
                    query += " AND (f.avg_co2_kg + COALESCE(a.avg_co2_kg, 0) + COALESCE(p.avg_co2_kg, 0)) <= %s"
                    params.append(filters['max_co2'])
            
            query += " ORDER BY total_co2 DESC LIMIT 1000"  # Performans için limit
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Sonuçları dict listesine çevir
            columns = [desc[0] for desc in cursor.description]
            data = []
            
            for row in results:
                row_dict = dict(zip(columns, row))
                # CO2 değerlerini formatla
                for key in ['fabric_co2', 'accessory_co2', 'process_co2', 'total_co2']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = round(float(row_dict[key]), 2)
                data.append(row_dict)
            
            conn.close()
            return data
            
        except Exception as e:
            self.logger.error(f"Dashboard veri alma hatası: {str(e)}")
            if 'conn' in locals():
                conn.close()
            raise
    
    def get_co2_calculations_for_export(self, user_id=None, limit=1000):
        """
        CO2 hesaplama geçmişini export için hazırla
        
        Args:
            user_id: Kullanıcı ID'si (opsiyonel)
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Export edilecek CO2 hesaplama verileri
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                id,
                product_name,
                total_co2,
                fabric_co2,
                accessory_co2,
                process_co2,
                created_at,
                user_id
            FROM co2_calculations
            WHERE 1=1
            """
            
            params = []
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Sonuçları dict listesine çevir
            columns = [desc[0] for desc in cursor.description]
            data = []
            
            for row in results:
                row_dict = dict(zip(columns, row))
                # Tarih formatını düzenle
                if row_dict.get('created_at'):
                    row_dict['created_at'] = row_dict['created_at'].strftime('%d/%m/%Y %H:%M')
                # CO2 değerlerini formatla
                for key in ['total_co2', 'fabric_co2', 'accessory_co2', 'process_co2']:
                    if row_dict.get(key) is not None:
                        row_dict[key] = round(float(row_dict[key]), 2)
                data.append(row_dict)
            
            conn.close()
            return data
            
        except Exception as e:
            self.logger.error(f"CO2 hesaplama veri alma hatası: {str(e)}")
            if 'conn' in locals():
                conn.close()
            raise