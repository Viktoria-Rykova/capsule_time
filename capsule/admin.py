from django.contrib import admin
from .models import Capsule, CapsuleAvailability, Category, Review
from decimal import Decimal
from django.utils.html import format_html


admin.site.site_header = "Управление сайтом Капсул Времени"
admin.site.index_title = "Добро пожаловать в административный раздел"


class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Цена'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('<1000', 'Менее 1000 руб.'),
            ('1000-5000', '1000 – 5000 руб.'),
            ('>5000', 'Более 5000 руб.'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '<1000':
            return queryset.filter(price__lt=1000)
        elif self.value() == '1000-5000':
            return queryset.filter(price__gte=1000, price__lte=5000)
        elif self.value() == '>5000':
            return queryset.filter(price__gt=5000)
        return queryset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'capsule_type')
    search_fields = ('name',)


@admin.register(Capsule)
class CapsuleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'price', 'discount', 'availability', 'created_at',  'brief_info', 'tag_count')
    list_display_links = ('title',)
    ordering = ('-created_at',)
    list_editable = ('price', 'discount')
    actions = ['make_available', 'set_discount_10_percent']
    search_fields = ('title', 'description__text', 'category__name', 'tags__name')
    list_filter = ('availability', 'category', PriceRangeFilter)
    fields = (
        'title',
        'slug',
        'price',
        'discount',
        'availability',
        'category',
        'description',
        'tags'
    )

    @admin.display(description="Кратко о капсуле")
    def brief_info(self, obj):
        return f"Описание: {len(obj.description.text)} символов." if obj.description else "Нет описания"
    
    @admin.display(description="Кол-во тегов")
    def tag_count(self, obj):
        return obj.tags.count() if hasattr(obj, 'tags') else 0
    
    @admin.action(description="Сделать выбранные капсулы доступными")
    def make_available(self, request, queryset):
        updated = queryset.update(availability=CapsuleAvailability.AVAILABLE.value)
        self.message_user(request, f"{updated} капсул отмечены как доступные.")

    @admin.action(description="Установить скидку 10%% на выбранные капсулы")
    def set_discount_10_percent(self, request, queryset):
        updated = 0
        for capsule in queryset:
            if capsule.price and capsule.price > 0:
                discount_amount = capsule.price * Decimal('0.1')      
                capsule.discount = discount_amount                     
                capsule.price = capsule.price - discount_amount        
                capsule.save()
                updated += 1
        self.message_user(request, f"На {updated} капсул установлена скидка 10%.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.file and obj.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.file.url)
        return "Нет изображения"

    image_preview.short_description = 'Превью изображения'