
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Author, Category, Blog, Image
from django.core.files import File

def populate():
    # Add authors using person_1.jpg to person_5.jpg
    author_names = [
        "Ali Valiyev",
        "Diyorbek Abdullaev",
        "Ziyoda Rahmonova",
        "Firdavs Karimov",
        "Nodira Xolmirzoda"
    ]
    author_bios = [
        "Texnologiya va dasturlash sohasida mutaxassis.",
        "Sayohat va fotografiya sevuvchi.",
        "Madaniyat va san'at tarixchisi.",
        "Sport va sog'lom turmush tarzi mutaxassisi.",
        "Kulinariya va taomlar tayyorlash ustasi."
    ]
    authors = []
    for i in range(1, 6):
        author, created = Author.objects.get_or_create(
            name=author_names[i-1],
            defaults={"bio": author_bios[i-1]}
        )
        if created:
            image_path = os.path.join(os.path.dirname(__file__), 'images', f'person_{i}.jpg')
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    author.image.save(f'person_{i}.jpg', File(f))
                    author.save()
        authors.append(author)

    # Add categories
    category_titles = [
        "Texnologiya",
        "Sayohat",
        "Madaniyat",
        "Sport",
        "Kulinariya"
    ]
    categories = []
    for i, title in enumerate(category_titles, 1):
        category, created = Category.objects.get_or_create(title=title)
        if created:
            # Use hero images for categories
            image_path = os.path.join(os.path.dirname(__file__), 'images', f'hero_{i}.jpg')
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    category.image.save(f'hero_{i}.jpg', File(f))
                    category.save()
        categories.append(category)

    # Add blogs with img_1_sq.jpg to img_7_sq.jpg
    blog_titles = [
        "Django 5.0 yangiliklari",
        "Dunyo bo'ylab sayohat qilish uchun 5 sabab",
        "O'zbekistonning madaniy merosi",
        "Yiliga sog'lom turmush tarzi",
        "O'zbek taomlari",
        "Python asoslari",
        "Fotografiya uchun kerakli narsalar"
    ]
    blog_short_descriptions = [
        "Django 5.0 versiyasida chiqgan yangi imkoniyatlar haqida.",
        "Sayohat qilish uchun eng yaxshi davlatlar.",
        "O'zbekistonning madaniy merosi va tarixiy joylari.",
        "Yiliga sog'lom turmush tarzi qanday o'tkazish.",
        "O'zbek taomlarini tayyorlash retseptlari.",
        "Python dasturlash tilining asoslari.",
        "Fotografiya uchun kerakli vositalar va maslahatlar."
    ]
    blog_long_descriptions = [
        "Django 5.0 versiyasida ko'plab yangi imkoniyatlar va yaxshilanishlar chiqdi. Ular orasida async viewlar, yangi admin interfeysi va boshqalar bor.",
        "Dunyo bo'ylab sayohat qilish sizga ko'plab sabablar bor. Masalan, yangi odamlar bilan tanishish, yangi madaniyatlarni bilish va hokazo.",
        "O'zbekistonning madaniy merosi juda boy. Bu yerda Samarqand, Buxoro, Xiva kabi tarixiy shaharlar bor.",
        "Yiliga sog'lom turmush tarzi o'tkazish uchun sport bilan shug'ullanishing, to'g'ri ovqatlanishing kerak.",
        "O'zbek taomlari juda mazali. Masalan, plov, manti, lag'mon va boshqalar.",
        "Python dasturlash tili hozirgi kunda eng mashhur dasturlash tillaridan biri.",
        "Fotografiya uchun kerakli vositalar kamera, ob'ektiv, tripod va boshqalar."
    ]

    for i in range(1, 8):
        # Cycle through authors and categories
        author = authors[(i-1) % len(authors)]
        category = categories[(i-1) % len(categories)]
        blog, created = Blog.objects.get_or_create(
            title=blog_titles[i-1],
            defaults={
                "short_description": blog_short_descriptions[i-1],
                "long_description": blog_long_descriptions[i-1],
                "category": category,
                "author": author
            }
        )
        if created:
            # Add img_i_sq.jpg as the main image
            image_path = os.path.join(os.path.dirname(__file__), 'images', f'img_{i}_sq.jpg')
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img = Image(blog=blog)
                    img.image.save(f'img_{i}_sq.jpg', File(f))
                    img.save()

if __name__ == '__main__':
    print("Populating data...")
    populate()
    print("Done!")

