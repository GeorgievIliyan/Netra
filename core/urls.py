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
    path('netra/dashboard/', views.dashboard, name='dashboard'),
    #* ===== TRANSACTION RELATED URLS ===== *#
    path('netra/transactions/log/', views.transaction_logging, name='log_transaction'),
    path('netra/transactions/all/', views.transactions_view, name='transactions'),
    path('netra/transactions/edit/<str:pk>/', views.transaction_edit, name='edit_transaction'),
    path('netra/transactions/delete/<str:pk>/', views.transaction_delete, name='delete_transaction'),
    #* ===== BUDGET GOALS RELATED URLS ===== *#
    path('netra/goals/create/', views.set_goal, name='set_goal'),
    path('netra/goals/all/', views.budget_goals, name='goals'),
    path('netra/goals/edit/<str:pk>/', views.goal_edit, name='edit_goal'),
    path('netra/goals/delete/<str:pk>/confirm', views.goal_delete, name='delete_goal')
]