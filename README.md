# Kararsızım

Kullanıcıların kararsız kaldıkları konularda hızlıca anket oluşturup diğer kullanıcılara danışabildiği bir web uygulaması.

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
