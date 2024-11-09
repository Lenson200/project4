from django import forms
from .models import UserProfile

class ProfileImageForm(forms.ModelForm):
    # Define the 'date_of_birth' field manually, applying widget attributes
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'placeholder': 'Date of birth', 
            'type': 'date'  
        })
    )

    class Meta:
        model = UserProfile
        fields = ['image', 'about', 'date_of_birth']