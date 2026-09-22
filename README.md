# Kararsızım

Kullanıcıların kararsız kaldıkları konularda hızlıca anket oluşturup diğer kullanıcılara danışabildiği bir web uygulaması.

**Canlı:** https://kararsizim-murex.vercel.app

Proje detayları ve geliştirme rehberi için [CLAUDE.md](CLAUDE.md) dosyasına bakın.

## Yerel geliştirme

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

`DATABASE_URL` tanımlanmazsa proje yerel SQLite veritabanını kullanır.

## Testler

```bash
python manage.py test
```

## Bilinen sınırlamalar

- Misafir oyları tarayıcı çerezine dayanır; çerez silinirse aynı kişi tekrar oy verebilir.

## Deployment

- **Veritabanı:** Supabase (Postgres), proje `kararsizim` (`eu-central-1`). Bağlantı, Transaction pooler (port 6543) üzerinden `DATABASE_URL` ile yapılır. `public` şemasındaki tüm tablolarda RLS etkin (politikasız) — bu, Supabase'in otomatik Data API'sini kapatır; Django kendi doğrudan Postgres bağlantısıyla (RLS'den etkilenmeden) çalışmaya devam eder.
- **Hosting:** Vercel, `gamzesa/Kararsizim-Project` reposuna bağlı (`master` branch → production). Sıfır yapılandırma: `vercel.json` yok, Django otomatik algılanıyor.
- **Ortam değişkenleri (Vercel):** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` — Vercel proje ayarlarında tanımlı, repoda değil.
- Yeni migration'lar yerel makineden Supabase'e karşı çalıştırılıp (`python manage.py migrate`) sonra `master`'a push edilmeli (build sırasında migration çalışmaz).
