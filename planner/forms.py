from django import forms
from .models import StudyTask

class StudyTaskForm(forms.ModelForm):
    class Meta:
        model = StudyTask
        fields = ['subject', 'hours', 'deadline']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject e.g. DBMS, CN, ML'
            }),
            'hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hours'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
