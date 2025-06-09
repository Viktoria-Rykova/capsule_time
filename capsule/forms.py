from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Review, Capsule


class CapsuleSimpleForm(forms.ModelForm):
    tags = forms.CharField(
        label="Теги (через запятую)",
        help_text="Например: память,воспоминания,будущее",
        required=False
    )

    class Meta:
        model = Capsule
        fields = ['title', 'description', 'price', 'discount', 'slug', 'tags']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'price': 'Цена',
            'discount': 'Скидка',
            'slug': 'Слаг',
        }
        help_texts = {
            'tags': 'Введите теги через запятую',
        }

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        validate_discount(discount)
        return discount

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        validate_slug(slug)
        return slug


def no_bad_words(value):
    forbidden = ['дурак', 'плохо', 'ужасно']
    for word in forbidden:
        if word in value.lower():
            raise ValidationError("Пожалуйста, не используйте оскорбительные слова.")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating', 'file']
        labels = {
            'name': 'Имя',
            'text': 'Ваш отзыв',
            'rating': 'Оценка (1-5)',
            'file': 'Загрузите файл',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        no_bad_words(text)
        return text
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.mp4']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError("Недопустимый тип файла.")
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Файл слишком большой (макс. 10 МБ).")
        return file


