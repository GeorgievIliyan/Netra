from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from decimal import Decimal
from . import models
from . import checkers as check
from . import forms

#* ===== MISC ===== *#
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
                print(f"Registration error: {e}")
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
        auth_logout(request)
        messages.info(request, 'You have been logged out of your account.')
        return redirect('login')
    return render(request, 'auth/logout.html')

@login_required
def delete_account(request):
    if request.method == "POST":
        user_to_delete = request.user
        try:
            user_to_delete.delete()
            logout(request) 
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('login')
        except Exception as e:
            print(f'A logout error has occured: {e}')
            messages.error(request, "There was an error deleting your account. Please try again.")
            return render(request, 'auth/delete_account.html')

    return render(request, 'auth/delete_account.html')

@login_required
def account_details(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'auth/account_details.html', context)

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

#* == TRANSACTIONS == *#
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
def transactions_view(request):
    user = request.user
    context = {
        'transactions': models.Transaction.objects.filter(user=user).order_by('-date_time')
    }
    return render(request, 'app/transactions.html', context)

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(models.Transaction, pk = pk)
    if request.method == "POST":
        transaction.delete()
        messages.success(request, 'Transaction deleted succesfully!')
        return redirect('dashboard')
    return render(request, 'app/transaction_delete.html', {'transaction': transaction})

def transaction_edit(request, pk):
    transaction = get_object_or_404(models.Transaction, pk=pk)

    if request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            transaction.title = form.cleaned_data['title']
            transaction.description = form.cleaned_data['description']
            transaction.type = form.cleaned_data['transaction_type']
            transaction.value = form.cleaned_data['value']
            transaction.save()
            messages.success(request, 'Transaction saved!')
            return redirect('dashboard')
    else:
        form = forms.TransactionForm(initial={
            'title': transaction.title,
            'description': transaction.description,
            'transaction_type': transaction.type,
            'value': transaction.value,
        })

    return render(request, 'app/transaction_edit.html', {'form': form, 'transaction': transaction})
        
#* ==== BUDGET GOALS ===== *#
@login_required
def set_goal(request):
    user = request.user
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
                    date = date,
                    user = user
                )
                return redirect('dashboard')
            except:
                messages.error(request, 'Could not create a budget goal! Please try again.')
                return render(request, 'app/set_goal.html', {'form': form})
    else:
        form = forms.GoalForm()
    return render(request, 'app/set_goal.html', {'form': form})

@login_required
def budget_goals(request):
    user_goals = models.BudgetGoal.objects.filter(user=request.user).order_by('-date')
    context = {
        'goals': user_goals
    }
    return render(request, 'app/goals.html', context)

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(models.BudgetGoal, pk = pk)
    
    if request.method == "POST":
        goal.delete()
        return redirect('goals')
    return render(request, 'app/goal_delete.html', {'goal': goal})

@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(models.BudgetGoal, pk = pk)
    if request.method == "POST":
        form = forms.GoalForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            value = form.cleaned_data['value']
            date = form.cleaned_data['date']
            
            try:
                goal.value = value
                goal.title = title
                goal.date = date
                messages.success(request, 'Budget Goal edited succesfully!')
                return redirect('dashboard')
            except:
                messages.error(request, 'Could not update budget goal! Please try again.')
                return render(request, 'app/set_goal.html', {'form': form})
    else:
        form = forms.GoalForm(initial={
            'title': goal.title,
            'value': goal.value,
            'date': goal.date
        })
    return render(request, 'app/goal_edit.html', {'form': form})