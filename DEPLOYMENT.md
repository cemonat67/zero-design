# Zero@Design Production Deployment Guide

Bu rehber Zero@Design uygulamasının production ortamına deployment sürecini açıklar.

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
- Docker & Docker Compose
- Domain adı (örn: onatltd.com)
- VPS/Server (minimum 2GB RAM, 20GB disk)

### 2. Deployment Adımları

```bash
# 1. Repository'yi klonlayın
git clone <your-repo-url>
cd Zero@Design

# 2. Production environment dosyasını oluşturun
cp .env.prod.example .env.prod
nano .env.prod  # Değerleri doldurun

# 3. Deployment script'ini çalıştırın
./scripts/deploy.sh
```

## 📋 Detaylı Kurulum

### Environment Konfigürasyonu

`.env.prod` dosyasını oluşturun ve aşağıdaki değerleri doldurun:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here-min-32-chars
CSRF_SECRET_KEY=your-csrf-secret-key-here-min-32-chars

# Database Configuration
DATABASE_URL=postgresql://username:password@postgres:5432/zero_design_prod
POSTGRES_DB=zero_design_prod
POSTGRES_USER=zero_design_user
POSTGRES_PASSWORD=your-strong-database-password-here

# Domain Configuration
DOMAIN_NAME=onatltd.com
SSL_EMAIL=admin@onatltd.com
```

### Manuel Deployment

```bash
# 1. Production Docker Compose ile başlatın
docker-compose -f docker-compose.prod.yml up -d

# 2. SSL sertifikası kurun
./scripts/ssl-setup.sh

# 3. Servislerin durumunu kontrol edin
docker-compose -f docker-compose.prod.yml ps
```

## 🔧 Servis Konfigürasyonları

### Docker Services

- **web**: Flask uygulaması (Gunicorn ile)
- **postgres**: PostgreSQL veritabanı
- **nginx**: Reverse proxy ve SSL termination
- **certbot**: Let's Encrypt SSL sertifika yönetimi
- **postgres_backup**: Otomatik veritabanı yedekleme
- **watchtower**: Container güncellemeleri

### Nginx Konfigürasyonu

- HTTP → HTTPS yönlendirme
- Rate limiting (API: 10 req/s, Login: 5 req/m)
- Security headers (HSTS, CSP, XSS Protection)
- Gzip compression
- Static file caching

### Security Features

- Non-root container kullanıcısı
- Database erişimi sadece app container'ından
- SSL/TLS encryption (TLS 1.2+)
- Security headers
- Rate limiting
- CSRF protection

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Servis durumu
./scripts/deploy.sh status

# Health check
curl https://onatltd.com/health
```

### Logs

```bash
# Tüm servislerin logları
docker-compose -f docker-compose.prod.yml logs -f

# Sadece web servisinin logları
docker-compose -f docker-compose.prod.yml logs -f web
```

### Backup

```bash
# Manuel backup
./scripts/deploy.sh backup

# Backup dosyaları
ls -la /var/lib/docker/volumes/zero_design_postgres_backups/_data/
```

## 🔄 Güncelleme Süreci

```bash
# 1. Yeni kodu çekin
git pull origin main

# 2. Deployment script'ini çalıştırın
./scripts/deploy.sh

# 3. Servislerin durumunu kontrol edin
./scripts/deploy.sh status
```

## 🔒 HTTP → HTTPS Geçiş Süreci

Uygulama başlangıçta HTTP-only modda çalışır. Domain hazır olduğunda HTTPS'e geçiş için:

### 1. Domain DNS Ayarları
```bash
# DNS A kaydı ekleyin
zero-design.<domain> → VPS_IP_ADDRESS
```

### 2. Environment Konfigürasyonu
`.env.prod` dosyasında domain bilgilerini güncelleyin:
```bash
DOMAIN_NAME=zero-design.<your-domain>
SSL_EMAIL=admin@<your-domain>
```

### 3. Nginx HTTPS Konfigürasyonu
`nginx/conf.d/default.conf` dosyasında HTTPS server block'unu aktifleştirin:
```bash
# HTTPS server block yorumlarını kaldırın (# işaretlerini silin)
# SSL certificate path'lerini kontrol edin
```

### 4. SSL Sertifikası Kurulumu
```bash
# SSL kurulum script'ini çalıştırın
./scripts/ssl-setup.sh

# Nginx'i yeniden başlatın
docker-compose -f docker-compose.prod.yml restart nginx
```

### 5. HTTPS Doğrulama
```bash
# HTTPS endpoint'ini test edin
curl -I https://zero-design.<your-domain>/health

# HTTP → HTTPS yönlendirmesini test edin
curl -I http://zero-design.<your-domain>/
```

### 6. Deployment Tag'i
```bash
git tag -a v1.1.0-https -m "Prod: HTTPS enabled"
git push origin v1.1.0-https
```

**Not**: Bu adımlar tek seferde uygulanmalı ve domain DNS ayarlarının propagation süresi (5-60 dakika) beklenmeli.

## 🚨 Troubleshooting

### Yaygın Sorunlar

1. **SSL Sertifikası Alınamıyor**
   - Domain DNS ayarlarını kontrol edin
   - Port 80'in açık olduğundan emin olun
   - Domain adının doğru olduğunu kontrol edin

2. **Database Bağlantı Hatası**
   - PostgreSQL container'ının çalıştığını kontrol edin
   - Database credentials'ları kontrol edin
   - Network bağlantısını kontrol edin

3. **Web Servisi Başlamıyor**
   - Gunicorn loglarını kontrol edin
   - Environment variables'ları kontrol edin
   - Port çakışması olup olmadığını kontrol edin

### Log Analizi

```bash
# Web servis logları
docker-compose -f docker-compose.prod.yml logs web

# Database logları
docker-compose -f docker-compose.prod.yml logs postgres

# Nginx logları
docker-compose -f docker-compose.prod.yml logs nginx
```

## 📈 Performance Optimization

### Gunicorn Konfigürasyonu

- 4 worker process
- 120 saniye timeout
- Keep-alive connections
- Request limiting (1000 requests per worker)

### Database Optimization

- Connection pooling
- Otomatik backup (günlük)
- 7 gün backup retention
- Health checks

### Nginx Optimization

- Gzip compression
- Static file caching (1 yıl)
- Connection keep-alive
- Buffer optimization

## 🔐 Security Checklist

- [ ] Güçlü şifreler kullanıldı
- [ ] SSL sertifikası kuruldu
- [ ] Security headers aktif
- [ ] Rate limiting yapılandırıldı
- [ ] Database erişimi kısıtlandı
- [ ] Non-root user kullanıldı
- [ ] Firewall kuralları ayarlandı
- [ ] Backup sistemi aktif

## 📞 Destek

Deployment sırasında sorun yaşarsanız:

1. Logları kontrol edin
2. Health check endpoint'ini test edin
3. Network bağlantısını kontrol edin
4. DNS ayarlarını doğrulayın

## 🎯 Production Environment Seçenekleri

### VPS Providers
- **DigitalOcean**: $10-20/ay, kolay kurulum
- **Hetzner**: €4-10/ay, uygun fiyat
- **Linode**: $10-20/ay, güvenilir
- **AWS EC2**: $10-30/ay, ölçeklenebilir

### Serverless Alternatifi
- **Frontend**: Vercel/Netlify
- **Backend**: Railway/Render
- **Database**: Supabase/PlanetScale

Her iki seçenek için de gerekli konfigürasyon dosyaları hazır durumda.