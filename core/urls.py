from django.urls import path
from . import views

urlpatterns = [
    #* ==== AUTH URLS ===== *#
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/account/details/', views.account_details, name='account'),
    path('auth/account/delete/confirm', views.delete_account, name='account_delete'),
    #* ===== APP URLS ===== *#
    path('app/dashboard/', views.dashboard, name='dashboard'),
    #* ===== TRANSACTION RELATED URLS ===== *#
    path('app/transactions/log/', views.transaction_logging, name='log_transaction'),
    path('app/transactions/all/', views.transactions_view, name='transactions'),
    path('app/transactions/edit/<str:pk>/', views.transaction_edit, name='edit_transaction'),
    path('app/transactions/delete/<str:pk>/', views.transaction_delete, name='delete_transaction'),
    #* ===== BUDGET GOALS RELATED URLS ===== *#
    path('app/goals/create/', views.set_goal, name='set_goal')
]