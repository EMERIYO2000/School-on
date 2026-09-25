from django.db import migrations
from django.utils.text import slugify


CATEGORIES = [
    ('Mathématiques', 'Cours et exercices de mathématiques'),
    ('Sciences', 'Physique, chimie et sciences de la vie'),
    ('Langues', 'Français, anglais et autres langues'),
    ('Informatique', 'Programmation, numérique et technologies'),
    ('Économie et gestion', 'Économie, gestion et entrepreneuriat'),
    ('Développement personnel', 'Méthodes de travail et compétences transversales'),
    ('Examens', "Préparation aux examens et concours"),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('courses', 'Category')
    for name, description in CATEGORIES:
        Category.objects.get_or_create(
            slug=slugify(name),
            defaults={'name': name, 'description': description},
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model('courses', 'Category')
    Category.objects.filter(slug__in=[slugify(name) for name, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [('courses', '0010_merge_20260925_0040')]
    operations = [migrations.RunPython(seed_categories, remove_categories)]
