from django.shortcuts import render, get_object_or_404, redirect
from .models import Capsule, CapsuleAvailability, Category, Tag, Review
from django.db.models import Q, CharField, F, Value, Count,  ExpressionWrapper, FloatField, Case, When
from django.db.models.functions import Coalesce
from .forms import CapsuleSimpleForm, ReviewForm, CapsuleSimpleForm
import os
import uuid
from django.http import HttpResponseForbidden
from django.views.generic import View, TemplateView, ListView, DetailView, FormView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .mixins import DataMixin
from django.core.paginator import Paginator
from django.contrib.auth.mixins import PermissionRequiredMixin


def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    name = f.name
    ext = ''
    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]

    suffix = str(uuid.uuid4())
    filename = f"{name}_{suffix}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return os.path.join('uploads', filename)


def index(request):
    reviews = Review.objects.order_by('-created_at')[:10] 
    if request.method == 'POST':
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review_form.save()
            return redirect('index')
    else:
        review_form = ReviewForm()
    capsules = Capsule.objects.annotate(
        source_label=Value("Главная страница", output_field=CharField())
    )

    # Капсулы со скидкой больше 10% с источником
    high_discount_capsules = Capsule.objects.filter(discount__gt=10).annotate(
        source_label=Value("Скидки", output_field=CharField())
    )

    # Доступные капсулы с источником
    available_capsules = Capsule.objects.filter(
        availability=CapsuleAvailability.AVAILABLE.value
    ).annotate(
        source_label=Value("В наличии", output_field=CharField())
    )

    try:
        latest_capsule = Capsule.objects.latest('created_at')
    except Capsule.DoesNotExist:
        latest_capsule = None

    try:
        earliest_capsule = Capsule.objects.earliest('created_at')
    except Capsule.DoesNotExist:
        earliest_capsule = None
    # Капсулы с финальной ценой и уровнем выгоды
    capsules_with_final_price = Capsule.objects.annotate(
        final_price=ExpressionWrapper(
            F('price') - (F('price') * F('discount') / 100),
            output_field=FloatField()
        ),
        benefit_level = Case(
            When(discount__gte=15, then=Value("Супер скидка")),
            When(discount__gte=1, then=Value("Хорошая скидка")),
            default=Value("Без скидки"),
            output_field=CharField()
            ),
    )
    categories = Category.objects.all()
    tags = Tag.objects.all()
    capsule_count = Capsule.objects.aggregate(total=Count('id'))['total']
    capsule_type_counts = Category.objects.annotate(
        capsule_count=Count('capsules')
    ).values('capsule_type', 'capsule_count')
    capsules = Capsule.objects.annotate(
    description_text=Coalesce('description__text', Value('Нет описания'))   
    )

    context = {
        'title': 'Главная',
        'capsules': capsules,
        'high_discount_capsules': high_discount_capsules,
        'latest_capsule': latest_capsule,
        'earliest_capsule': earliest_capsule,
        'available_capsules': available_capsules,
        'capsules_with_final_price': capsules_with_final_price,
        'categories': categories,
        'tags': tags,
        'capsule_count': capsule_count,
        'capsule_type_counts': capsule_type_counts,
        'reviews': reviews,
        'can_delete_review': request.user.has_perm('capsule.delete_review')
        # 'review_form': review_form,
    }

    return render(request, 'index.html', context)


class UploadView(DataMixin, View):
    def get(self, request):
        context = self.get_mixin_context(title='Название вашей капсулы')
        return render(request, 'upload.html', context)


class CapsulesByTagView(DataMixin, ListView):
    model = Capsule
    template_name = 'capsules_by_tag.html'
    context_object_name = 'capsules'

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Capsule.objects.filter(
            tags=self.tag, 
            availability=CapsuleAvailability.AVAILABLE.value
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.get_mixin_context(**context)
        context['tag'] = self.tag
        context['title'] = f"Капсулы с тегом: {self.tag.name}"
        return context


class PaymentView(DataMixin, TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.get_mixin_context(**context)
        context['title'] = 'Оплата'
        return context


def electo(request):
    electronic_category = Category.objects.filter(capsule_type="electronic").first()

    if electronic_category:
        capsules_list = Capsule.objects.filter(
            availability=CapsuleAvailability.AVAILABLE.value,
            category=electronic_category
        ).select_related('description')
    else:
        capsules_list = Capsule.objects.none()

    paginator = Paginator(capsules_list, 3) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'available_capsules': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'electo.html', context)

def nature(request):
    physical_category = Category.objects.filter(capsule_type="physical").first()

    if physical_category:
        capsules_list = Capsule.objects.filter(
            availability=CapsuleAvailability.AVAILABLE.value,
            category=physical_category
        ).select_related('description')
    else:
        capsules_list = Capsule.objects.none()

    paginator = Paginator(capsules_list, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'available_capsules': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'nature.html', context)


class CapsuleDetailView(DataMixin, DetailView):
    model = Capsule
    template_name = 'capsule_detail.html'
    context_object_name = 'capsule'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(**context)


class SimpleCapsuleFormView(DataMixin, FormView):
    template_name = 'simple_form.html'
    form_class = CapsuleSimpleForm

    def form_valid(self, form):
        context = self.get_mixin_context(
            form=self.form_class(),
            success=True,
            data=form.cleaned_data
        )
        return self.render_to_response(context)
    

class ReviewCreateView(DataMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'model_form.html'
    success_url = '/reviews/'

    def form_valid(self, form):
        self.object = form.save()
        context = self.get_mixin_context(success=True, data=self.object)
        context['form'] = self.form_class()
        return self.render_to_response(context)


class ReviewDeleteView(PermissionRequiredMixin, DataMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('index')
    template_name = 'index.html'
    permission_required = 'capsule.delete_review'  # <-- название права
    raise_exception = True  # выбрасывает 403, если прав нет

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        # доп. проверка: только автор или админ может удалить
        if request.user != self.object.name and not request.user.is_staff:
            return HttpResponseForbidden("Вы не можете удалить этот отзыв.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_context = get_index_context(self.request)
        context.update(base_context)
        context = self.get_mixin_context(**context)
        context['deleting_review'] = self.object
        return context
    

class ReviewUpdateView(DataMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_form.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['deleting_review'] = self.object
        context = self.get_mixin_context(**context)
        return context


class CapsuleCreateView(PermissionRequiredMixin, CreateView):
    model = Capsule
    form_class = CapsuleSimpleForm
    template_name = 'add_capsule.html'
    permission_required = 'timecapsule.add_capsule'  # или 'app_name.add_model'
    
    def get_success_url(self):
        return self.object.get_absolute_url()