"""
Zero@Design - Eco-Design @ Source Platform
Ana uygulama dosyası
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import json
import os
from datetime import datetime
import pandas as pd
from ai_agent import ai_agent
from dpp_nft import DPPGenerator, NFTIntegration, DPPStorage
from blockchain_integration import BlockchainDPPIntegration, DPPBlockchainStorage
from database_manager import db_manager
from auth_manager import AuthManager
from security_middleware import SecurityMiddleware, require_auth, require_csrf
from co2_calculator import co2_calculator
from settings_manager import SettingsManager
from export_manager import ExportManager

app = Flask(__name__)

# Konfigürasyon
app.config['SECRET_KEY'] = 'zero-design-secret-key-2024-secure'
app.config['DEBUG'] = True

# Auth Manager'ı başlat
auth_manager = AuthManager()

# Settings Manager'ı başlat
settings_manager = SettingsManager()

# Security Middleware'i başlat
security = SecurityMiddleware(app)

# Export Manager'ı başlat
export_manager = ExportManager()

# Veri dosyaları için klasör
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    """Ana sayfa - Kullanıcı durumuna göre yönlendirme"""
    if 'user_id' in session:
        # Kullanıcı giriş yapmışsa dashboard'a yönlendir
        return redirect(url_for('dashboard'))
    else:
        # Kullanıcı giriş yapmamışsa giriş sayfasına yönlendir
        return redirect(url_for('signin'))

@app.route('/signup')
def signup():
    """Kayıt sayfası"""
    return render_template('signup.html')

@app.route('/signin')
def signin():
    """Giriş sayfası"""
    return render_template('signin.html')

@app.route('/dashboard')
@require_auth
def dashboard():
    """Dashboard - Giriş yapmış kullanıcılar için"""
    user_name = session.get('user_name', 'Kullanıcı')
    return render_template('dashboard.html', user_name=user_name)

@app.route('/logout')
def logout():
    """Çıkış yap"""
    security.destroy_session()
    return redirect(url_for('index'))

@app.route('/forgot-password')
def forgot_password():
    """Şifre sıfırlama sayfası"""
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password():
    """Şifre sıfırlama formu sayfası"""
    return render_template('reset_password.html')

@app.route('/benchmark')
def benchmark():
    """Benchmark tablosu sayfası"""
    return render_template('benchmark.html')

@app.route('/style-card')
def style_card():
    """Stil kartı sayfası"""
    return render_template('style_card.html')

@app.route('/collection')
def collection():
    """Koleksiyon dashboard sayfası"""
    return render_template('collection.html')

@app.route('/dpp')
def dpp():
    """DPP sayfası"""
    return render_template('dpp.html')

@app.route('/analytics')
def analytics():
    """Analytics sayfası"""
    return render_template('analytics.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/database')
def database():
    return render_template('database.html')

@app.route('/export')
def export():
    return render_template('export.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/optimize')
def optimize():
    return render_template('optimize.html')

@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

@app.route('/design')
def design():
    """Tasarım sayfası"""
    return render_template('design.html')

@app.route('/blockchain-status')
def blockchain_status():
    """Blockchain durumu sayfası"""
    return render_template('blockchain_status.html')

@app.route('/api/benchmark-data')
def get_benchmark_data():
    """Benchmark verilerini döndürür"""
    benchmark_data = {
        "categories": {
            "Women": {
                "Tops": ["Tişört", "Bluz", "Gömlek", "Sweatshirt", "Kazak", "Hırka", "Polo yaka tişört", "Atlet / Tops", "Yelek"],
                "Bottoms": ["Pantolon", "Jean", "Etek", "Şort", "Tayt"],
                "Outerwear": ["Ceket", "Blazer ceket", "Trençkot", "Parka", "Mont / Kaban", "Palto"],
                "Dresses": ["Günlük elbise", "Tulum", "Abiye elbise"],
                "Other": ["Pijama takımı", "Bikini & Mayo"]
            },
            "Men": {
                "Tops": ["Tişört", "Polo yaka tişört", "Gömlek", "Sweatshirt", "Kazak", "Hırka", "Yelek"],
                "Bottoms": ["Pantolon", "Jean", "Şort"],
                "Outerwear": ["Ceket", "Blazer ceket", "Trençkot", "Parka", "Mont / Kaban", "Palto"],
                "Other": ["Pijama takımı"]
            }
        },
        "products": [
            {
                "id": 1,
                "name": "Temel Tişört",
                "gender": "Women",
                "category": "Tops",
                "product_type": "Tişört",
                "co2_emission": 4.2,
                "fiber_composition": "100% Pamuk",
                "weight": 180
            },
            {
                "id": 2,
                "name": "Organik Tişört", 
                "gender": "Women",
                "category": "Tops",
                "product_type": "Tişört",
                "co2_emission": 2.8,
                "fiber_composition": "100% Organik Pamuk",
                "weight": 180
            },
            {
                "id": 3,
                "name": "Klasik Jean",
                "gender": "Women",
                "category": "Bottoms",
                "product_type": "Jean",
                "co2_emission": 12.5,
                "fiber_composition": "98% Pamuk, 2% Elastan",
                "weight": 450
            },
            {
                "id": 4,
                "name": "Eco Jean",
                "gender": "Women",
                "category": "Bottoms", 
                "product_type": "Jean",
                "co2_emission": 8.3,
                "fiber_composition": "70% Organik Pamuk, 28% Geri Dönüştürülmüş Polyester, 2% Elastan",
                "weight": 420
            },
            {
                "id": 5,
                "name": "Şifon Bluz",
                "gender": "Women",
                "category": "Tops",
                "product_type": "Bluz",
                "co2_emission": 6.8,
                "fiber_composition": "100% Polyester",
                "weight": 150
            },
            {
                "id": 6,
                "name": "Tencel Günlük Elbise",
                "gender": "Women",
                "category": "Dresses",
                "product_type": "Günlük elbise",
                "co2_emission": 5.2,
                "fiber_composition": "100% Tencel",
                "weight": 280
            },
            {
                "id": 7,
                "name": "Erkek Polo Tişört",
                "gender": "Men",
                "category": "Tops",
                "product_type": "Polo yaka tişört",
                "co2_emission": 4.5,
                "fiber_composition": "100% Pamuk",
                "weight": 200
            },
            {
                "id": 8,
                "name": "Erkek Klasik Gömlek",
                "gender": "Men",
                "category": "Tops",
                "product_type": "Gömlek",
                "co2_emission": 5.8,
                "fiber_composition": "65% Pamuk, 35% Polyester",
                "weight": 220
            },
            {
                "id": 9,
                "name": "Erkek Chino Pantolon",
                "gender": "Men",
                "category": "Bottoms",
                "product_type": "Pantolon",
                "co2_emission": 7.2,
                "fiber_composition": "98% Pamuk, 2% Elastan",
                "weight": 380
            },
            {
                "id": 10,
                "name": "Kadın Blazer Ceket",
                "gender": "Women",
                "category": "Outerwear",
                "product_type": "Blazer ceket",
                "co2_emission": 15.4,
                "fiber_composition": "70% Polyester, 28% Viskon, 2% Elastan",
                "weight": 520
            },
            {
                "id": 11,
                "name": "Kadın Mini Etek",
                "gender": "Women",
                "category": "Bottoms",
                "product_type": "Etek",
                "co2_emission": 3.8,
                "fiber_composition": "95% Pamuk, 5% Elastan",
                "weight": 160
            },
            {
                "id": 12,
                "name": "Erkek Sweatshirt",
                "gender": "Men",
                "category": "Tops",
                "product_type": "Sweatshirt",
                "co2_emission": 8.9,
                "fiber_composition": "80% Pamuk, 20% Polyester",
                "weight": 450
            }
        ]
    }
    return jsonify(benchmark_data)

@app.route('/api/save-style-card', methods=['POST'])
def save_style_card():
    """Stil kartını kaydet"""
    data = request.get_json()
    
    # Stil kartı verilerini dosyaya kaydet
    style_card_file = os.path.join(DATA_DIR, 'style_cards.json')
    
    # Mevcut verileri yükle
    if os.path.exists(style_card_file):
        with open(style_card_file, 'r', encoding='utf-8') as f:
            style_cards = json.load(f)
    else:
        style_cards = []
    
    # Yeni stil kartını ekle
    data['created_at'] = datetime.now().isoformat()
    data['id'] = len(style_cards) + 1
    style_cards.append(data)
    
    # Dosyaya kaydet
    with open(style_card_file, 'w', encoding='utf-8') as f:
        json.dump(style_cards, f, ensure_ascii=False, indent=2)
    
    return jsonify({"status": "success", "id": data['id']})

@app.route('/api/style-cards')
def get_style_cards():
    """Kaydedilmiş stil kartlarını getir"""
    style_card_file = os.path.join(DATA_DIR, 'style_cards.json')
    
    if os.path.exists(style_card_file):
        with open(style_card_file, 'r', encoding='utf-8') as f:
            style_cards = json.load(f)
    else:
        style_cards = []
    
    return jsonify({"style_cards": style_cards})

@app.route('/api/ai-suggestions', methods=['POST'])
def get_ai_suggestions():
    """AI önerilerini döndürür"""
    try:
        data = request.get_json()
        
        # AI Agent ile analiz yap
        analysis = ai_agent.analyze_product(data)
        
        # Önerileri formatla
        suggestions = []
        for suggestion in analysis['suggestions']:
            suggestions.append({
                'type': suggestion.type,
                'title': suggestion.title,
                'description': suggestion.description,
                'impact': suggestion.impact,
                'co2_reduction': suggestion.co2_reduction,
                'implementation_difficulty': suggestion.implementation_difficulty,
                'cost_impact': suggestion.cost_impact,
                'confidence': suggestion.confidence
            })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'current_co2': analysis['current_co2'],
            'sustainability_score': analysis['sustainability_score'],
            'scenarios': analysis['scenarios']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/optimize-collection', methods=['POST'])
def optimize_collection():
    """Koleksiyon optimizasyonu yapar"""
    try:
        data = request.get_json()
        collection_data = data.get('collection', [])
        target_reduction = data.get('target_reduction', 15.0)
        
        # AI Agent ile optimizasyon yap
        optimization = ai_agent.optimize_collection(collection_data, target_reduction)
        
        return jsonify({
            'success': True,
            'optimization': optimization
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai-feedback', methods=['POST'])
def submit_ai_feedback():
    """AI önerilerine geri bildirim gönderir"""
    try:
        data = request.get_json()
        suggestion_id = data.get('suggestion_id')
        feedback = data.get('feedback')
        
        # AI Agent'a geri bildirim gönder
        ai_agent.learn_from_feedback(suggestion_id, feedback)
        
        return jsonify({
            'success': True,
            'message': 'Geri bildirim kaydedildi'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-dpp', methods=['POST'])
def create_dpp():
    """Stil kartından DPP oluştur ve blockchain'e kaydet"""
    try:
        data = request.get_json()
        
        # DPP oluştur
        dpp = dpp_generator.create_dpp(data)
        
        # DPP'yi doğrula
        validation = dpp_generator.validate_dpp(dpp)
        
        if validation['valid']:
            # DPP'yi yerel olarak kaydet
            if dpp_storage.save_dpp(dpp):
                # NFT metadata hazırla
                nft_metadata = nft_integration.prepare_nft_metadata(dpp)
                
                # Blockchain'e kaydet
                blockchain_result = blockchain_integration.register_dpp_on_blockchain(dpp)
                
                # Blockchain kaydını yerel olarak sakla
                if blockchain_result['success']:
                    blockchain_storage.save_blockchain_record(dpp['dpp_id'], blockchain_result)
                
                return jsonify({
                    'success': True,
                    'dpp_id': dpp['dpp_id'],
                    'dpp': dpp,
                    'nft_metadata': nft_metadata,
                    'validation': validation,
                    'blockchain': blockchain_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'DPP kaydedilemedi'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'DPP doğrulama başarısız',
                'validation': validation
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dpp/<dpp_id>')
def get_dpp(dpp_id):
    """DPP'yi getir (yerel ve blockchain verisi ile)"""
    try:
        # Yerel DPP'yi yükle
        dpp = dpp_storage.load_dpp(dpp_id)
        
        if dpp:
            # Blockchain kaydını yükle
            blockchain_record = blockchain_storage.load_blockchain_record(dpp_id)
            
            # Blockchain'den doğrulama yap
            blockchain_verification = blockchain_integration.verify_dpp_on_blockchain(dpp_id)
            
            return jsonify({
                'success': True,
                'dpp': dpp,
                'blockchain_record': blockchain_record,
                'blockchain_verification': blockchain_verification
            })
        else:
            return jsonify({
                'success': False,
                'error': 'DPP bulunamadı'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dpp-list')
def list_dpps():
    """Tüm DPP'leri listele"""
    try:
        dpp_ids = dpp_storage.list_dpps()
        
        # Her DPP için temel bilgileri getir
        dpp_list = []
        for dpp_id in dpp_ids:
            dpp = dpp_storage.load_dpp(dpp_id)
            if dpp:
                dpp_list.append({
                    'dpp_id': dpp_id,
                    'product_name': dpp['product_info']['name'],
                    'category': dpp['product_info']['category'],
                    'co2_footprint': dpp['sustainability']['co2_footprint']['total_kg'],
                    'sustainability_score': dpp['sustainability']['sustainability_score'],
                    'created_at': dpp['created_at']
                })
        
        return jsonify({
            'success': True,
            'dpps': dpp_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/nft-metadata/<dpp_id>')
def get_nft_metadata(dpp_id):
    """DPP için NFT metadata getir"""
    try:
        dpp = dpp_storage.load_dpp(dpp_id)
        
        if dpp:
            nft_metadata = nft_integration.prepare_nft_metadata(dpp)
            return jsonify({
                'success': True,
                'metadata': nft_metadata
            })
        else:
            return jsonify({
                'success': False,
                'error': 'DPP bulunamadı'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain-stats')
def get_blockchain_stats():
    """Blockchain istatistiklerini getir"""
    try:
        stats = blockchain_integration.get_blockchain_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== VERİTABANI API ENDPOINT'LERİ =====

@app.route('/api/database/stats')
def get_database_stats():
    """Veritabanı istatistiklerini getir"""
    try:
        stats = db_manager.get_database_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/operations/finished-products')
def get_finished_product_operations():
    """Bitmiş ürün işlemlerini getir"""
    try:
        category = request.args.get('category')
        operations = db_manager.get_finished_product_operations(category)
        return jsonify({
            'success': True,
            'operations': operations,
            'count': len(operations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/operations/garment-processes')
def get_garment_processes():
    """Konfeksiyon süreçlerini getir"""
    try:
        category = request.args.get('category')
        processes = db_manager.get_garment_processes(category)
        return jsonify({
            'success': True,
            'processes': processes,
            'count': len(processes)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/co2-data/master')
def get_master_co2_data():
    """Master CO2 verilerini getir"""
    try:
        category = request.args.get('category')
        operation = request.args.get('operation')
        co2_data = db_manager.get_master_co2_data(category, operation)
        return jsonify({
            'success': True,
            'co2_data': co2_data,
            'count': len(co2_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories')
def get_categories():
    """Ürün kategorilerini getir"""
    try:
        categories = db_manager.get_product_categories()
        categories_by_table = db_manager.get_categories_by_table()
        return jsonify({
            'success': True,
            'categories': categories,
            'categories_by_table': categories_by_table
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search_operations():
    """İşlem arama"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Arama terimi gerekli'
            }), 400
        
        results = db_manager.search_operations(search_term)
        total_results = sum(len(v) for v in results.values())
        
        return jsonify({
            'success': True,
            'results': results,
            'total_results': total_results,
            'search_term': search_term
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate-co2', methods=['POST'])
@require_auth
@require_csrf
def calculate_total_co2():
    """
    Yeni CO₂ hesaplama endpoint'i
    Input: fabric_id, accessory_ids[], process_ids[], quantities
    Output: total_co2 + detaylı breakdown JSON
    """
    try:
        data = request.get_json()
        
        # Input parametrelerini al
        fabric_id = data.get('fabric_id')
        fabric_quantity_kg = float(data.get('fabric_quantity_kg', 1.0))
        accessory_ids = data.get('accessory_ids', [])
        accessory_quantities = data.get('accessory_quantities', [])
        process_ids = data.get('process_ids', [])
        
        # Validation
        if not fabric_id and not accessory_ids and not process_ids:
            return jsonify({
                'success': False,
                'error': 'En az bir kumaş, aksesuar veya işlem seçilmeli'
            }), 400
        
        # CO₂ hesaplama
        result = co2_calculator.calculate_total_co2(
            fabric_id=fabric_id,
            fabric_quantity_kg=fabric_quantity_kg,
            accessory_ids=accessory_ids,
            accessory_quantities=accessory_quantities,
            process_ids=process_ids
        )
        
        # Hata kontrolü
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Geçersiz parametre: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'CO₂ hesaplama hatası: {str(e)}'
        }), 500

@app.route('/api/co2-items')
@require_auth
def get_co2_items():
    """
    Mevcut kumaş, aksesuar ve işlemleri listele
    """
    try:
        items = co2_calculator.get_available_items()
        
        if 'error' in items:
            return jsonify({
                'success': False,
                'error': items['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Öğeleri getirme hatası: {str(e)}'
        }), 500

@app.route('/api/co2-calculator', methods=['POST'])
def calculate_co2():
    """CO2 hesaplama"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '')
        selected_operations = data.get('operations', [])
        
        if not product_name:
            return jsonify({
                'success': False,
                'error': 'Ürün adı gerekli'
            }), 400
        
        if not selected_operations:
            return jsonify({
                'success': False,
                'error': 'En az bir işlem seçilmeli'
            }), 400
        
        calculation_result = db_manager.calculate_product_co2(product_name, selected_operations)
        
        return jsonify({
            'success': True,
            'calculation': calculation_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/co2-calculations')
def get_co2_calculations():
    """CO2 hesaplama geçmişini getir"""
    try:
        limit = int(request.args.get('limit', 50))
        calculations = db_manager.get_co2_calculations(limit)
        return jsonify({
            'success': True,
            'calculations': calculations,
            'count': len(calculations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/operations/by-product-group')
def get_operations_by_product_group():
    """Ürün grubuna göre işlemleri getir"""
    try:
        product_group = request.args.get('product_group', '')
        if not product_group:
            return jsonify({
                'success': False,
                'error': 'Ürün grubu gerekli'
            }), 400
        
        operations = db_manager.get_operations_by_product_group(product_group)
        return jsonify({
            'success': True,
            'operations': operations,
            'count': len(operations),
            'product_group': product_group
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Yeni CSV verilerini kullanacak API endpoint'leri

@app.route('/api/master-konfeksiyon')
def get_master_konfeksiyon():
    """Master konfeksiyon verilerini getirir"""
    try:
        category = request.args.get('category')
        name = request.args.get('name')
        
        data = db_manager.get_master_konfeksiyon_data(category, name)
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fabric-co2')
def get_fabric_co2():
    """Kumaş CO2 verilerini getirir"""
    try:
        gender = request.args.get('gender')
        category = request.args.get('category')
        product = request.args.get('product')
        fabric_type = request.args.get('fabric_type')
        
        data = db_manager.get_product_fabric_co2_data(gender, category, product, fabric_type)
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fabric-types')
def get_fabric_types():
    """Kumaş tiplerini getirir"""
    try:
        fabric_types = db_manager.get_fabric_types()
        
        return jsonify({
            'success': True,
            'fabric_types': fabric_types
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compositions')
def get_compositions():
    """Kompozisyonları getirir"""
    try:
        compositions = db_manager.get_compositions()
        
        return jsonify({
            'success': True,
            'compositions': compositions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fabric-search')
def search_fabric():
    """Kompozisyona göre kumaş arar"""
    try:
        composition = request.args.get('composition', '')
        
        if not composition:
            return jsonify({'error': 'Kompozisyon parametresi gerekli'}), 400
        
        results = db_manager.search_fabric_by_composition(composition)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data-entry')
def data_entry():
    """Veri giriş sayfası"""
    try:
        # Database'den kategorileri al
        categories = db_manager.get_product_categories()
        
        # Kumaş tiplerini al
        fabric_types = db_manager.get_fabric_types()
        
        # Kompozisyonları al
        compositions = db_manager.get_compositions()
        
        return render_template('data_entry.html', 
                             categories=categories,
                             fabric_types=fabric_types,
                             compositions=compositions)
    except Exception as e:
        return render_template('data_entry.html', 
                             categories=[],
                             fabric_types=[],
                             compositions=[])

@app.route('/api/save-style-data', methods=['POST'])
def save_style_data():
    """Stil verilerini kaydet"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Veri bulunamadı'}), 400
        
        # Stil verilerini database'e kaydet
        style_id = db_manager.save_style_data(data)
        
        return jsonify({
            'success': True,
            'message': 'Stil verileri başarıyla kaydedildi',
            'style_id': style_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-style-data/<style_code>')
def get_style_data(style_code):
    """Stil verilerini getir"""
    try:
        style_data = db_manager.get_style_data(style_code)
        
        if not style_data:
            return jsonify({'error': 'Stil bulunamadı'}), 404
        
        return jsonify({
            'success': True,
            'data': style_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-all-styles')
def get_all_styles():
    """Tüm stilleri listele"""
    try:
        styles = db_manager.get_all_styles()
        
        return jsonify({
            'success': True,
            'styles': styles,
            'count': len(styles)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/co2-range/<category>')
def get_co2_range(category):
    """Kategoriye göre CO2 aralığını getirir"""
    try:
        co2_range = db_manager.get_co2_range_by_category(category)
        
        return jsonify({
            'success': True,
            'category': category,
            'co2_range': co2_range
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DPP ve NFT nesnelerini başlat
# Global nesneler
dpp_generator = DPPGenerator()
nft_integration = NFTIntegration()
dpp_storage = DPPStorage()
blockchain_integration = BlockchainDPPIntegration()
blockchain_storage = DPPBlockchainStorage()

# Authentication API Routes
@app.route('/health')
def health_check():
    """Docker health check endpoint"""
    try:
        # Basit bir sağlık kontrolü
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Zero@Design'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/csrf-token')
def get_csrf_token():
    """CSRF token'ı döndür"""
    token = security.generate_csrf_token()
    return jsonify({'csrf_token': token})

@app.route('/api/signup', methods=['POST'])
@require_csrf
def api_signup():
    """Kullanıcı kayıt API'si"""
    try:
        data = request.get_json()
        
        # Güvenlik kontrolü - input sanitization
        first_name = security.sanitize_input(data.get('firstName', ''))
        last_name = security.sanitize_input(data.get('lastName', ''))
        email = security.sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        
        # Gerekli alanları kontrol et
        if not all([first_name, last_name, email, password]):
            return jsonify({'error': 'Tüm alanlar doldurulmalıdır'}), 400
        
        # E-posta format kontrolü
        if not security.validate_email_format(email):
            return jsonify({'error': 'Geçersiz e-posta formatı'}), 400
        
        # Şifre güç kontrolü
        is_strong, message = security.validate_password_strength(password)
        if not is_strong:
            return jsonify({'error': message}), 400
        
        # Kullanıcıyı kaydet (email'i username olarak kullan)
        result = auth_manager.register_user(
            username=email,  # Email'i username olarak kullan
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if result['success']:
            # Rate limiting temizle
            client_ip = security.get_client_ip()
            security.clear_failed_attempts(client_ip)
            
            return jsonify({
                'success': True,
                'message': 'Kayıt başarılı',
                'user_id': result['user_id']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Kayıt sırasında hata: {str(e)}'}), 500

@app.route('/api/signin', methods=['POST'])
@require_csrf
def api_signin():
    """Kullanıcı giriş API'si"""
    try:
        data = request.get_json()
        
        # Güvenlik kontrolü - input sanitization
        email = security.sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        
        # Rate limiting kontrolü
        client_ip = security.get_client_ip()
        if security.is_rate_limited(client_ip):
            return jsonify({'error': 'Çok fazla başarısız deneme. 15 dakika sonra tekrar deneyin.'}), 429
        
        # Gerekli alanları kontrol et
        if not email or not password:
            return jsonify({'error': 'E-posta ve şifre gereklidir'}), 400
        
        # Kullanıcı girişini kontrol et
        result = auth_manager.login_user(email, password)
        
        if result['success']:
            # Güvenli session oluştur
            security.create_session(
                result['user']['id'],
                result['user']['email'],
                f"{result['user']['first_name']} {result['user']['last_name']}"
            )
            
            # Başarılı giriş - rate limiting temizle
            security.clear_failed_attempts(client_ip)
            
            return jsonify({
                'success': True,
                'message': 'Giriş başarılı',
                'redirect': '/dashboard',
                'user': {
                    'id': result['user']['id'],
                    'email': result['user']['email'],
                    'first_name': result['user']['first_name'],
                    'last_name': result['user']['last_name']
                }
            })
        else:
            # Başarısız giriş - rate limiting kaydet
            security.record_failed_attempt(client_ip)
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        return jsonify({'error': f'Giriş sırasında hata: {str(e)}'}), 500

@app.route('/api/user/profile')
@require_auth
def get_user_profile():
    """Kullanıcı profil bilgilerini getir"""
    try:
        user_id = security.get_current_user_id()
        user = auth_manager.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
        else:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Profil bilgileri alınırken hata oluştu'}), 500

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Şifre sıfırlama bağlantısı gönder"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'E-posta adresi gereklidir'}), 400
        
        # E-posta formatını kontrol et
        if not auth_manager.validate_email(data['email']):
            return jsonify({'error': 'Geçersiz e-posta formatı'}), 400
        
        # Şifre sıfırlama token'ı oluştur
        result = auth_manager.create_password_reset_token(data['email'])
        
        if result['success']:
            # Gerçek uygulamada burada e-posta gönderilir
            # Şimdilik sadece başarılı yanıt döndürüyoruz
            return jsonify({
                'success': True,
                'message': 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi',
                'reset_token': result['token']  # Demo için - gerçek uygulamada bu gönderilmez
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Şifre sıfırlama sırasında hata: {str(e)}'}), 500

@app.route('/api/check-reset-token', methods=['POST'])
def api_check_reset_token():
    """Şifre sıfırlama token'ının geçerliliğini kontrol et"""
    try:
        data = request.get_json()
        
        if not data.get('token'):
            return jsonify({'error': 'Token gereklidir'}), 400
        
        # Token'ın geçerliliğini kontrol et
        is_valid = auth_manager.validate_reset_token(data['token'])
        
        if is_valid:
            return jsonify({'success': True, 'valid': True})
        else:
            return jsonify({'error': 'Token geçersiz veya süresi dolmuş'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Token kontrolü sırasında hata: {str(e)}'}), 500

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Şifre sıfırlama API'si"""
    try:
        data = request.get_json()
        
        token = data.get('token', '')
        new_password = data.get('newPassword', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token ve yeni şifre gereklidir'}), 400
        
        # Şifre gücünü kontrol et
        if not auth_manager.validate_password(new_password):
            return jsonify({'error': 'Şifre en az 6 karakter olmalı ve güçlü olmalıdır'}), 400
        
        # Şifreyi sıfırla
        result = auth_manager.reset_password(token, new_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Şifre başarıyla sıfırlandı. Giriş yapabilirsiniz.',
                'redirect': '/signin'
            })
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Şifre sıfırlama sırasında hata oluştu'}), 500

@app.route('/profile')
@require_auth
def profile():
    """Kullanıcı profil sayfası"""
    return render_template('profile.html')

@app.route('/api/user/update-profile', methods=['POST'])
@require_auth
@require_csrf
def update_user_profile():
    """Kullanıcı profil bilgilerini güncelle"""
    try:
        data = request.get_json()
        user_id = security.get_current_user_id()
        
        # Güvenlik kontrolü - input sanitization
        first_name = security.sanitize_input(data.get('firstName', ''))
        last_name = security.sanitize_input(data.get('lastName', ''))
        email = security.sanitize_input(data.get('email', ''))
        
        # Validasyon
        if not all([first_name, last_name, email]):
            return jsonify({'error': 'Tüm alanlar doldurulmalıdır'}), 400
        
        # E-posta format kontrolü
        if not security.validate_email_format(email):
            return jsonify({'error': 'Geçersiz e-posta formatı'}), 400
        
        # Profil güncelleme
        result = auth_manager.update_user_profile(user_id, first_name, last_name, email)
        
        if result['success']:
            # Session'daki kullanıcı adını güncelle
            session['user_name'] = f"{first_name} {last_name}"
            session['user_email'] = email
            
            return jsonify({
                'success': True,
                'message': 'Profil başarıyla güncellendi'
            })
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Profil güncelleme sırasında hata oluştu'}), 500

@app.route('/api/user/change-password', methods=['POST'])
@require_auth
@require_csrf
def change_user_password():
    """Kullanıcı şifresini değiştir"""
    try:
        data = request.get_json()
        user_id = security.get_current_user_id()
        
        current_password = data.get('currentPassword', '')
        new_password = data.get('newPassword', '')
        
        # Validasyon
        if not current_password or not new_password:
            return jsonify({'error': 'Mevcut şifre ve yeni şifre gereklidir'}), 400
        
        # Şifre gücü kontrolü
        is_strong, message = security.validate_password_strength(new_password)
        if not is_strong:
            return jsonify({'error': message}), 400
        
        # Şifre değiştirme
        result = auth_manager.change_password(user_id, current_password, new_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Şifre başarıyla değiştirildi'
            })
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Şifre değiştirme sırasında hata oluştu'}), 500

# =====================================================
# SETTINGS API ENDPOINTS
# =====================================================

@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """Sistem ayarlarını getir"""
    try:
        user_id = security.get_current_user_id()
        
        # Admin kontrolü (basit kontrol - geliştirilmeli)
        user_info = auth_manager.get_user_by_id(user_id)
        is_admin = user_info and user_info.get('username') == 'admin'  # Basit admin kontrolü
        
        if is_admin:
            # Admin tüm ayarları görebilir
            settings = settings_manager.get_all_settings(public_only=False)
        else:
            # Normal kullanıcı sadece genel ayarları görebilir
            settings = settings_manager.get_all_settings(public_only=True)
        
        return jsonify({
            'success': True,
            'data': settings,
            'is_admin': is_admin
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ayarları getirme hatası: {str(e)}'
        }), 500

@app.route('/api/settings', methods=['POST'])
@require_auth
@require_csrf
def update_settings():
    """Sistem ayarlarını güncelle (sadece admin)"""
    try:
        user_id = security.get_current_user_id()
        
        # Admin kontrolü
        user_info = auth_manager.get_user_by_id(user_id)
        is_admin = user_info and user_info.get('username') == 'admin'
        
        if not is_admin:
            return jsonify({
                'success': False,
                'error': 'Bu işlem için admin yetkisi gereklidir'
            }), 403
        
        data = request.get_json()
        settings_data = data.get('settings', {})
        
        if not settings_data:
            return jsonify({
                'success': False,
                'error': 'Ayar verisi bulunamadı'
            }), 400
        
        # Her ayarı güncelle
        updated_count = 0
        errors = []
        
        for key, value in settings_data.items():
            success = settings_manager.set_setting(key, value)
            if success:
                updated_count += 1
            else:
                errors.append(f"'{key}' ayarı güncellenemedi")
        
        if errors:
            return jsonify({
                'success': False,
                'error': f'Bazı ayarlar güncellenemedi: {", ".join(errors)}',
                'updated_count': updated_count
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} ayar başarıyla güncellendi',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ayarları güncelleme hatası: {str(e)}'
        }), 500

@app.route('/api/user/preferences', methods=['GET'])
@require_auth
def get_user_preferences():
    """Kullanıcı tercihlerini getir"""
    try:
        user_id = security.get_current_user_id()
        preferences = settings_manager.get_user_preferences(user_id)
        
        return jsonify({
            'success': True,
            'data': preferences
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Kullanıcı tercihlerini getirme hatası: {str(e)}'
        }), 500

@app.route('/api/user/preferences', methods=['POST'])
@require_auth
@require_csrf
def update_user_preferences():
    """Kullanıcı tercihlerini güncelle"""
    try:
        user_id = security.get_current_user_id()
        data = request.get_json()
        preferences = data.get('preferences', {})
        
        success = settings_manager.set_user_preferences(user_id, preferences)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Tercihler başarıyla güncellendi'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tercihler güncellenemedi'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Kullanıcı tercihlerini güncelleme hatası: {str(e)}'
        }), 500

@app.route('/api/collections')
def get_collections():
    """Tüm koleksiyonları getirir"""
    try:
        collections = db_manager.get_collections()
        return jsonify({
            'success': True,
            'collections': collections
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/styles-by-collection/<collection>')
def get_styles_by_collection(collection):
    """Koleksiyona göre stilleri getirir"""
    try:
        styles = db_manager.get_styles_by_collection(collection)
        return jsonify({
            'success': True,
            'styles': styles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/co2-threshold-check', methods=['POST'])
@require_auth
def check_co2_threshold():
    """CO₂ değerinin eşiği aşıp aşmadığını kontrol et"""
    try:
        data = request.get_json()
        co2_value = data.get('co2_value', 0)
        
        if not isinstance(co2_value, (int, float)):
            return jsonify({
                'success': False,
                'error': 'Geçersiz CO₂ değeri'
            }), 400
        
        threshold = settings_manager.get_co2_threshold()
        is_exceeded = settings_manager.is_threshold_exceeded(co2_value)
        alert_color = settings_manager.get_alert_color()
        
        return jsonify({
            'success': True,
            'data': {
                'co2_value': co2_value,
                'threshold': threshold,
                'is_exceeded': is_exceeded,
                'alert_color': alert_color,
                'percentage': (co2_value / threshold * 100) if threshold > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'CO₂ eşik kontrolü hatası: {str(e)}'
        }), 500

# =====================================================
# EXPORT API ENDPOINTS
# =====================================================

@app.route('/api/export/csv', methods=['POST'])
@require_auth
def export_csv():
    """Dashboard verilerini CSV formatında export et"""
    try:
        user_id = security.get_current_user_id()
        data = request.get_json()
        
        # Export tipini belirle
        export_type = data.get('export_type', 'dashboard')  # dashboard, co2_calculations
        filters = data.get('filters', {})
        
        if export_type == 'dashboard':
            # Dashboard verilerini al
            export_data = export_manager.get_dashboard_data_for_export(user_id, filters)
            filename_prefix = "dashboard_export"
            
        elif export_type == 'co2_calculations':
            # CO2 hesaplama geçmişini al
            limit = filters.get('limit', 1000)
            export_data = export_manager.get_co2_calculations_for_export(user_id, limit)
            filename_prefix = "co2_calculations_export"
            
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz export tipi'
            }), 400
        
        if not export_data:
            return jsonify({
                'success': False,
                'error': 'Export edilecek veri bulunamadı'
            }), 404
        
        # CSV export işlemi
        csv_content, filename = export_manager.export_to_csv(export_data, filename_prefix)
        
        # Response oluştur
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'CSV export hatası: {str(e)}'
        }), 500

@app.route('/api/export/pdf', methods=['POST'])
@require_auth
def export_pdf():
    """Dashboard verilerini PDF formatında export et"""
    try:
        user_id = security.get_current_user_id()
        data = request.get_json()
        
        # Export tipini belirle
        export_type = data.get('export_type', 'dashboard')
        filters = data.get('filters', {})
        title = data.get('title', 'Export Raporu')
        
        if export_type == 'dashboard':
            # Dashboard verilerini al
            export_data = export_manager.get_dashboard_data_for_export(user_id, filters)
            filename_prefix = "dashboard_export"
            title = "Dashboard CO₂ Raporu"
            
        elif export_type == 'co2_calculations':
            # CO2 hesaplama geçmişini al
            limit = filters.get('limit', 1000)
            export_data = export_manager.get_co2_calculations_for_export(user_id, limit)
            filename_prefix = "co2_calculations_export"
            title = "CO₂ Hesaplama Geçmişi Raporu"
            
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz export tipi'
            }), 400
        
        if not export_data:
            return jsonify({
                'success': False,
                'error': 'Export edilecek veri bulunamadı'
            }), 404
        
        # PDF export işlemi
        pdf_content, filename = export_manager.export_to_pdf(export_data, title, filename_prefix)
        
        # Response oluştur
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'PDF export hatası: {str(e)}'
        }), 500

@app.route('/api/export/preview', methods=['POST'])
@require_auth
def export_preview():
    """Export edilecek veriyi önizleme olarak göster"""
    try:
        user_id = security.get_current_user_id()
        data = request.get_json()
        
        export_type = data.get('export_type', 'dashboard')
        filters = data.get('filters', {})
        limit = data.get('preview_limit', 10)  # Önizleme için limit
        
        if export_type == 'dashboard':
            export_data = export_manager.get_dashboard_data_for_export(user_id, filters)
        elif export_type == 'co2_calculations':
            export_data = export_manager.get_co2_calculations_for_export(user_id, 1000)
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz export tipi'
            }), 400
        
        # Önizleme için veriyi sınırla
        preview_data = export_data[:limit] if export_data else []
        
        return jsonify({
            'success': True,
            'data': {
                'preview': preview_data,
                'total_records': len(export_data) if export_data else 0,
                'preview_records': len(preview_data),
                'columns': list(preview_data[0].keys()) if preview_data else []
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Export önizleme hatası: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)