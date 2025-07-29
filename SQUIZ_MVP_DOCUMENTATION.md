# 📝 SQUIZ - Kapsamlı Quiz Platformu MVP Dokümantasyonu

## 📋 İçindekiler
1. [Ürün Genel Bakış](#ürün-genel-bakış)
2. [Teknik Mimari](#teknik-mimari)
3. [Özellikler Detayı](#özellikler-detayı)
4. [API Dokümantasyonu](#api-dokümantasyonu)
5. [Kullanıcı Rehberleri](#kullanıcı-rehberleri)
6. [Admin Rehberi](#admin-rehberi)
7. [İş Analizi](#iş-analizi)
8. [Deployment Rehberi](#deployment-rehberi)
9. [Gelecek Planları](#gelecek-planları)

---

## 🎯 Ürün Genel Bakış

### Squiz Nedir?
**Squiz**, modern ve kapsamlı bir online quiz platformudur. Eğitim kurumları, öğretmenler ve öğrenciler için tasarlanmış bu platform, quiz oluşturma, yönetme ve değerlendirme süreçlerini tamamen dijitalleştirir.

### 🚀 Temel Değer Önerisi
- **Kolay Kullanım**: Sezgisel arayüzle hızlı quiz oluşturma
- **Esnek Soru Türleri**: Çoktan seçmeli, açık uçlu, resimli sorular
- **Gerçek Zamanlı Analiz**: Detaylı performans raporları
- **Sosyal Özellikler**: Q&A forum, takip sistemi
- **Mobil Uyumlu**: Tüm cihazlarda mükemmel çalışma
- **Matematiksel İfadeler**: LaTeX desteği ile matematik soruları

### 🎯 Hedef Kitle
- **Birincil**: Eğitim kurumları (üniversite, lise, ortaokul)
- **İkincil**: Özel ders öğretmenleri
- **Üçüncül**: Kurumsal eğitim departmanları
- **Dördüncül**: Kendi kendine öğrenen bireyler

---

## 🏗️ Teknik Mimari

### Sistem Mimarisi
\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React.js      │◄──►│   FastAPI       │◄──►│   MongoDB       │
│   Tailwind CSS  │    │   Python 3.11   │    │   Motor Driver  │
│   Framer Motion │    │   JWT Auth      │    │   Atlas Cloud   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
\`\`\`

### Teknoloji Yığını

#### Frontend (React.js)
- **React**: 18.2.0
- **Tailwind CSS**: Modern, responsive tasarım
- **Framer Motion**: Animasyonlar ve geçişler
- **Axios**: HTTP istekleri
- **MathJax**: Matematik ifadelerinin görüntülenmesi
- **React Image Crop**: Görsel düzenleme

#### Backend (FastAPI)
- **FastAPI**: 0.110.1 - Yüksek performanslı API
- **Python**: 3.11
- **Motor**: Asenkron MongoDB driver
- **JWT**: Güvenli kimlik doğrulama
- **Bcrypt**: Şifre hashleme
- **Pydantic**: Veri validasyonu

#### Database (MongoDB)
- **MongoDB Atlas**: Bulut veritabanı
- **Collections**: users, quizzes, quiz_attempts, questions, answers, discussions
- **Indexing**: Performans optimizasyonu

### Güvenlik Mimarisi
- **JWT Tabanlı Kimlik Doğrulama**: Güvenli token sistemi
- **CORS Yapılandırması**: Cross-origin istekler kontrolü
- **Şifre Hashleme**: Bcrypt ile güvenli şifreleme
- **Rol Tabanlı Erişim**: Admin/User yetki kontrolü
- **Input Validasyonu**: Pydantic ile veri kontrolü

---

## ✨ Özellikler Detayı

### 🔐 Kimlik Doğrulama Sistemi

#### Kullanıcı Kayıt ve Giriş
- **Kullanıcı Kayıt**: Email, isim, şifre ile kayıt
- **Giriş**: Email/şifre ile güvenli giriş
- **Şifre Güvenliği**: Bcrypt hashleme
- **Token Yönetimi**: 24 saat geçerli JWT tokenlar
- **Rol Sistemi**: Admin ve User rolleri

#### Güvenlik Özellikleri
- **Şifre Değiştirme**: Mevcut şifre doğrulaması
- **Token Yenileme**: Otomatik token yenileme
- **Oturum Yönetimi**: Güvenli oturum kontrolü

### 📝 Quiz Oluşturma ve Yönetim

#### Esnek Soru Türleri
1. **Çoktan Seçmeli Sorular**
   - Tek doğru cevap
   - Çoklu doğru cevap
   - 2-6 arası seçenek
   - Görsel destekli seçenekler

2. **Açık Uçlu Sorular**
   - Metin tabanlı cevaplar
   - Anahtar kelime puanlama
   - Kısmi puan desteği
   - Manuel değerlendirme seçeneği

#### Quiz Yapılandırma
- **Kategori Sistemi**: Subject → Subcategory → Quiz hiyerarşisi
- **Zaman Sınırı**: İsteğe bağlı süre kısıtlaması
- **Geçme Notu**: Minimum başarı yüzdesi
- **Karıştırma**: Soru ve seçenek karıştırma
- **Taslak Modu**: Yayınlama öncesi test imkanı

#### Medya Desteği
- **Resim Yükleme**: Base64 formatında resim desteği
- **PDF Ekleri**: Döküman ekleme imkanı
- **Resim Kırpma**: Entegre kırpma aracı
- **Matematiksel İfadeler**: LaTeX ile matematik formülleri

### 📊 Analiz ve Raporlama

#### Gerçek Zamanlı Analytics
- **Quiz İstatistikleri**: Deneme sayısı, ortalama puan
- **Kullanıcı Performansı**: Bireysel başarı analizi
- **Soru Analizi**: Soru bazında doğru/yanlış oranları
- **Kategori Performansı**: Konu başlığına göre analiz

#### Detaylı Raporlama
- **Sınav Sonuçları**: Kapsamlı sonuç görüntüleme
- **İlerleme Takibi**: Kullanıcı gelişim grafikleri
- **Karşılaştırma**: Sınıf/grup karşılaştırmaları
- **Export İmkanı**: Sonuçları dışa aktarma

### ⏱️ Gerçek Zamanlı Quiz Oturumları

#### Oturum Yönetimi
- **Oturum Başlatma**: Quiz için oturum oluşturma
- **Duraklatma/Devam**: Esnek oturum kontrolü
- **Otomatik Kayıt**: Cevapların gerçek zamanlı kaydı
- **Zaman Takibi**: Hassas süre ölçümü

#### Timer Özellikleri
- **Canlı Sayaç**: Gerçek zamanlı geri sayım
- **Otomatik Gönderim**: Süre dolduğunda otomatik gönderim
- **Uyarı Sistemi**: Süre bitiminden önce uyarı
- **Oturum Durumu**: Aktif/Duraklatılmış/Tamamlandı

### 💬 Q&A Forum Sistemi

#### Soru-Cevap Platformu
- **Soru Gönderimi**: Resimli soru paylaşımı
- **Cevap Sistemi**: Çoklu cevap desteği
- **Kabul Edilen Cevap**: En iyi cevap işaretleme
- **Oylama Sistemi**: Upvote/downvote mekanizması

#### Tartışma Özellikleri
- **Thread Sistemi**: İç içe tartışma zincirleri
- **Etiketleme**: Konu bazında kategorilendirme
- **Sabitleme**: Önemli soruları sabitleme (Admin)
- **Durum Yönetimi**: Açık/Cevaplanmış/Kapalı durumlar

### 👥 Sosyal Özellikler

#### Takip Sistemi
- **Kullanıcı Takibi**: Diğer kullanıcıları takip etme
- **Aktivite Akışı**: Takip edilen kullanıcıların aktiviteleri
- **Gizlilik Kontrolleri**: Özel/genel profil ayarları
- **Bildirimler**: Yeni aktiviteler için bildirimler

#### Profil Yönetimi
- **Kişisel Profil**: Detaylı kullanıcı profilleri
- **İstatistikler**: Kişisel performans verileri
- **Gizlilik Ayarları**: Profil görünürlük kontrolü
- **Aktivite Geçmişi**: Geçmiş quiz ve forum aktiviteleri

### 🎛️ Admin Paneli

#### Kullanıcı Yönetimi
- **Kullanıcı Listesi**: Tüm kayıtlı kullanıcılar
- **Rol Ataması**: Admin/User rol yönetimi
- **Aktivasyon**: Kullanıcı hesabı aktif/pasif
- **Detaylı Profiller**: Kullanıcı detay görüntüleme

#### Quiz Yönetimi
- **Toplu İşlemler**: Çoklu quiz yayınlama
- **Klasör Organizasyonu**: Subject/Subcategory yönetimi
- **Quiz Taşıma**: Klasörler arası quiz taşıma
- **Yayın Kontrolü**: Taslak/Yayınlanmış durum yönetimi

#### İstatistik ve Raporlar
- **Platform İstatistikleri**: Genel kullanım verileri
- **Performans Metrikleri**: Sistem performans analizi
- **Kullanıcı Aktivitesi**: Aktif kullanıcı raporları
- **Quiz Popülerliği**: En çok çözülen quizler

---

*[Dokümantasyon devam ediyor... Tam içerik için dosyayı indirin]*
