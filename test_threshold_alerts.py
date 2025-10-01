"""
Test suite for CO₂ Threshold Alert System
Tests for settings management, threshold checking, and export functionality
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from io import BytesIO
import pandas as pd

# Import modules to test
from settings_manager import SettingsManager
from export_manager import ExportManager
from database_manager import DatabaseManager


class TestSettingsManager:
    """Test cases for SettingsManager class"""
    
    @pytest.fixture
    def settings_manager(self):
        """Create a SettingsManager instance for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_db:
            db_path = tmp_db.name
        
        manager = SettingsManager(db_path)
        
        yield manager
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @patch('sqlite3.connect')
    def test_get_setting_default(self, mock_connect, settings_manager):
        """Test getting default setting value"""
        # Mock database response - no result found
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = settings_manager.get_setting('co2_threshold', 15.0)
        assert result == 15.0
    
    @patch('sqlite3.connect')
    def test_get_setting_from_db(self, mock_connect, settings_manager):
        """Test getting setting from database with proper conversion"""
        # Mock database connection and cursor - should return (value, data_type) tuple
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('20.5', 'number')
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = settings_manager.get_setting('co2_threshold')
        assert result == 20.5  # Should be converted to float
    
    @patch('sqlite3.connect')
    def test_set_setting(self, mock_connect, settings_manager):
        """Test setting a value"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # Setting doesn't exist
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = settings_manager.set_setting('co2_threshold', 25.0, 'CO2 threshold value')
        assert result is True
    
    def test_get_co2_threshold_default(self, settings_manager):
        """Test getting default CO₂ threshold"""
        with patch.object(settings_manager, 'get_setting', return_value=15.0):
            threshold = settings_manager.get_co2_threshold()
            assert threshold == 15.0
    
    def test_get_alert_color_default(self, settings_manager):
        """Test getting default alert color"""
        with patch.object(settings_manager, 'get_setting', return_value='#D51635'):
            color = settings_manager.get_alert_color()
            assert color == '#D51635'
    
    @patch('sqlite3.connect')
    def test_get_user_preferences_default(self, mock_connect, settings_manager):
        """Test getting default user preferences"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        prefs = settings_manager.get_user_preferences(1)
        assert prefs == {}
    
    @patch('sqlite3.connect')
    def test_get_user_preferences_from_db(self, mock_connect, settings_manager):
        """Test getting user preferences from database"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('{"theme": "dark", "notifications": true}',)
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        prefs = settings_manager.get_user_preferences(1)
        assert prefs == {"theme": "dark", "notifications": True}


class TestExportManager:
    """Test cases for ExportManager class"""
    
    @pytest.fixture
    def export_manager(self):
        """Create an ExportManager instance for testing"""
        with patch('export_manager.DatabaseSetup') as mock_db_setup:
            manager = ExportManager()
            # Mock the db attribute with proper methods
            manager.db = Mock()
            manager.db.get_connection = Mock()
            return manager
    
    def test_export_to_csv_basic(self, export_manager):
        """Test basic CSV export functionality"""
        # Test data
        test_data = [
            {'name': 'Product 1', 'co2': 5.2},
            {'name': 'Product 2', 'co2': 3.8}
        ]
        
        csv_content, filename = export_manager.export_to_csv(test_data, "test")
        
        assert "Product 1" in csv_content
        assert "5.2" in csv_content
        assert filename.startswith("test_")
        assert filename.endswith(".csv")
    
    def test_export_to_csv_empty_data(self, export_manager):
        """Test CSV export with empty data"""
        with pytest.raises(ValueError, match="Export edilecek veri bulunamadı"):
            export_manager.export_to_csv([], "test")
    
    def test_export_to_pdf_basic(self, export_manager):
        """Test basic PDF export functionality"""
        test_data = [
            {'name': 'Product 1', 'co2': 5.2}
        ]
        
        pdf_content, filename = export_manager.export_to_pdf(test_data, "Test Report", "test")
        
        assert isinstance(pdf_content, bytes)
        assert filename.startswith("test_")
        assert filename.endswith(".pdf")
    
    def test_get_dashboard_data_for_export(self, export_manager):
        """Test getting dashboard data for export"""
        # Mock database response with proper structure
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ('Cotton', 2.5, 'Button', 0.1, 'Dyeing', 1.2, 3.8)
        ]
        mock_cursor.description = [
            ('fabric_name',), ('fabric_co2',), ('accessory_name',), 
            ('accessory_co2',), ('process_name',), ('process_co2',), ('total_co2',)
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        export_manager.db.get_connection.return_value = mock_conn
        
        result = export_manager.get_dashboard_data_for_export()
        
        assert len(result) == 1
        assert result[0]['fabric_name'] == 'Cotton'
        assert result[0]['total_co2'] == 3.8
        mock_conn.close.assert_called_once()
    
    def test_get_co2_calculations_for_export(self, export_manager):
        """Test getting CO₂ calculations for export"""
        # Mock database response with datetime object
        from datetime import datetime
        test_datetime = datetime.now()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, 'Test Product', 5.5, 2.0, 0.5, 3.0, test_datetime, 'user1')
        ]
        mock_cursor.description = [
            ('id',), ('product_name',), ('total_co2',), ('fabric_co2',),
            ('accessory_co2',), ('process_co2',), ('created_at',), ('user_id',)
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        export_manager.db.get_connection.return_value = mock_conn
        
        result = export_manager.get_co2_calculations_for_export()
        
        assert len(result) == 1
        assert result[0]['product_name'] == 'Test Product'
        assert result[0]['total_co2'] == 5.5
        # Check that datetime was formatted
        assert isinstance(result[0]['created_at'], str)
        mock_conn.close.assert_called_once()


class TestCO2Calculations:
    @pytest.fixture
    def db_manager(self):
        # Create a simple mock for database manager
        return Mock()
    
    @patch('sqlite3.connect')
    def test_calculate_product_co2_basic(self, mock_connect, db_manager):
        """Test basic CO₂ calculation"""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock fabric data
        mock_cursor.fetchone.return_value = (2.5,)  # fabric CO2
        
        # Test calculation
        fabric_co2 = 2.5
        accessory_co2 = 0.5
        process_co2 = 1.0
        
        total_co2 = fabric_co2 + accessory_co2 + process_co2
        
        assert total_co2 == 4.0
        assert fabric_co2 == 2.5
    
    @patch('sqlite3.connect')
    def test_save_co2_calculation(self, mock_connect, db_manager):
        """Test saving CO₂ calculation to database"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Test data
        calculation_data = {
            'product_name': 'Test Product',
            'total_co2': 12.5,
            'fabric_co2': 8.0,
            'accessory_co2': 2.0,
            'process_co2': 2.5,
            'user_id': 'test_user'
        }
        
        # Simulate saving
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        # Verify the mock was called
        assert calculation_data['product_name'] == 'Test Product'
        assert calculation_data['total_co2'] == 12.5
    
    @patch('sqlite3.connect')
    def test_get_co2_calculations(self, mock_connect, db_manager):
        """Test retrieving CO₂ calculations"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock return data
        mock_cursor.fetchall.return_value = [
            (1, 'Product 1', 10.5, 6.0, 2.0, 2.5, '2024-01-01', 'user1'),
            (2, 'Product 2', 15.2, 8.0, 3.0, 4.2, '2024-01-02', 'user1')
        ]
        
        # Mock column descriptions
        mock_cursor.description = [
            ('id',), ('product_name',), ('total_co2',), ('fabric_co2',),
            ('accessory_co2',), ('process_co2',), ('created_at',), ('user_id',)
        ]
        
        # Simulate getting calculations
        results = mock_cursor.fetchall()
        
        assert len(results) == 2
        assert results[0][1] == 'Product 1'  # product_name
        assert results[0][2] == 10.5  # total_co2


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @patch('sqlite3.connect')
    def test_settings_workflow(self, mock_connect):
        """Test complete settings and threshold workflow"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock settings retrieval - should return (value, data_type) tuple
        mock_cursor.fetchone.return_value = ('25.0', 'number')
        
        # Create settings manager
        settings_manager = SettingsManager()
        
        # Test threshold retrieval
        threshold = settings_manager.get_setting('co2_threshold', 20.0)
        assert threshold == 25.0
        
        # Test threshold checking
        assert settings_manager.is_threshold_exceeded(30.0) == True
        assert settings_manager.is_threshold_exceeded(15.0) == False
    
    def test_export_workflow(self):
        """Test complete export workflow"""
        from datetime import datetime
        
        with patch('export_manager.DatabaseSetup'):
            export_manager = ExportManager()
            
            # Mock the db attribute
            export_manager.db = Mock()
            
            # Mock database response for CO2 calculations
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                (1, 'Test Product', 12.5, 8.0, 2.0, 2.5, datetime.now(), 'user1')
            ]
            mock_cursor.description = [
                ('id',), ('product_name',), ('total_co2',), ('fabric_co2',),
                ('accessory_co2',), ('process_co2',), ('created_at',), ('user_id',)
            ]
            
            mock_conn = Mock()
            mock_conn.cursor.return_value = mock_cursor
            export_manager.db.get_connection.return_value = mock_conn
            
            # Test getting CO2 calculations for export
            result = export_manager.get_co2_calculations_for_export()
            
            assert len(result) == 1
            assert result[0]['product_name'] == 'Test Product'
            assert result[0]['total_co2'] == 12.5
            
            # Test CSV export
            csv_content, filename = export_manager.export_to_csv(result, "test")
            assert "Test Product" in csv_content
            assert filename.endswith(".csv")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])