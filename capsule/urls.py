from django.urls import path
from . import views
from .views import (
    UploadView,
    PaymentView,
    CapsuleDetailView,
    CapsulesByTagView,
    SimpleCapsuleFormView,
    ReviewCreateView,
    ReviewDeleteView,
    ReviewUpdateView,
    CapsuleCreateView,
)

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', UploadView.as_view(), name='upload'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('electo/', views.electo, name='electo'),
    path('nature/', views.nature, name='nature'),
    path('add/', CapsuleCreateView.as_view(), name='add_capsule'),
    path('capsule/<slug:slug>/', CapsuleDetailView.as_view(), name='capsule_detail'),
    path('tags/<slug:slug>/', CapsulesByTagView.as_view(), name='capsules_by_tag'),
    path('capsule-form/', SimpleCapsuleFormView.as_view(), name='capsule_simple_form'),
    path('capsule-modelform/', ReviewCreateView.as_view(), name='model_form'),
    path('review/delete/<int:pk>/', ReviewDeleteView.as_view(), name='review_delete'),
    path('review/update/<int:pk>/', ReviewUpdateView.as_view(), name='review_update'),
]
