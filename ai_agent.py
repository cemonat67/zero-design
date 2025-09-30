"""
Zero@Design AI Agent
Basit kural tabanlı öneri sistemi
"""

import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Suggestion:
    """AI önerisi veri yapısı"""
    type: str  # 'material', 'process', 'design', 'supply_chain'
    title: str
    description: str
    impact: str  # 'high', 'medium', 'low'
    co2_reduction: str  # Örn: '30-50%'
    implementation_difficulty: str  # 'easy', 'medium', 'hard'
    cost_impact: str  # 'low', 'medium', 'high'
    confidence: float  # 0.0 - 1.0

class ZeroDesignAIAgent:
    """Zero@Design AI Agent - Kural tabanlı öneri sistemi"""
    
    def __init__(self):
        self.fiber_co2_values = {
            'Pamuk': 5.9,
            'Organik Pamuk': 3.8,
            'Polyester': 9.5,
            'Geri Dönüştürülmüş Polyester': 4.2,
            'Yün': 10.8,
            'Keten': 2.1,
            'Tencel': 2.8,
            'Viskoz': 6.2,
            'Elastan': 15.6,
            'Naylon': 12.3,
            'Modal': 3.5,
            'Bambu': 3.2,
            'Kenevir': 2.0
        }
        
        self.sustainable_fibers = [
            'Organik Pamuk', 'Geri Dönüştürülmüş Polyester', 'Keten', 
            'Tencel', 'Modal', 'Bambu', 'Kenevir'
        ]
        
        self.high_impact_fibers = [
            'Polyester', 'Elastan', 'Naylon', 'Yün'
        ]
        
        self.process_co2_impact = {
            'conventional_dyeing': 1.5,
            'low_impact_dyeing': 0.8,
            'natural_dyeing': 0.3,
            'conventional_finishing': 1.2,
            'enzymatic_wash': 0.8,
            'ozone_treatment': 0.7,
            'laser_treatment': 0.6
        }
        
        # Öğrenme için basit hafıza
        self.suggestion_history = []
        self.feedback_data = []
    
    def analyze_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün analizi yapar ve önerileri döndürür"""
        
        # Temel bilgileri çıkar
        fiber_composition = product_data.get('fiberComposition', [])
        processes = product_data.get('processes', {})
        weight = product_data.get('weight', 200)
        category = product_data.get('productCategory', 'T-shirt')
        target_market = product_data.get('targetMarket', 'local')
        
        # CO₂ hesapla
        current_co2 = self._calculate_co2(fiber_composition, processes, weight)
        
        # Sürdürülebilirlik skoru hesapla
        sustainability_score = self._calculate_sustainability_score(
            fiber_composition, processes, current_co2
        )
        
        # Önerileri oluştur
        suggestions = self._generate_suggestions(
            fiber_composition, processes, current_co2, category, target_market
        )
        
        # What-if senaryoları
        scenarios = self._generate_scenarios(fiber_composition, processes, weight)
        
        return {
            'current_co2': current_co2,
            'sustainability_score': sustainability_score,
            'suggestions': suggestions,
            'scenarios': scenarios,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_co2(self, fiber_composition: List[Dict], processes: Dict, weight: float) -> float:
        """CO₂ emisyonu hesaplar"""
        total_co2 = 0
        
        # Lif bazlı CO₂
        for fiber in fiber_composition:
            fiber_type = fiber.get('type', 'Pamuk')
            percentage = fiber.get('percentage', 0)
            co2_value = self.fiber_co2_values.get(fiber_type, 5.0)
            total_co2 += (co2_value * percentage / 100)
        
        # İşlem bazlı CO₂
        dyeing = processes.get('dyeing', {})
        if dyeing.get('naturalDye'):
            total_co2 += self.process_co2_impact['natural_dyeing']
        elif dyeing.get('lowImpactDye'):
            total_co2 += self.process_co2_impact['low_impact_dyeing']
        else:
            total_co2 += self.process_co2_impact['conventional_dyeing']
        
        finishing = processes.get('finishing', {})
        finishing_co2 = self.process_co2_impact['conventional_finishing']
        
        if finishing.get('enzymaticWash'):
            finishing_co2 *= 0.8
        if finishing.get('ozoneTreatment'):
            finishing_co2 *= 0.7
        if finishing.get('laserTreatment'):
            finishing_co2 *= 0.6
        
        total_co2 += finishing_co2
        
        # Ağırlık ayarlaması
        total_co2 = total_co2 * (weight / 200)
        
        return round(total_co2, 1)
    
    def _calculate_sustainability_score(self, fiber_composition: List[Dict], 
                                      processes: Dict, co2_emission: float) -> int:
        """Sürdürülebilirlik skoru hesaplar"""
        score = 100
        
        # CO₂ cezası
        if co2_emission > 10:
            score -= 30
        elif co2_emission > 7:
            score -= 20
        elif co2_emission > 5:
            score -= 10
        
        # Lif kompozisyonu bonusu/cezası
        for fiber in fiber_composition:
            fiber_type = fiber.get('type', 'Pamuk')
            percentage = fiber.get('percentage', 0)
            
            if fiber_type in self.sustainable_fibers:
                score += (percentage / 100) * 15
            elif fiber_type in self.high_impact_fibers:
                score -= (percentage / 100) * 10
        
        # İşlem bonusları
        dyeing = processes.get('dyeing', {})
        if dyeing.get('naturalDye'):
            score += 10
        elif dyeing.get('lowImpactDye'):
            score += 5
        if dyeing.get('waterBasedDye'):
            score += 5
        
        finishing = processes.get('finishing', {})
        if finishing.get('enzymaticWash'):
            score += 5
        if finishing.get('ozoneTreatment'):
            score += 5
        if finishing.get('laserTreatment'):
            score += 5
        
        return max(0, min(100, round(score)))
    
    def _generate_suggestions(self, fiber_composition: List[Dict], processes: Dict, 
                            current_co2: float, category: str, target_market: str) -> List[Suggestion]:
        """Önerileri oluşturur"""
        suggestions = []
        
        # Yüksek CO₂ önerileri
        if current_co2 > 8:
            suggestions.append(Suggestion(
                type='material',
                title='Geri Dönüştürülmüş Lif Kullanın',
                description='Geri dönüştürülmüş polyester veya organik pamuk kullanarak CO₂ emisyonunu önemli ölçüde azaltabilirsiniz.',
                impact='high',
                co2_reduction='30-50%',
                implementation_difficulty='medium',
                cost_impact='medium',
                confidence=0.9
            ))
        
        # Lif bazlı öneriler
        for fiber in fiber_composition:
            fiber_type = fiber.get('type', 'Pamuk')
            percentage = fiber.get('percentage', 0)
            
            if fiber_type == 'Polyester' and percentage > 20:
                suggestions.append(Suggestion(
                    type='material',
                    title='Geri Dönüştürülmüş Polyester',
                    description=f'%{percentage} polyester yerine geri dönüştürülmüş polyester kullanın.',
                    impact='medium',
                    co2_reduction='40-60%',
                    implementation_difficulty='easy',
                    cost_impact='low',
                    confidence=0.8
                ))
            
            if fiber_type == 'Pamuk' and percentage > 30:
                suggestions.append(Suggestion(
                    type='material',
                    title='Organik Pamuk Alternatifi',
                    description=f'%{percentage} konvansiyonel pamuk yerine organik pamuk tercih edin.',
                    impact='medium',
                    co2_reduction='35-45%',
                    implementation_difficulty='easy',
                    cost_impact='medium',
                    confidence=0.7
                ))
            
            if fiber_type in ['Elastan', 'Naylon'] and percentage > 5:
                suggestions.append(Suggestion(
                    type='material',
                    title='Düşük Karbonlu Alternatif',
                    description=f'{fiber_type} yerine Tencel veya Modal gibi düşük karbonlu alternatifler kullanın.',
                    impact='high',
                    co2_reduction='50-70%',
                    implementation_difficulty='medium',
                    cost_impact='medium',
                    confidence=0.6
                ))
        
        # İşlem bazlı öneriler
        dyeing = processes.get('dyeing', {})
        if not dyeing.get('naturalDye') and not dyeing.get('lowImpactDye'):
            suggestions.append(Suggestion(
                type='process',
                title='Düşük Etkili Boyama',
                description='Doğal veya düşük etkili boyar madde kullanarak çevresel etkiyi azaltın.',
                impact='medium',
                co2_reduction='15-25%',
                implementation_difficulty='medium',
                cost_impact='medium',
                confidence=0.8
            ))
        
        finishing = processes.get('finishing', {})
        if not finishing.get('enzymaticWash'):
            suggestions.append(Suggestion(
                type='process',
                title='Enzimatik Yıkama',
                description='Geleneksel yıkama yerine enzimatik yıkama kullanın.',
                impact='low',
                co2_reduction='10-20%',
                implementation_difficulty='easy',
                cost_impact='low',
                confidence=0.7
            ))
        
        # Tedarik zinciri önerileri
        if target_market == 'global':
            suggestions.append(Suggestion(
                type='supply_chain',
                title='Yerel Tedarik Zinciri',
                description='Lojistik emisyonlarını azaltmak için yerel tedarikçileri tercih edin.',
                impact='medium',
                co2_reduction='20-35%',
                implementation_difficulty='hard',
                cost_impact='medium',
                confidence=0.6
            ))
        
        # Tasarım önerileri
        if category in ['Jean', 'Mont', 'Ceket']:
            suggestions.append(Suggestion(
                type='design',
                title='Modüler Tasarım',
                description='Parçaları değiştirilebilir modüler tasarım ile ürün ömrünü uzatın.',
                impact='high',
                co2_reduction='25-40%',
                implementation_difficulty='hard',
                cost_impact='high',
                confidence=0.5
            ))
        
        # En iyi 5 öneriyi döndür
        suggestions.sort(key=lambda x: (x.confidence, x.impact == 'high'), reverse=True)
        return suggestions[:5]
    
    def _generate_scenarios(self, fiber_composition: List[Dict], processes: Dict, 
                          weight: float) -> List[Dict[str, Any]]:
        """What-if senaryoları oluşturur"""
        scenarios = []
        base_co2 = self._calculate_co2(fiber_composition, processes, weight)
        
        # Senaryo 1: Tüm lifleri sürdürülebilir alternatiflere değiştir
        sustainable_composition = []
        for fiber in fiber_composition:
            fiber_type = fiber.get('type', 'Pamuk')
            percentage = fiber.get('percentage', 0)
            
            if fiber_type == 'Pamuk':
                new_type = 'Organik Pamuk'
            elif fiber_type == 'Polyester':
                new_type = 'Geri Dönüştürülmüş Polyester'
            elif fiber_type in ['Elastan', 'Naylon']:
                new_type = 'Tencel'
            else:
                new_type = fiber_type
            
            sustainable_composition.append({
                'type': new_type,
                'percentage': percentage
            })
        
        sustainable_co2 = self._calculate_co2(sustainable_composition, processes, weight)
        scenarios.append({
            'name': 'Sürdürülebilir Lifler',
            'description': 'Tüm lifleri sürdürülebilir alternatiflere değiştir',
            'co2_before': base_co2,
            'co2_after': sustainable_co2,
            'reduction_percentage': round(((base_co2 - sustainable_co2) / base_co2) * 100, 1),
            'changes': sustainable_composition
        })
        
        # Senaryo 2: Düşük etkili işlemler
        eco_processes = {
            'dyeing': {
                'naturalDye': True,
                'lowImpactDye': False,
                'waterBasedDye': True
            },
            'finishing': {
                'enzymaticWash': True,
                'ozoneTreatment': True,
                'laserTreatment': True
            }
        }
        
        eco_process_co2 = self._calculate_co2(fiber_composition, eco_processes, weight)
        scenarios.append({
            'name': 'Eco-Friendly İşlemler',
            'description': 'Doğal boyama ve düşük etkili finishing işlemleri',
            'co2_before': base_co2,
            'co2_after': eco_process_co2,
            'reduction_percentage': round(((base_co2 - eco_process_co2) / base_co2) * 100, 1),
            'changes': eco_processes
        })
        
        # Senaryo 3: Ağırlık optimizasyonu
        optimized_weight = weight * 0.8  # %20 daha hafif
        weight_optimized_co2 = self._calculate_co2(fiber_composition, processes, optimized_weight)
        scenarios.append({
            'name': 'Ağırlık Optimizasyonu',
            'description': f'Ürün ağırlığını {weight}g\'dan {optimized_weight}g\'a düşür',
            'co2_before': base_co2,
            'co2_after': weight_optimized_co2,
            'reduction_percentage': round(((base_co2 - weight_optimized_co2) / base_co2) * 100, 1),
            'changes': {'weight': optimized_weight}
        })
        
        return scenarios
    
    def optimize_collection(self, collection_data: List[Dict[str, Any]], 
                          target_reduction: float = 15.0) -> Dict[str, Any]:
        """Koleksiyon optimizasyonu yapar"""
        
        total_co2_before = 0
        optimized_products = []
        
        for product in collection_data:
            analysis = self.analyze_product(product)
            total_co2_before += analysis['current_co2']
            
            # En iyi senaryoyu seç
            best_scenario = max(analysis['scenarios'], 
                              key=lambda x: x['reduction_percentage'])
            
            optimized_products.append({
                'original': product,
                'optimized_co2': best_scenario['co2_after'],
                'reduction': best_scenario['reduction_percentage'],
                'changes': best_scenario['changes']
            })
        
        total_co2_after = sum(p['optimized_co2'] for p in optimized_products)
        actual_reduction = ((total_co2_before - total_co2_after) / total_co2_before) * 100
        
        return {
            'target_reduction': target_reduction,
            'actual_reduction': round(actual_reduction, 1),
            'total_co2_before': round(total_co2_before, 1),
            'total_co2_after': round(total_co2_after, 1),
            'products': optimized_products,
            'success': actual_reduction >= target_reduction
        }
    
    def learn_from_feedback(self, suggestion_id: str, feedback: Dict[str, Any]):
        """Geri bildirimden öğrenir (basit implementasyon)"""
        self.feedback_data.append({
            'suggestion_id': suggestion_id,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        # Basit öğrenme: pozitif geri bildirim alan önerilerin confidence'ını artır
        if feedback.get('rating', 0) >= 4:
            # Bu tür önerilerin confidence'ını artır
            pass
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Öğrenme verilerinden içgörüler çıkarır"""
        if not self.feedback_data:
            return {'message': 'Henüz yeterli veri yok'}
        
        # Basit istatistikler
        total_feedback = len(self.feedback_data)
        positive_feedback = sum(1 for f in self.feedback_data 
                              if f['feedback'].get('rating', 0) >= 4)
        
        return {
            'total_suggestions': len(self.suggestion_history),
            'total_feedback': total_feedback,
            'positive_feedback_rate': round((positive_feedback / total_feedback) * 100, 1) if total_feedback > 0 else 0,
            'most_successful_suggestion_types': self._get_successful_suggestion_types()
        }
    
    def _get_successful_suggestion_types(self) -> List[str]:
        """En başarılı öneri tiplerini döndürür"""
        type_success = {}
        
        for feedback in self.feedback_data:
            if feedback['feedback'].get('rating', 0) >= 4:
                suggestion_type = feedback.get('suggestion_type', 'unknown')
                type_success[suggestion_type] = type_success.get(suggestion_type, 0) + 1
        
        return sorted(type_success.keys(), key=lambda x: type_success[x], reverse=True)

# Global AI Agent instance
ai_agent = ZeroDesignAIAgent()