# Generated by Django 3.2.16 on 2024-03-26 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='Слаг'),
        ),
    ]
