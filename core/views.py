from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from decimal import Decimal
from . import models
from . import checkers as check
from . import forms

#* ===== AUTHENTICATION VIEWS ===== *#
def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                models.UserProfile.objects.create(user=user)
                messages.success(request, 'Account created successfully!')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Could not create account. Please try again!')
        return render(request, 'auth/register.html', {'form': form})

    else:
        form = forms.RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username = username, password = password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Logged in succesfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid creditentials!')
                return render(request, 'auth/login.html', {'form':form})
    else:
        form = forms.LoginForm()
    return render(request, 'auth/login.html', {"form": form})

@login_required
def logout(request):
    if request.method == "POST":
        logout(request)
        return redirect('dashboard')
    return render(request, 'auth/logout.html')

@login_required
def delete_account(request):
    if request.method == "POST":
        user_to_delete = request.user
        logout(request) 
        try:
            user_to_delete.delete()
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('home')
        except Exception as e:
            print(f'A logout error has occured: {e}')
            messages.error(request, "There was an error deleting your account. Please try again.")
            return render(request, 'auth/delete_account_confirm.html')

    return render(request, 'auth/delete_account_confirm.html')

#* ===== MAIN APPLICATION ===== *#

def get_user_financial_summary(user, start_date=None, end_date=None):
    queryset = models.Transaction.objects.filter(user=user, value__isnull=False)
    
    if start_date:
        start_datetime = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        queryset = queryset.filter(date_time__gte=start_datetime)
    if end_date:
        end_datetime = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))
        queryset = queryset.filter(date_time__lte=end_datetime)

    income_sum = queryset.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    expenses_sum = queryset.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    savings_sum = queryset.filter(type='saving').aggregate(total=Sum('value'))['total'] or 0

    net_balance = income_sum - expenses_sum

    return {
        'total_income': income_sum,
        'total_expenses': expenses_sum,
        'total_savings': savings_sum,
        'net_balance': net_balance,
    }
    
@login_required
def dashboard(request):
    user = request.user
    # Date calculations
    today = timezone.localdate()

    day_start_date = today
    day_end_date = today

    week_start_date = today - datetime.timedelta(days=6)
    week_end_date = today

    month_start_date = today.replace(day=1)
    if today.month == 12:
        month_end_date = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
    else:
        month_end_date = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)

    # Financial summary for each day
    summary_today = get_user_financial_summary(user, start_date=day_start_date, end_date=day_end_date)
    summary_week = get_user_financial_summary(user, start_date=week_start_date, end_date=week_end_date)
    summary_month = get_user_financial_summary(user, start_date=month_start_date, end_date=month_end_date)

    # Retriving all budget goals
    goals = models.BudgetGoal.objects.filter(
        date__year=today.year,
        date__month=today.month
    ).order_by('-date')

    for goal in goals:
        if goal.value and goal.value > 0:
            total_expenses = summary_month['total_expenses']
            goal_value = goal.value
        
            # Decimal conversion
            if not isinstance(total_expenses, Decimal):
                total_expenses = Decimal(str(total_expenses))
            if not isinstance(goal_value, Decimal):
                goal_value = Decimal(str(goal_value))
        
            progress = (total_expenses / goal_value) * Decimal('100')

            goal.progress_to_goal = min(max(progress, Decimal('0')), Decimal('100'))
        else:
            goal.progress_to_goal = None


    # Context passing
    context = {
        'transactions': models.Transaction.objects.filter(user=user).order_by('-date_time'),
        'summary_today': summary_today,
        'summary_week': summary_week,
        'summary_month': summary_month,
        'goals': goals,
        'month_start_date': month_start_date,
    }

    return render(request, 'app/dashboard.html', context)

@login_required
def transaction_logging(request):
    if request.method == "POST":
        user = request.user
        form = forms.TransactionForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            type = form.cleaned_data['transaction_type']
            value = Decimal(str(form.cleaned_data['value']))
            
            try:
                models.Transaction.objects.create(
                    user = user,
                    title = title,
                    description = description,
                    type = type,
                    value = value
                )
                messages.success(request, 'Logged transaction succesfully!')
                return redirect('dashboard')
            except Exception as e:
                print(f"An error occured while logging a transaction: {e}.")
                messages.error(request,"Could not log transaction! Please try again.")
                return render(request, 'app/transaction_log.html', {'form': form})
    else:
        form = forms.TransactionForm()
    return render(request, 'app/transaction_log.html', {'form': form})

@login_required
def set_goal(request):
    if request.method == "POST":
        form = forms.GoalForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            value = form.cleaned_data['value']
            date = form.cleaned_data['date']
            
            try:
                models.BudgetGoal.objects.create(
                    title = title,
                    value = value,
                    date = date
                )
                return redirect('dashboard')
            except:
                messages.error(request, 'Could not create a budget goal! Please try again.')
                return render(request, 'app/set_goal.html', {'form': form})
    else:
        form = forms.GoalForm()
    return render(request, 'app/set_goal.html', {'form': form})