from django import forms
from . import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username: ")
    email = forms.EmailField(label="Email: ")
    password = forms.CharField(widget=forms.PasswordInput, label="Password: ")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password: ")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken! Please use a different one instead.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use! Please use a different one instead!")
        return email


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords do not match!")

        return cleaned_data
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username: ")
    password = forms.CharField(widget=forms.PasswordInput, label="Password: ")
    
class TransactionForm(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    description = forms.CharField(
        label="Description: ",
        widget=forms.Textarea,
        max_length=300,
        required=False,
        help_text="*optional Provide description (max 300 characters)." 
    )
    transaction_type = forms.ChoiceField(choices=models.Transaction.TRANSACTION_TYPES, label="Choose transaction type: ", required=True)
    category = forms.ModelChoiceField(
        queryset= models.TransactionCategory.objects.all(),
        required=False,
        label="Category: "
    )
    value = forms.FloatField(required=True, validators=[
            MinValueValidator(0, message="Transaction can\'t be less than 0!"),
        ])
    
class GoalForm(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    value = forms.DecimalField(required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    
class NoteForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title: ")
    text = forms.CharField(widget=forms.Textarea, label="Your thoughts and observations: ")