"""
DPP (Digital Product Passport) ve NFT entegrasyonu için temel yapı
Zero@Design projesi - Faz 4 hazırlık
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests

class DPPGenerator:
    """Digital Product Passport oluşturucu"""
    
    def __init__(self):
        self.dpp_schema_version = "1.0"
        self.issuer = "Zero@Design Platform"
    
    def create_dpp(self, style_card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stil kartından DPP oluştur"""
        
        # Benzersiz DPP ID oluştur
        dpp_id = str(uuid.uuid4())
        
        # Ürün hash'i oluştur (değişiklik takibi için)
        product_hash = self._generate_product_hash(style_card_data)
        
        # DPP yapısı
        dpp = {
            "dpp_id": dpp_id,
            "schema_version": self.dpp_schema_version,
            "issuer": self.issuer,
            "created_at": datetime.now().isoformat(),
            "product_hash": product_hash,
            
            # Temel ürün bilgileri
            "product_info": {
                "name": style_card_data.get('product_name', ''),
                "category": style_card_data.get('product_type', ''),
                "brand": style_card_data.get('brand', 'Zero@Design'),
                "season": style_card_data.get('season', ''),
                "collection": style_card_data.get('collection', '')
            },
            
            # Sürdürülebilirlik verileri
            "sustainability": {
                "co2_footprint": {
                    "total_kg": style_card_data.get('total_co2', 0),
                    "breakdown": style_card_data.get('co2_breakdown', {}),
                    "calculation_method": "Zero@Design LCA Model v1.0"
                },
                "sustainability_score": style_card_data.get('sustainability_score', 0),
                "certifications": style_card_data.get('certifications', []),
                "recyclability": style_card_data.get('recyclability', 'Unknown')
            },
            
            # Malzeme kompozisyonu
            "materials": {
                "fiber_composition": style_card_data.get('fiber_composition', []),
                "total_weight": style_card_data.get('weight', 0),
                "material_origins": style_card_data.get('material_origins', [])
            },
            
            # Üretim bilgileri
            "production": {
                "processes": style_card_data.get('processes', []),
                "manufacturing_location": style_card_data.get('manufacturing_location', ''),
                "production_date": style_card_data.get('production_date', ''),
                "batch_number": style_card_data.get('batch_number', '')
            },
            
            # Tedarik zinciri
            "supply_chain": {
                "suppliers": style_card_data.get('suppliers', []),
                "transportation": style_card_data.get('transportation', {}),
                "traceability_level": style_card_data.get('traceability_level', 'Basic')
            },
            
            # Yaşam döngüsü
            "lifecycle": {
                "care_instructions": style_card_data.get('care_instructions', []),
                "expected_lifespan": style_card_data.get('expected_lifespan', ''),
                "end_of_life": style_card_data.get('end_of_life', 'Unknown')
            },
            
            # Doğrulama
            "verification": {
                "verified": False,
                "verification_date": None,
                "verifier": None,
                "verification_method": "Pending"
            }
        }
        
        return dpp
    
    def _generate_product_hash(self, data: Dict[str, Any]) -> str:
        """Ürün verilerinden hash oluştur"""
        # Kritik alanları seç
        critical_data = {
            'product_name': data.get('product_name', ''),
            'fiber_composition': data.get('fiber_composition', []),
            'processes': data.get('processes', []),
            'weight': data.get('weight', 0)
        }
        
        # JSON string'e çevir ve hash oluştur
        data_string = json.dumps(critical_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def validate_dpp(self, dpp: Dict[str, Any]) -> Dict[str, Any]:
        """DPP doğrulama"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Zorunlu alanları kontrol et
        required_fields = [
            "dpp_id", "product_info", "sustainability", 
            "materials", "production"
        ]
        
        for field in required_fields:
            if field not in dpp:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Veri tutarlılığı kontrolleri
        if "sustainability" in dpp:
            co2_total = dpp["sustainability"]["co2_footprint"]["total_kg"]
            if co2_total < 0:
                validation_result["valid"] = False
                validation_result["errors"].append("CO2 footprint cannot be negative")
        
        return validation_result

class NFTIntegration:
    """NFT entegrasyonu için temel yapı"""
    
    def __init__(self, blockchain_network: str = "polygon"):
        self.blockchain_network = blockchain_network
        self.contract_address = None  # Gelecekte smart contract adresi
        
    def prepare_nft_metadata(self, dpp: Dict[str, Any]) -> Dict[str, Any]:
        """DPP'den NFT metadata'sı hazırla"""
        
        metadata = {
            "name": f"Zero@Design DPP - {dpp['product_info']['name']}",
            "description": f"Digital Product Passport for {dpp['product_info']['name']} - Sustainable Fashion Transparency",
            "image": self._generate_nft_image_url(dpp),
            "external_url": f"https://zerodesign.app/dpp/{dpp['dpp_id']}",
            
            # NFT standart özellikleri
            "attributes": [
                {
                    "trait_type": "Product Category",
                    "value": dpp['product_info']['category']
                },
                {
                    "trait_type": "CO2 Footprint (kg)",
                    "value": dpp['sustainability']['co2_footprint']['total_kg']
                },
                {
                    "trait_type": "Sustainability Score",
                    "value": dpp['sustainability']['sustainability_score']
                },
                {
                    "trait_type": "Blockchain Network",
                    "value": self.blockchain_network
                },
                {
                    "trait_type": "DPP Version",
                    "value": dpp['schema_version']
                }
            ],
            
            # Zero@Design özel alanları
            "zero_design": {
                "dpp_id": dpp['dpp_id'],
                "product_hash": dpp['product_hash'],
                "created_at": dpp['created_at'],
                "issuer": dpp['issuer']
            }
        }
        
        # Malzeme kompozisyonunu ekle
        for material in dpp['materials']['fiber_composition']:
            metadata["attributes"].append({
                "trait_type": f"Material - {material.get('fiber', 'Unknown')}",
                "value": f"{material.get('percentage', 0)}%"
            })
        
        return metadata
    
    def _generate_nft_image_url(self, dpp: Dict[str, Any]) -> str:
        """NFT için görsel URL'i oluştur"""
        # Gelecekte dinamik görsel oluşturma
        return f"https://zerodesign.app/api/nft-image/{dpp['dpp_id']}"
    
    def create_nft_contract_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Smart contract için NFT verisi hazırla"""
        
        return {
            "tokenURI": f"https://zerodesign.app/api/nft-metadata/{metadata['zero_design']['dpp_id']}",
            "recipient": "0x0000000000000000000000000000000000000000",  # Placeholder
            "dppId": metadata['zero_design']['dpp_id'],
            "productHash": metadata['zero_design']['product_hash'],
            "co2Footprint": int(metadata['attributes'][1]['value'] * 1000),  # Wei cinsinden
            "sustainabilityScore": metadata['attributes'][2]['value']
        }

class DPPStorage:
    """DPP depolama ve erişim yönetimi"""
    
    def __init__(self, storage_path: str = "data/dpp"):
        self.storage_path = storage_path
        import os
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
    
    def save_dpp(self, dpp: Dict[str, Any]) -> bool:
        """DPP'yi dosyaya kaydet"""
        try:
            file_path = f"{self.storage_path}/{dpp['dpp_id']}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dpp, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"DPP kaydetme hatası: {e}")
            return False
    
    def load_dpp(self, dpp_id: str) -> Optional[Dict[str, Any]]:
        """DPP'yi yükle"""
        try:
            file_path = f"{self.storage_path}/{dpp_id}.json"
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"DPP yükleme hatası: {e}")
            return None
    
    def list_dpps(self) -> List[str]:
        """Tüm DPP ID'lerini listele"""
        import os
        try:
            files = os.listdir(self.storage_path)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception as e:
            print(f"DPP listeleme hatası: {e}")
            return []

# Kullanım örneği ve test fonksiyonları
def create_sample_dpp():
    """Örnek DPP oluştur"""
    
    # Örnek stil kartı verisi
    sample_style_card = {
        'product_name': 'Eco T-Shirt',
        'product_type': 'T-shirt',
        'brand': 'Zero@Design',
        'season': 'SS24',
        'collection': 'Sustainable Basics',
        'total_co2': 8.5,
        'co2_breakdown': {
            'materials': 5.2,
            'production': 2.1,
            'transportation': 1.2
        },
        'sustainability_score': 85,
        'fiber_composition': [
            {'fiber': 'Organic Cotton', 'percentage': 95},
            {'fiber': 'Elastane', 'percentage': 5}
        ],
        'weight': 150,
        'processes': ['Dyeing', 'Finishing'],
        'manufacturing_location': 'Turkey',
        'certifications': ['GOTS', 'OEKO-TEX']
    }
    
    # DPP oluştur
    dpp_generator = DPPGenerator()
    dpp = dpp_generator.create_dpp(sample_style_card)
    
    # NFT metadata hazırla
    nft_integration = NFTIntegration()
    nft_metadata = nft_integration.prepare_nft_metadata(dpp)
    
    # DPP'yi kaydet
    storage = DPPStorage()
    storage.save_dpp(dpp)
    
    return dpp, nft_metadata

if __name__ == "__main__":
    # Test
    dpp, nft_metadata = create_sample_dpp()
    print("DPP oluşturuldu:", dpp['dpp_id'])
    print("NFT metadata hazırlandı")