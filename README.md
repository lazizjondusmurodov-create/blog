# Blog loyihasi (Django)

Diagrammadagi 4 ta jadval asosida qurildi: Author, Category, Blog, Image
(models `posts/models.py` faylida).

## Ishga tushirish

1. Virtual muhit yaratish:
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (macOS/Linux)

2. Kutubxonalarni o'rnatish:
   pip install -r requirements.txt

3. Migratsiya:
   python manage.py makemigrations
   python manage.py migrate

4. Admin uchun foydalanuvchi yaratish:
   python manage.py createsuperuser

5. Serverni ishga tushirish:
   python manage.py runserver

Keyin brauzerda:
- http://127.0.0.1:8000/        -> blog ro'yxati
- http://127.0.0.1:8000/admin/  -> admin panel (Author, Category, Blog, Image qo'shish/tahrirlash)
