from django.db import migrations
from django.utils.text import slugify


CATEGORIES = [
    ('Mathématiques', 'Aide et discussions de mathématiques'),
    ('Sciences', 'Physique, chimie et biologie'),
    ('Langues', 'Français, anglais et autres langues'),
    ('Informatique', 'Programmation et technologies'),
    ('Examens', 'Préparations et révisions'),
    ('Méthodologie', "Méthodes d'apprentissage"),
    ('Orientation', 'Orientation scolaire et professionnelle'),
    ('Cours School On', 'Questions liées aux cours School On'),
    ('Mentorat', 'Accompagnement pédagogique'),
    ('Autre éducatif', 'Autres sujets liés à l’apprentissage'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('forum', 'CommunityCategory')
    for order, (name, description) in enumerate(CATEGORIES):
        Category.objects.get_or_create(
            slug=slugify(name),
            defaults={'name': name, 'description': description, 'display_order': order},
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model('forum', 'CommunityCategory')
    Category.objects.filter(slug__in=[slugify(name) for name, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [('forum', '0003_communitycategory_forumpost_parent_post_and_more')]
    operations = [migrations.RunPython(seed_categories, remove_categories)]
