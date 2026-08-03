from django import forms
from .models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Full name',
               'pattern': '[a-zA-Z ]+', 'title': 'Enter Characters Only'}), required=True, max_length=100)
    loginid = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Choose a login ID',
               'pattern': '[a-zA-Z0-9]+'}), required=True, max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password',
               'pattern': '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}',
               'title': 'Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters'}),
        required=True, max_length=100)
    mobile = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '10-digit mobile number',
               'pattern': '[56789][0-9]{9}'}), required=True, max_length=100)
    email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'you@example.com',
               'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'}), required=True, max_length=100)
    locality = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Locality'}), required=True, max_length=100)
    address = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 4, 'cols': 22, 'placeholder': 'Address'}), required=True, max_length=250)
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'City', 'autocomplete': 'off',
               'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True, max_length=100)
    state = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'State', 'autocomplete': 'off',
               'pattern': '[A-Za-z ]+', 'title': 'Enter Characters Only '}), required=True, max_length=100)
    status = forms.CharField(widget=forms.HiddenInput(), initial='waiting', max_length=100)

    class Meta():
        model = UserRegistrationModel
        fields = '__all__'
