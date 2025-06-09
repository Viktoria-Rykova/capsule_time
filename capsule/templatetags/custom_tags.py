from django import template
from django.urls import reverse
from django.db import models


register = template.Library()

@register.filter
def add_tax(value):
    try:
        # Вычисляем 13% от значения
        tax = float(value) * 0.13
        # Возвращаем итоговую сумму с добавленным налогом
        return float(value) + tax
    except (ValueError, TypeError):
        return value  # Если ошибка, просто возвращаем исходное значение

@register.simple_tag
def show_discounted_name(capsule, discount_percent):
    try:
        # Вычисляем скидку
        original_price = float(capsule['price'])
        discount = original_price * (discount_percent / 100)
        discounted_price = original_price - discount
        # Формируем строку с названием и скидкой
        return f"{capsule['name']} - Скидка {discount_percent}% (Теперь {discounted_price:.2f} рублей)"
    except (ValueError, TypeError):
        return capsule['name']  # Если ошибка, просто возвращаем название без изменений


@register.filter
def is_image(file_url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(file_url.lower().endswith(ext) for ext in image_extensions)   