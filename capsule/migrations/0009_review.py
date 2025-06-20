# Generated by Django 4.2.20 on 2025-06-07 14:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capsule', '0008_delete_timecapsule'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ваше имя')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Оценка (1-5)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
            ],
        ),
    ]
