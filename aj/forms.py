from django import forms
from .models import Project
from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'team_members']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'team_members': forms.CheckboxSelectMultiple(),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assigned_to', 'project']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=Task.STATUS_CHOICES),
            'priority': forms.Select(choices=Task.PRIORITY_CHOICES),
            'assigned_to': forms.Select(),
            'project': forms.Select(),
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255)
