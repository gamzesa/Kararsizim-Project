# Kararsızım — Proje Planı ve Geliştirme Rehberi

> Bu dosya Claude Code için hazırlanmıştır. Projenin kök dizinine `CLAUDE.md` adıyla koy.
> Claude Code her oturumda bu dosyayı okuyarak projenin amacını, kurallarını ve hangi fazda olduğumuzu bilir.
> **Önemli:** Tüm fazlar aynı anda yapılmayacak. Her seferinde yalnızca bir faz üzerinde çalışılır (bkz. Bölüm 10).

---

## 1. Proje Özeti

**Kararsızım**, kullanıcıların kararsız kaldıkları konularda diğer kullanıcılara danışmak için hızlıca anket oluşturabildiği bir web uygulamasıdır.

Örnek: *"Bugün sinemaya mı gitsem, restorana mı?"* → 2 ila 5 seçenek → diğer kullanıcılar oy verir → sonuçlar yüzde olarak görünür.

**Hedef:** Önce çalışan, sade bir **prototip** çıkarmak. Karmaşık mimari, ekstra kütüphane veya erken optimizasyon yok. Sonradan geliştirilecek.

---

## 2. Temel İş Kuralları

| Kural | Açıklama |
|---|---|
| Takip sistemi yok | Kullanıcılar birbirini takip etmez. Herkes platformdaki tüm anketleri görür. |
| Misafir erişimi | Üye olmayanlar anketleri görebilir ve **oy verebilir**. |
| Anket oluşturma | Yalnızca **üye olan** kullanıcılar anket oluşturabilir. Misafir "Anket Oluştur"a tıklarsa giriş sayfasına yönlendirilir (`?next=` ile geri döner). |
| Seçenek sayısı | Her ankette **en az 2, en fazla 5** seçenek olmalı. Hem frontend hem backend doğrular. |
| Kayıt bilgileri | E-posta + kullanıcı adı + parola. E-posta ve kullanıcı adı benzersiz olmalı. |
| Gizlilik | Anketlerde yalnızca **kullanıcı adı** görünür. E-posta hiçbir sayfada, hiçbir HTML/JSON çıktısında gösterilmez. |
| Tek oy | Her kişi bir ankete yalnızca **bir kez** oy verebilir (üye: kullanıcı hesabı ile; misafir: tarayıcı çerezi ile — bkz. Bölüm 5.3). |
| Oy değiştirme | Prototipte oy değiştirme / geri alma **yok**. |
| Sonuçların görünmesi | Oy veren kişi sonuçları hemen görür. Anket sahibi sonuçları her zaman görür. Oy vermemiş kişi yalnızca seçenekleri ve toplam oy sayısını görür. |
| Kendi anketine oy | Anket sahibi kendi anketine oy verebilir. |
| Anket silme | Anket sahibi kendi anketini silebilir (onay sorulur). Düzenleme prototipte yok. |
| Anket süresi | Prototipte anketlerin bitiş süresi yok, sürekli açık kalır. |

---

## 3. Teknoloji Yığını

| Katman | Teknoloji | Not |
|---|---|---|
| Dil | Python 3.12 | Vercel Python runtime ile uyumlu olmalı |
| Framework | Django 5.2 (LTS) | Django template sistemi ile sunucu taraflı render |
| Veritabanı | Supabase (PostgreSQL) | Yalnızca veritabanı olarak kullanılır. Supabase Auth **kullanılmaz**, kimlik doğrulama Django'nun kendi auth sistemi ile yapılır. |
| DB sürücüsü | `psycopg[binary]` (v3) | |
| Ortam değişkenleri | `python-dotenv` + `dj-database-url` | |
| Frontend | Saf HTML + CSS + JavaScript | Framework yok (React/Vue/Tailwind yok). Aynı repo içinde `templates/` ve `static/` klasörlerinde. |
| Deployment | Vercel | Vercel'in sıfır yapılandırmalı Django desteği (Nisan 2026'dan beri). `vercel.json` gerekmez. |

**Kullanılmayacaklar (prototip için):** Django REST Framework, Celery, Redis, Docker, npm/bundler, CSS framework'leri, Supabase JS istemcisi.

`requirements.txt` minimum şöyle olmalı:
```
Django>=5.2,<5.3
psycopg[binary]
dj-database-url
python-dotenv
```

---

## 4. Klasör Yapısı

```
kararsizim/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── manage.py
├── .env.example
├── .gitignore
├── .python-version          # 3.12
├── config/                  # Django proje ayarları
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                # Kayıt, giriş, çıkış, özel kullanıcı modeli
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── polls/                   # Anket, seçenek, oy
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── utils.py             # Misafir oy çerezi yardımcıları
├── templates/
│   ├── base.html
│   ├── accounts/
│   │   ├── register.html
│   │   └── login.html
│   └── polls/
│       ├── poll_list.html
│       ├── poll_detail.html
│       ├── poll_create.html
│       ├── my_polls.html
│       └── _poll_card.html  # Tekrar kullanılan kart parçası
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── main.js          # Genel yardımcılar (CSRF, toast mesajları)
        ├── create_poll.js   # Dinamik seçenek ekleme/silme
        └── vote.js          # fetch ile oy verme ve sonuç animasyonu
```

---

## 5. Veri Modelleri

### 5.1 `accounts.User` (özel kullanıcı modeli)

Proje **en başta** özel kullanıcı modeli ile başlamalı (`AUTH_USER_MODEL = "accounts.User"`), sonradan değiştirmek zordur.

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    # username AbstractUser'dan gelir ve zaten benzersizdir
```

- Giriş **e-posta veya kullanıcı adı** + parola ile yapılabilir (basit özel authentication backend).
- Kullanıcı adı kuralları: 3–20 karakter, yalnızca harf, rakam, alt çizgi ve nokta. Büyük/küçük harf duyarsız benzersizlik kontrolü yap (`iexact`).
- Parola: Django'nun varsayılan parola doğrulayıcıları.

### 5.2 `polls` modelleri

```python
class Poll(models.Model):
    public_id = models.CharField(max_length=12, unique=True, editable=False, default=generate_public_id)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)   # isteğe bağlı açıklama
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    voter_token = models.CharField(max_length=64)   # üye için "u:<user_id>", misafir için "g:<uuid>"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "voter_token"], name="one_vote_per_voter_per_poll"),
        ]
```

- Oy sayıları için ayrı bir sayaç alanı tutma; `annotate(Count("votes"))` ile hesapla (prototip için yeterli).
- `Option` her zaman ait olduğu `Poll` ile doğrulanmalı (başka anketin seçeneğine oy verilemesin).
- URL'lerde ve tüm dış referanslarda `Poll.pk` (sıralı `id`) **değil**, `public_id` kullanılır — böylece toplam anket sayısı URL'den tahmin edilemez. `public_id`, 12 karakterlik, karışabilecek harfleri (l, 1, I, O, 0) içermeyen bir alfabeden rastgele üretilir (`polls/models.py: generate_public_id`).

### 5.3 Misafir oylama mantığı

- İlk ziyarette tarayıcıya `kararsizim_voter` adında bir çerez yerleştirilir: rastgele UUID4, süre 1 yıl, `HttpOnly`, `SameSite=Lax`, production'da `Secure`.
- Misafir oyunda `voter_token = "g:" + uuid`, üye oyunda `voter_token = "u:" + str(user.id)`.
- Aynı ankete ikinci oy denemesinde `UniqueConstraint` + view içindeki kontrol ile "Bu ankete zaten oy verdin" döner.
- **Bilinen sınırlama (bilinçli):** Misafir çerezi silerek tekrar oy verebilir. Prototip için kabul edilebilir; ileride IP tabanlı rate limit eklenebilir. Bunu README'ye not et.
- Misafirken oy verip sonra giriş yapan kullanıcının oylarını birleştirme **yapılmaz**.

---

## 6. Sayfalar ve URL'ler

| URL | View | Erişim | Açıklama |
|---|---|---|---|
| `/` | `poll_list` | Herkes | Tüm anketler, en yeni en üstte, sayfa başına 20 anket (Django `Paginator`). |
| `/anket/<public_id>/` | `poll_detail` | Herkes | Soru, açıklama, yazar kullanıcı adı, seçenekler, oy verme veya sonuçlar. |
| `/anket/<public_id>/oy/` | `vote` | Herkes | Yalnızca `POST`. JSON döner (bkz. 6.1). JS kapalıysa normal form POST ile de çalışmalı ve detay sayfasına yönlendirmeli. |
| `/anket/olustur/` | `poll_create` | Üye (`@login_required`) | Soru + açıklama + 2–5 seçenek. |
| `/anket/<public_id>/sil/` | `poll_delete` | Yalnızca anket sahibi | `POST` ile silme; başkası denerse 403/404. |
| `/anketlerim/` | `my_polls` | Üye | Kullanıcının kendi anketleri. |
| `/kayit/` | `register` | Misafir | Kayıttan sonra otomatik giriş ve anasayfaya yönlendirme. |
| `/giris/` | `login` | Misafir | E-posta/kullanıcı adı + parola. `next` parametresini destekle. |
| `/cikis/` | `logout` | Üye | `POST` ile çıkış (Django 5 gereği). |
| `/admin/` | Django admin | Superuser | Modeller admin'e kayıtlı olmalı. |

### 6.1 Oy verme endpoint'i (JSON)

İstek: `POST /anket/<public_id>/oy/` — body: `option_id`, header: `X-CSRFToken`.

Başarılı yanıt:
```json
{
  "ok": true,
  "total_votes": 42,
  "voted_option_id": 7,
  "results": [
    {"option_id": 7, "text": "Sinema", "votes": 25, "percent": 59.5},
    {"option_id": 8, "text": "Restoran", "votes": 17, "percent": 40.5}
  ]
}
```

Hata yanıtları: zaten oy verilmişse `409` + `{"ok": false, "error": "Bu ankete zaten oy verdin."}`, geçersiz seçenek için `400`.
Yanıtta **hiçbir zaman** e-posta veya kullanıcı listesi bulunmaz.

---

## 7. Arayüz ve Tasarım Rehberi

### 7.1 Genel his
Gençlere hitap eden, **temiz, ferah, açık renkli**, eğlenceli ama sade bir arayüz. Bol boşluk, yumuşak köşeler, hafif gölgeler, küçük mikro-animasyonlar. Mobil öncelikli (mobile-first) ve tamamen responsive.

### 7.2 Renk paleti (CSS değişkenleri olarak `:root` içinde tanımla)

```css
:root {
  --bg: #F7F7FC;            /* sayfa arka planı, çok açık lavanta-beyaz */
  --surface: #FFFFFF;       /* kartlar */
  --primary: #7C5CFF;       /* ana renk: canlı ama yumuşak mor */
  --primary-soft: #EEE9FF;  /* mor arka plan tonları */
  --mint: #3DD9A4;          /* başarı / oy verildi */
  --mint-soft: #E3FAF2;
  --peach: #FFB37A;
  --pink: #FF8AC0;
  --sky: #6CC4FF;
  --lemon: #FFD66B;
  --text: #22223B;          /* ana metin */
  --text-muted: #7A7A95;    /* ikincil metin */
  --border: #E8E8F2;
  --danger: #FF6B6B;
  --radius: 18px;
  --shadow: 0 6px 24px rgba(124, 92, 255, 0.08);
}
```

- Her seçeneğe sırayla bir renk atanır: mor, mint, şeftali, pembe, gökyüzü mavisi (5 seçenek = 5 renk). Sonuç çubukları bu renklerin açık tonlarıyla dolar.
- Koyu, ağır renkler ve siyah arka plan kullanılmaz.

### 7.3 Tipografi
- Font: **Plus Jakarta Sans** (Google Fonts), yedek: `system-ui, -apple-system, "Segoe UI", sans-serif`.
- Başlıklar kalın (700–800), gövde metni 400–500. Türkçe karakterler (ç, ğ, ı, ö, ş, ü) sorunsuz görünmeli.

### 7.4 Bileşenler
- **Üst menü (header):** Solda logo "Kararsızım 🤔" (logo metni mor), sağda: misafirse "Giriş Yap" + "Kayıt Ol" butonları; üyeyse "Anket Oluştur" (belirgin mor buton), "Anketlerim", kullanıcı adı ve "Çıkış".
- **Anket kartı:** Beyaz kart, yumuşak gölge, üstte `@kullaniciadi · 2 saat önce` (Django `timesince`), kalın soru metni, seçenek sayısı ve toplam oy sayısı rozetleri. Hover'da hafif yukarı kalkma.
- **Oy verme:** Seçenekler büyük, dokunmaya uygun butonlar (min 48px yükseklik). Tıklanınca fetch ile oy gider, butonlar yerini animasyonlu yüzde çubuklarına bırakır. Kullanıcının seçtiği seçenekte ✓ işareti ve mint vurgu.
- **Anket oluşturma formu:** Başlangıçta 2 seçenek alanı. "+ Seçenek ekle" butonu 5'e ulaşınca pasifleşir. 3. seçenekten itibaren her alanın yanında "×" silme butonu. Canlı karakter sayacı (soru 200, seçenek 100).
- **Boş durumlar:** Hiç anket yoksa sevimli bir mesaj: "Henüz kimse kararsız değil gibi… İlk anketi sen oluştur!"
- **Mesajlar:** Django `messages` çerçevesi ile sağ üstte kaybolan toast bildirimleri.
- **Emoji kullanımı:** Ölçülü; başlıklarda ve boş durumlarda eğlence katmak için.

### 7.5 Erişilebilirlik
- Yeterli kontrast (açık renkli arka planda metin her zaman `--text`).
- Tüm butonlarda odak (focus) stilleri, form alanlarında `label`.
- `prefers-reduced-motion` açıksa animasyonlar kapatılır.

---

## 8. Ayarlar ve Ortam Değişkenleri

`.env.example`:
```
DJANGO_SECRET_KEY=degistir-beni
DJANGO_DEBUG=True
DATABASE_URL=postgresql://postgres.[PROJE_REF]:[PAROLA]@aws-0-[BOLGE].pooler.supabase.com:6543/postgres
ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
CSRF_TRUSTED_ORIGINS=https://*.vercel.app
```

`settings.py` kuralları:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` ortam değişkenlerinden okunur. Gizli bilgi asla koda yazılmaz, `.env` `.gitignore`'da olur.
- `DATABASE_URL` yoksa yerel geliştirme için SQLite'a düşülür (bu sayede Faz 1–3 Supabase olmadan geliştirilebilir).
- Supabase **connection pooler (transaction mode, port 6543)** ile bağlanırken serverless ortam için:
  ```python
  DATABASES["default"]["CONN_MAX_AGE"] = 0
  DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
  DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = "require"
  ```
- `LANGUAGE_CODE = "tr"`, `TIME_ZONE = "Europe/Istanbul"`, `USE_TZ = True`.
- `STATIC_URL = "/static/"`, `STATICFILES_DIRS = [BASE_DIR / "static"]`, `STATIC_ROOT = BASE_DIR / "staticfiles"`. Production'da statik dosyaları Vercel CDN sunar; ayrıntılar için Vercel'in Django dokümantasyonuna bak.
- `LOGIN_URL = "login"`, `LOGIN_REDIRECT_URL = "poll_list"`, `LOGOUT_REDIRECT_URL = "poll_list"`.
- `DEBUG=False` iken: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`.

---

## 9. Kodlama Kuralları (Claude Code için)

1. **Sadelik önce gelir.** Bir şeyi Django'nun yerleşik özellikleriyle yapabiliyorsan ek paket ekleme.
2. **Arayüz metinleri Türkçe**, kod (değişken, fonksiyon, sınıf adları) ve yorumlar İngilizce.
3. Formlar Django `forms` ile, doğrulama her zaman **backend'de** yapılır; JS doğrulaması yalnızca kullanıcı deneyimi içindir.
4. Tüm POST isteklerinde CSRF koruması aktif. JS `fetch` isteklerinde `csrftoken` çerezinden `X-CSRFToken` başlığı gönderilir.
5. Kullanıcıdan gelen metinler template'lerde otomatik escape edilir; `|safe` kullanma.
6. E-posta alanı hiçbir template'e, JSON yanıtına veya admin dışı sayfaya çıkmaz.
7. Sorgularda `select_related("author")` ve `prefetch_related("options")` kullanarak N+1 sorgularından kaçın.
8. Her fazın sonunda: `python manage.py check`, migration'lar, ve temel testler (`python manage.py test`) sorunsuz çalışmalı.
9. Her fazın sonunda kısa bir özet ver: ne yapıldı, nasıl test edilir, bir sonraki faz için notlar.
10. Bir fazdayken sonraki fazların işine **girme**; gerekirse sadece not düş.

---

## 10. Geliştirme Fazları

### ✅ Faz durumu (Claude Code her faz bitiminde burayı güncellesin)
- [x] Faz 1 — Proje iskeleti ve kimlik doğrulama
- [x] Faz 2 — Anket oluşturma, listeleme ve oylama
- [x] Faz 3 — Arayüz cilası ve etkileşimler
- [ ] Faz 4 — Supabase bağlantısı ve Vercel deployment
- [ ] Faz 5 — (İleride) İyileştirmeler

---

### Faz 1 — Proje İskeleti ve Kimlik Doğrulama

**Kapsam**
- Django projesi (`config`) ve `accounts`, `polls` uygulamalarını oluştur.
- `requirements.txt`, `.gitignore`, `.env.example`, `README.md`.
- Ortam değişkenli `settings.py` (yerelde SQLite).
- Özel `User` modeli (Bölüm 5.1), e-posta veya kullanıcı adı ile giriş yapan authentication backend.
- Kayıt, giriş, çıkış sayfaları ve formları (Türkçe hata mesajları).
- `base.html` (header, mesaj alanı, footer) ve temel `style.css` (renk değişkenleri + font; detaylı cila Faz 3'te).
- Geçici basit anasayfa.
- Admin'e User kaydı.

**Kabul kriterleri**
- Kayıt olunabiliyor; aynı e-posta veya kullanıcı adıyla ikinci kayıt engelleniyor.
- E-posta ile de kullanıcı adı ile de giriş yapılabiliyor.
- Header'da giriş durumuna göre doğru butonlar görünüyor.
- Kayıt/giriş için testler yazılmış ve geçiyor.

---

### Faz 2 — Anket Oluşturma, Listeleme ve Oylama

**Kapsam**
- `Poll`, `Option`, `Vote` modelleri (Bölüm 5.2) ve migration'lar, admin kayıtları.
- Anket oluşturma formu: soru, isteğe bağlı açıklama, 2–5 seçenek (formset veya dinamik alan isimleri). Boş seçenekler yok sayılır, aynı metinli seçenekler engellenir. `create_poll.js` ile seçenek ekleme/silme.
- Anasayfa: tüm anketler, sayfalama, kart görünümü.
- Anket detay sayfası.
- Oy verme: misafir çerezi (Bölüm 5.3), JSON endpoint (Bölüm 6.1), JS kapalıyken form fallback'i.
- Sonuç gösterme kuralları (Bölüm 2).
- "Anketlerim" sayfası ve anket silme.

**Kabul kriterleri**
- Misafir anket göremez değil — **görür ve oy verir**, ama "Anket Oluştur"da giriş sayfasına yönlendirilir.
- 1 veya 6 seçenekli anket backend tarafından reddedilir.
- Aynı kişi (üye veya aynı çerezli misafir) ikinci kez oy veremez.
- Başka anketin seçeneğiyle oy verilemez.
- Sadece anket sahibi silebilir.
- Hiçbir sayfada e-posta görünmez (bunun için bir test yaz).
- Model, form ve view testleri geçiyor.

---

### Faz 3 — Arayüz Cilası ve Etkileşimler

**Kapsam**
- Bölüm 7'deki tasarım rehberinin tam uygulanması.
- Seçenek renkleri, animasyonlu sonuç çubukları (`vote.js`), seçilen seçenekte ✓ ve mint vurgu.
- Kart hover efektleri, toast mesajları, boş durum ekranları.
- Mobil, tablet ve masaüstü için responsive düzen (360px genişlikte kusursuz görünmeli).
- Göreli zaman gösterimi ("2 saat önce"), karakter sayaçları.
- Özel 404 ve 500 sayfaları (aynı tasarım dilinde).
- Erişilebilirlik kontrolleri (Bölüm 7.5).

**Kabul kriterleri**
- Açık, ferah ve tutarlı bir görünüm; tüm sayfalar aynı tasarım dilinde.
- Oy verme sayfa yenilenmeden gerçekleşiyor ve sonuçlar animasyonla geliyor.
- Konsolda JavaScript hatası yok.

---

### Faz 4 — Supabase Bağlantısı ve Vercel Deployment

**Kapsam — Supabase**
- Supabase projesinde **Connect → Transaction pooler** bağlantı dizesini `DATABASE_URL` olarak kullan.
- Bölüm 8'deki pooler ayarlarını uygula.
- Migration'ları **yerel makineden** Supabase'e karşı çalıştır: `python manage.py migrate` (build sırasında migration çalıştırma).
- `createsuperuser` ile admin hesabı oluştur.
- Supabase'in otomatik açtığı Data API tablolara erişmesin diye: Django tabloları `public` şemasında olduğundan, bu tablolarda RLS'yi etkinleştir (politika ekleme) — Django doğrudan Postgres bağlantısıyla çalıştığı için etkilenmez. Bunu README'de açıkla.

**Kapsam — Vercel**
- Vercel, Nisan 2026'dan beri Django'yu **sıfır yapılandırmayla** destekliyor: `manage.py` ve `settings.py` otomatik algılanır, statik dosyalar Vercel CDN'den sunulur. Bu yüzden `vercel.json`, `build_files.sh` veya `/api` klasörü **oluşturma**.
- Uygulamadan önce güncel dokümantasyonu mutlaka oku: https://vercel.com/docs/frameworks/full-stack/django — orada belirtilen gereksinimleri (entrypoint, statik dosya ayarları, Python sürümü) birebir uygula.
- Python sürümünü `.python-version` dosyasıyla sabitle (`3.12`).
- Vercel ortam değişkenleri: `DJANGO_SECRET_KEY` (yeni, güçlü), `DJANGO_DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
- README'ye adım adım deployment talimatı ekle.

**Kabul kriterleri**
- Canlı URL'de kayıt, giriş, anket oluşturma, oy verme çalışıyor.
- Statik dosyalar (CSS/JS/font) yükleniyor.
- `DEBUG=False` ve gizli bilgiler repoda yok.

---

### Faz 5 — İleride Yapılabilecekler (şimdilik YAPMA)
- Anket bitiş süresi / anketi kapatma
- Kategoriler ve etiketler (Yemek, Eğlence, Alışveriş…)
- Arama ve "en popüler / en yeni" sıralama
- Seçeneklere görsel ekleme
- Anket paylaşım linki ve sosyal medya kartları (Open Graph)
- Yorumlar
- Misafir oylar için IP tabanlı rate limit
- Parola sıfırlama (e-posta gönderimi)
- Karanlık mod

---

## 11. Claude Code'a Verilecek Promptlar

Her fazı ayrı bir oturumda veya sırayla, bir öncekinin bittiğini doğruladıktan sonra başlat.

**Faz 1 promptu**
```
CLAUDE.md dosyasını baştan sona oku. Sadece "Faz 1 — Proje İskeleti ve Kimlik Doğrulama"yı uygula.
Önce kısa bir uygulama planı çıkar ve onayımı bekle. Onaydan sonra kodla,
testleri çalıştır, kabul kriterlerini tek tek doğrula ve CLAUDE.md'deki faz durumunu güncelle.
Faz 2'ye geçme.
```

**Faz 2 promptu**
```
CLAUDE.md'yi oku. Faz 1 tamamlandı. Şimdi sadece "Faz 2 — Anket Oluşturma, Listeleme ve Oylama"yı uygula.
Önce planını göster, onayımdan sonra kodla. Misafir oylama ve tek oy kuralına özellikle dikkat et.
Testleri yaz ve çalıştır, kabul kriterlerini doğrula, faz durumunu güncelle.
```

**Faz 3 promptu**
```
CLAUDE.md'yi oku. Faz 1 ve 2 tamamlandı. Şimdi sadece "Faz 3 — Arayüz Cilası ve Etkileşimler"i uygula.
Bölüm 7'deki tasarım rehberine sadık kal: açık renkler, ferah, gençlere hitap eden, mobil öncelikli.
Framework kullanma, saf HTML/CSS/JS. Bitirdiğinde hangi sayfaları nasıl kontrol etmem gerektiğini listele.
```

**Faz 4 promptu**
```
CLAUDE.md'yi oku. Faz 1–3 tamamlandı. Şimdi "Faz 4 — Supabase Bağlantısı ve Vercel Deployment"ı uygula.
Önce Vercel'in Django için güncel önerilen yapılandırmasını kontrol et.
Gizli bilgileri asla koda yazma. Benim elle yapmam gereken adımları (Supabase panelinden bağlantı dizesi alma,
Vercel'e ortam değişkeni ekleme vb.) numaralı bir kontrol listesi olarak ver.
```
