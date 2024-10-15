from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome_completo', 'idade', 'sexo', 'exame']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'exame': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
