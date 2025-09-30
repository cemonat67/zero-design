"""
Blockchain entegrasyonu için ink! smart contract ile etkileşim modülü
Zero@Design projesi - DPP blockchain kaydı
"""

import json
import hashlib
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainDPPIntegration:
    """DPP'leri blockchain'e kaydetmek için entegrasyon sınıfı"""
    
    def __init__(self, contract_address: str = None, rpc_url: str = None):
        """
        Blockchain entegrasyonu başlatıcı
        
        Args:
            contract_address: ink! smart contract adresi
            rpc_url: Substrate RPC endpoint URL'i
        """
        self.contract_address = contract_address or "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
        self.rpc_url = rpc_url or "ws://127.0.0.1:9944"
        self.chain_id = "development"
        
    def register_dpp_on_blockchain(self, dpp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DPP'yi blockchain'e kaydet
        
        Args:
            dpp_data: DPP verisi
            
        Returns:
            Blockchain kayıt sonucu
        """
        try:
            # DPP verilerini blockchain formatına çevir
            blockchain_data = self._prepare_blockchain_data(dpp_data)
            
            # Simülasyon: Gerçek blockchain entegrasyonu için substrate-interface kullanılacak
            # Şimdilik mock response döndürüyoruz
            transaction_hash = self._simulate_blockchain_transaction(blockchain_data)
            
            result = {
                'success': True,
                'transaction_hash': transaction_hash,
                'block_number': self._get_current_block_number(),
                'contract_address': self.contract_address,
                'dpp_id': dpp_data.get('dpp_id'),
                'blockchain_id': self._generate_blockchain_id(dpp_data),
                'timestamp': datetime.now().isoformat(),
                'gas_used': 150000,  # Tahmini gas kullanımı
                'status': 'confirmed'
            }
            
            logger.info(f"DPP blockchain'e kaydedildi: {dpp_data.get('dpp_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Blockchain kayıt hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dpp_id': dpp_data.get('dpp_id')
            }
    
    def verify_dpp_on_blockchain(self, dpp_id: str) -> Dict[str, Any]:
        """
        DPP'nin blockchain'deki durumunu doğrula
        
        Args:
            dpp_id: DPP kimliği
            
        Returns:
            Doğrulama sonucu
        """
        try:
            # Simülasyon: Blockchain'den DPP verilerini çek
            blockchain_data = self._simulate_blockchain_query(dpp_id)
            
            if blockchain_data:
                return {
                    'success': True,
                    'verified': True,
                    'dpp_id': dpp_id,
                    'blockchain_data': blockchain_data,
                    'verification_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': True,
                    'verified': False,
                    'dpp_id': dpp_id,
                    'message': 'DPP blockchain\'de bulunamadı'
                }
                
        except Exception as e:
            logger.error(f"Blockchain doğrulama hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dpp_id': dpp_id
            }
    
    def get_dpp_from_blockchain(self, blockchain_id: str) -> Dict[str, Any]:
        """
        Blockchain'den DPP verilerini getir
        
        Args:
            blockchain_id: Blockchain'deki DPP kimliği
            
        Returns:
            DPP verileri
        """
        try:
            # Simülasyon: Blockchain'den veri çekme
            data = self._simulate_blockchain_query(blockchain_id)
            
            if data:
                return {
                    'success': True,
                    'dpp_data': data,
                    'blockchain_id': blockchain_id
                }
            else:
                return {
                    'success': False,
                    'error': 'DPP blockchain\'de bulunamadı',
                    'blockchain_id': blockchain_id
                }
                
        except Exception as e:
            logger.error(f"Blockchain veri çekme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'blockchain_id': blockchain_id
            }
    
    def _prepare_blockchain_data(self, dpp_data: Dict[str, Any]) -> Dict[str, Any]:
        """DPP verilerini blockchain formatına hazırla"""
        
        # Kritik verileri çıkar
        product_name = dpp_data.get('product_info', {}).get('name', '')
        co2_footprint = int(dpp_data.get('sustainability', {}).get('co2_footprint', {}).get('total_kg', 0))
        sustainability_score = int(dpp_data.get('sustainability', {}).get('score', 0))
        
        # Metadata hash oluştur
        metadata_hash = self._generate_metadata_hash(dpp_data)
        
        return {
            'dpp_id': dpp_data.get('dpp_id'),
            'product_name': product_name,
            'co2_footprint': co2_footprint,
            'sustainability_score': sustainability_score,
            'metadata_hash': metadata_hash,
            'creator': dpp_data.get('issuer', 'Zero@Design'),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_metadata_hash(self, dpp_data: Dict[str, Any]) -> str:
        """DPP metadata için hash oluştur"""
        # DPP verilerini JSON string'e çevir ve hash'le
        dpp_json = json.dumps(dpp_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(dpp_json.encode('utf-8')).hexdigest()
    
    def _generate_blockchain_id(self, dpp_data: Dict[str, Any]) -> str:
        """Blockchain için benzersiz ID oluştur"""
        base_string = f"{dpp_data.get('dpp_id')}_{datetime.now().timestamp()}"
        return hashlib.md5(base_string.encode()).hexdigest()
    
    def _simulate_blockchain_transaction(self, data: Dict[str, Any]) -> str:
        """Blockchain transaction simülasyonu"""
        # Gerçek implementasyonda substrate-interface kullanılacak
        transaction_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(transaction_data.encode()).hexdigest()
    
    def _simulate_blockchain_query(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Blockchain query simülasyonu"""
        # Gerçek implementasyonda blockchain'den veri çekilecek
        # Şimdilik mock data döndürüyoruz
        return {
            'dpp_id': query_id,
            'product_name': 'Sustainable T-Shirt',
            'co2_footprint': 5,
            'sustainability_score': 85,
            'verified': True,
            'block_number': self._get_current_block_number(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_current_block_number(self) -> int:
        """Mevcut block numarasını getir (simülasyon)"""
        # Gerçek implementasyonda blockchain'den alınacak
        return 12345
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Blockchain istatistiklerini getir"""
        return {
            'contract_address': self.contract_address,
            'chain_id': self.chain_id,
            'rpc_url': self.rpc_url,
            'current_block': self._get_current_block_number(),
            'total_dpps': 0,  # Gerçek implementasyonda contract'tan alınacak
            'verified_dpps': 0,
            'last_update': datetime.now().isoformat()
        }

class DPPBlockchainStorage:
    """DPP blockchain kayıtları için yerel storage"""
    
    def __init__(self, storage_path: str = "data/blockchain"):
        self.storage_path = storage_path
        import os
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
    
    def save_blockchain_record(self, dpp_id: str, blockchain_result: Dict[str, Any]) -> bool:
        """Blockchain kayıt sonucunu yerel olarak sakla"""
        try:
            import os
            file_path = os.path.join(self.storage_path, f"{dpp_id}_blockchain.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(blockchain_result, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Blockchain kayıt saklama hatası: {str(e)}")
            return False
    
    def load_blockchain_record(self, dpp_id: str) -> Optional[Dict[str, Any]]:
        """Blockchain kaydını yerel olarak yükle"""
        try:
            import os
            file_path = os.path.join(self.storage_path, f"{dpp_id}_blockchain.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Blockchain kayıt yükleme hatası: {str(e)}")
            return None

# Test fonksiyonu
def test_blockchain_integration():
    """Blockchain entegrasyonunu test et"""
    
    # Test DPP verisi
    test_dpp = {
        'dpp_id': 'test-dpp-123',
        'product_info': {
            'name': 'Eco T-Shirt',
            'category': 'Apparel'
        },
        'sustainability': {
            'co2_footprint': {'total_kg': 5},
            'score': 85
        },
        'issuer': 'Zero@Design'
    }
    
    # Blockchain entegrasyonu test et
    blockchain = BlockchainDPPIntegration()
    
    # DPP'yi blockchain'e kaydet
    result = blockchain.register_dpp_on_blockchain(test_dpp)
    print("Blockchain kayıt sonucu:", json.dumps(result, indent=2))
    
    # DPP'yi doğrula
    verification = blockchain.verify_dpp_on_blockchain(test_dpp['dpp_id'])
    print("Blockchain doğrulama sonucu:", json.dumps(verification, indent=2))
    
    # İstatistikleri getir
    stats = blockchain.get_blockchain_stats()
    print("Blockchain istatistikleri:", json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_blockchain_integration()