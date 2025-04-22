from django import forms
from .models import EntradaAcervo, Categoria, TipoMidia
from django.core.validators import MinLengthValidator

class EntradaAcervoForm(forms.ModelForm):
    class Meta:
        model = EntradaAcervo
        fields = ['titulo', 'categoria', 'arquivo', 'data_estimada', 'marcadores']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título da memória'}),
            'data_estimada': forms.DateInput(attrs={'type': 'date'}),
            'marcadores': forms.TextInput(attrs={'placeholder': 'Ex: importante, histórico, emocional'}),
        }
        
        labels = {
            'titulo': 'Título',
            'data_estimada': 'Data Estimada',
            'marcadores': 'Marcadores (tags)',
        }

    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        empty_label="Escolha uma categoria",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    conteudo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        validators=[MinLengthValidator(20)],
        label="Conteúdo",
        help_text="Descreva em detalhes a memória que deseja preservar (mínimo 20 caracteres)"
    )

    arquivo = forms.FileField(
        required=False,
        label="Arquivo (opcional)",
        help_text="Envie uma foto, áudio, vídeo ou documento relacionado"
    )