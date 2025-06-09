from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class CapsuleType(models.TextChoices):
    electronic = 'electronic', 'Электронные'
    physical = 'physical', 'Физические'


class CapsuleAvailability(models.TextChoices):
    AVAILABLE = 'available', 'В наличии'
    UNAVAILABLE = 'unavailable', 'Не в наличии'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    capsule_type = models.CharField(
        max_length=20,
        choices=CapsuleType.choices,
        default=CapsuleType.electronic.value,
        verbose_name="Тип капсулы"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    slug = models.SlugField(null=True, unique=True, blank=True, verbose_name="Слаг")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class CapsuleDescription(models.Model):
    text = models.TextField(verbose_name="Полное описание")

    def __str__(self):
        return self.text[:100]
    
    class Meta:
        verbose_name = "Описание капсулы"
        verbose_name_plural = "Описания капсул"


class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ваше имя")
    text = models.TextField(verbose_name="Отзыв")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка (1-5)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    file = models.FileField(upload_to='review_files/', blank=True, null=True, verbose_name="Файл")

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"
    
    class Meta:
        verbose_name_plural = "Отзывы"


class CapsuleFile(models.Model):
    file = models.FileField(upload_to='capsule_files/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Файл {self.file.name}"


class Capsule(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость (руб.)")
    discount = models.IntegerField(default=0, verbose_name="Скидка (%)")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Слаг")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    description = models.OneToOneField(
        CapsuleDescription,
        on_delete=models.CASCADE,
        related_name="capsule",
        verbose_name="Полное описание",
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="capsules",
        verbose_name="Категория"
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="capsules",
        blank=True,
        verbose_name="Теги"
    )

    availability = models.CharField(
        max_length=20,
        choices=CapsuleAvailability.choices,
        default=CapsuleAvailability.AVAILABLE.value,
        verbose_name="Доступность"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('capsule_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Капсула"
        verbose_name_plural = "Капсулы"
