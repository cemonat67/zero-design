# 🌐 onatltd.com DNS Planı

Bu dokümant, `onatltd.com` domain'i altında tüm projelerin DNS konfigürasyonunu içerir.

## 📋 DNS Kayıtları Tablosu

| Subdomain | Type | Value (Points To) | Açıklama |
|-----------|------|-------------------|----------|
| `onatltd.com` | A | `VPS_IP` | Ana domain (kurumsal web / landing page) |
| `www.onatltd.com` | CNAME | `onatltd.com` | WWW yönlendirmesi |
| `app.onatltd.com` | A | `VPS_IP` | Zero@Design Production |
| `staging.onatltd.com` | A | `VPS_IP` | Zero@Design Staging |
| `dpp.onatltd.com` | A | `VPS_IP` | Digital Product Passport |
| `hsp.onatltd.com` | A | `VPS_IP` | Health Sustainability Passport |
| `sjit.onatltd.com` | A | `VPS_IP` | Supply Just-In-Time |
| `texyard.onatltd.com` | A | `VPS_IP` | TexYard Sourcing Platform |
| `dashboard.onatltd.com` | A | `VPS_IP` | Rabateks All-in-One Dashboard |

## 🚀 Hızlı Kurulum Adımları

### 1. DNS Kayıtlarını Ekle (Wix DNS Panel)
```
# Öncelikle bu kayıtları ekle (propagation için zaman gerekli)
app.onatltd.com → A → VPS_IP
staging.onatltd.com → A → VPS_IP
```

### 2. Production Deployment
```bash
# .env.prod güncelle
DOMAIN_NAME=app.onatltd.com
SSL_EMAIL=admin@onatltd.com

# SSL kurulum
./scripts/ssl-setup.sh

# Deploy
./scripts/deploy.sh

# Nginx restart
docker-compose -f docker-compose.prod.yml restart nginx
```

### 3. Staging Deployment
```bash
# Staging deploy
docker-compose -f docker-compose.staging.yml up -d

# SSL kurulum (staging için)
DOMAIN_NAME=staging.onatltd.com ./scripts/ssl-setup.sh
```

### 4. Doğrulama
```bash
# Production test
curl -I https://app.onatltd.com/health

# Staging test  
curl -I https://staging.onatltd.com/health
```

## 🔐 SSL Sertifika Seçenekleri

### Seçenek 1: Tek Tek Sertifika
```bash
# Her subdomain için ayrı
./scripts/ssl-setup.sh  # app.onatltd.com için
DOMAIN_NAME=staging.onatltd.com ./scripts/ssl-setup.sh  # staging için
```

### Seçenek 2: Wildcard Sertifika (Önerilen)
```bash
# Tüm subdomain'ler için tek sertifika
./scripts/ssl-wildcard-setup.sh
```

## 📊 Port Konfigürasyonu

| Service | Production Ports | Staging Ports |
|---------|------------------|---------------|
| HTTP | 80 | - |
| HTTPS | 443 | - |
| Staging HTTP | - | 8080 |
| Staging HTTPS | - | 8443 |

## 🏗️ Gelecek Projeler İçin Hazırlık

### Yeni Subdomain Ekleme
1. DNS kaydını ekle: `newproject.onatltd.com → A → VPS_IP`
2. Nginx config oluştur: `nginx/conf.d/newproject.conf`
3. Docker compose oluştur: `docker-compose.newproject.yml`
4. SSL kurulum: `DOMAIN_NAME=newproject.onatltd.com ./scripts/ssl-setup.sh`

### Multi-VPS Dağıtım
```
# Farklı VPS'lere dağıtım örneği
app.onatltd.com → A → 123.45.67.89 (VPS-1)
dpp.onatltd.com → A → 123.45.67.90 (VPS-2)  
dashboard.onatltd.com → A → 123.45.67.91 (VPS-3)
```

## ⚡ Cloudflare Entegrasyonu (Opsiyonel)

### Avantajlar
- ✅ CDN (hızlandırma)
- ✅ DDoS koruması
- ✅ Otomatik SSL
- ✅ Analytics
- ✅ Caching

### Kurulum
1. Domain'i Cloudflare'e transfer et
2. DNS kayıtlarını Cloudflare'de yapılandır
3. SSL/TLS → Full (strict) seç
4. Security → Under Attack Mode (gerektiğinde)

## 🔍 Troubleshooting

### DNS Propagation Kontrolü
```bash
# DNS propagation kontrolü
dig app.onatltd.com
nslookup app.onatltd.com

# Online araçlar
# https://dnschecker.org
# https://whatsmydns.net
```

### SSL Sorunları
```bash
# SSL sertifika kontrolü
openssl s_client -connect app.onatltd.com:443 -servername app.onatltd.com

# Certbot log kontrolü
docker-compose -f docker-compose.prod.yml logs nginx
```

### Nginx Konfigürasyon Test
```bash
# Syntax kontrolü
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 📝 Notlar

- **DNS Propagation**: 1-24 saat sürebilir
- **Wildcard SSL**: `*.onatltd.com` tüm subdomain'leri kapsar
- **Rate Limiting**: Her subdomain için ayrı konfigüre edilebilir
- **Backup**: Her proje için ayrı backup stratejisi uygulanabilir
- **Monitoring**: Tüm subdomain'ler için merkezi monitoring kurulabilir

## 🎯 Öncelik Sırası

1. **Yüksek**: `app.onatltd.com` (Production)
2. **Orta**: `staging.onatltd.com` (Test ortamı)
3. **Düşük**: Diğer projeler (ihtiyaç halinde)

---

**Son Güncelleme**: $(date)
**Versiyon**: 1.0.0