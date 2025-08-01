from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
@login_required
def dashboard(request):
    return render(request, 'app/dashboard.html')

@login_required
def transaction_logging(request):
    return render(request, 'app/transaction_log.html')