from django.forms import ModelForm
from .models import *
from django import forms

class ChatMessageCreateForm(ModelForm):

    class Meta:
        model = GroupMessage
        fields = ['body']
        
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'Add Message ...', 'class': 'p-4 text-black', 'maxlength': '300', 'autofocus': True})
        }