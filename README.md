# Zero@Design - Sürdürülebilir Moda Platformu

Zero@Design, tekstil ve moda endüstrisinde sürdürülebilirlik ve şeffaflığı artırmak için geliştirilmiş kapsamlı bir dijital platformdur. Platform, CO₂ ayak izi hesaplama, benchmark analizi, AI destekli öneriler ve Digital Product Passport (DPP) entegrasyonu sunmaktadır.

## 🌟 Özellikler

### Faz 1: Temel Modüller
- **Benchmark Tablosu**: Ürün kategorileri için CO₂ emisyon karşılaştırmaları
- **Style Card**: Ürün detayları ve sürdürülebilirlik analizi
- **Collection Dashboard**: Koleksiyon bazlı CO₂ analizi ve optimizasyon

### Faz 2: AI Agent
- **Kural Tabanlı AI**: Sürdürülebilirlik önerileri
- **Malzeme Optimizasyonu**: Alternatif malzeme önerileri
- **İşlem Optimizasyonu**: Üretim süreçleri için öneriler
- **Koleksiyon Optimizasyonu**: CO₂ azaltım hedefleri

### Faz 3: Demo Arayüzü
- **Responsive Web Interface**: Modern ve kullanıcı dostu arayüz
- **Interaktif Grafikler**: Chart.js ile görselleştirme
- **Real-time Hesaplamalar**: Anlık CO₂ ve sürdürülebilirlik skorları

### Faz 4: DPP/NFT Entegrasyonu
- **Digital Product Passport**: Ürün yaşam döngüsü izlenebilirliği
- **NFT Metadata**: Blockchain entegrasyonu için hazırlık
- **Doğrulama Sistemi**: DPP veri bütünlüğü kontrolü

## 🚀 Kurulum

### Gereksinimler
- Python 3.9+
- Flask 2.3.3
- Modern web tarayıcısı

### Adımlar

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd ZeroAtDesign
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
python app.py
```

4. **Tarayıcıda açın:**
```
http://localhost:5000
```

## 📁 Proje Yapısı

```
ZeroAtDesign/
├── app.py                 # Ana Flask uygulaması
├── ai_agent.py           # AI Agent modülü
├── dpp_nft.py           # DPP/NFT entegrasyonu
├── requirements.txt      # Python bağımlılıkları
├── data/                # Veri dosyaları
├── static/              # CSS, JS, resimler
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/           # HTML şablonları
    ├── base.html
    ├── index.html
    ├── benchmark.html
    ├── style_card.html
    ├── collection.html
    └── dpp.html
```

## 🔧 API Endpoints

### Benchmark
- `GET /api/benchmark-data` - Benchmark verilerini getir

### Style Card
- `POST /api/save-style-card` - Stil kartını kaydet
- `GET /api/style-cards` - Kaydedilmiş stil kartlarını getir

### AI Agent
- `POST /api/ai-suggestions` - AI önerilerini al
- `POST /api/optimize-collection` - Koleksiyon optimizasyonu
- `POST /api/ai-feedback` - AI'ya geri bildirim gönder

### DPP/NFT
- `POST /api/create-dpp` - DPP oluştur
- `GET /api/dpp/<dpp_id>` - DPP detaylarını getir
- `GET /api/dpp-list` - Tüm DPP'leri listele
- `GET /api/nft-metadata/<dpp_id>` - NFT metadata'sını getir

## 🎯 Kullanım Senaryoları

### 1. Benchmark Analizi
- Ürün kategorileri arasında CO₂ emisyon karşılaştırması
- Sektör ortalamaları ile kıyaslama
- Filtreleme ve sıralama özellikleri

### 2. Style Card Oluşturma
- Ürün detaylarını girin (isim, kategori, ağırlık)
- Lif kompozisyonunu tanımlayın
- İşlem adımlarını seçin
- Otomatik CO₂ hesaplama ve sürdürülebilirlik skoru

### 3. AI Destekli Optimizasyon
- Mevcut ürün verilerini analiz edin
- Malzeme alternatifleri alın
- İşlem optimizasyonu önerileri
- "What-if" senaryoları

### 4. DPP Oluşturma
- Style Card'dan DPP oluşturun
- Ürün yaşam döngüsü verilerini kaydedin
- NFT metadata'sı hazırlayın
- Blockchain entegrasyonu için hazırlık

## 🔬 Teknik Detaylar

### CO₂ Hesaplama Modeli
Platform, aşağıdaki faktörleri kullanarak CO₂ ayak izini hesaplar:
- **Malzeme Faktörleri**: Lif türüne göre emisyon katsayıları
- **İşlem Faktörleri**: Boyama, apre gibi işlemler için ek emisyonlar
- **Ağırlık Faktörü**: Ürün ağırlığına göre ölçeklendirme
- **Lojistik**: Taşıma ve dağıtım emisyonları

### Sürdürülebilirlik Skoru
0-100 arası skor hesaplama:
- CO₂ ayak izi (40%)
- Geri dönüştürülmüş malzeme oranı (30%)
- Sertifikalar (20%)
- Yerel üretim (10%)

### AI Agent Algoritması
Kural tabanlı sistem:
- Malzeme optimizasyonu kuralları
- İşlem verimliliği kuralları
- Tedarik zinciri optimizasyonu
- Öğrenme mekanizması (feedback loop)

## 🌍 Sürdürülebilirlik Hedefleri

### Kısa Vadeli (6 ay)
- ✅ Benchmark ve analiz araçları
- ✅ AI destekli öneriler
- ✅ Demo arayüzü

### Orta Vadeli (12 ay)
- 🔄 DPP entegrasyonu
- 🔄 NFT hazırlığı
- 📋 Blockchain entegrasyonu

### Uzun Vadeli (18+ ay)
- 📋 Tam blockchain entegrasyonu
- 📋 Tedarik zinciri izlenebilirliği
- 📋 Sektör standardizasyonu

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

Proje Sahibi: Zero@Design Team
- Email: info@zerodesign.app
- Website: https://zerodesign.app

## 🙏 Teşekkürler

- Design for Net Zero dersi kapsamında geliştirilmiştir
- Sürdürülebilir moda endüstrisi için katkıda bulunan tüm paydaşlara teşekkürler

---

**Not**: Bu platform, tekstil endüstrisinde sürdürülebilirlik ve şeffaflığı artırmak amacıyla geliştirilmiş bir araştırma projesidir. Üretim ortamında kullanım için ek güvenlik ve performans optimizasyonları gerekebilir.