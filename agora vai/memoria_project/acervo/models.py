from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Contribuidor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contribuidor')
    bio = models.TextField(verbose_name="Biografia", blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    nivel_acesso = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nível de Acesso"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    def __str__(self):
        return self.usuario.username

class RegistroAcesso(models.Model):
    entrada = models.ForeignKey('EntradaAcervo', on_delete=models.CASCADE, verbose_name="Entrada Acessada")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    data_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data de Acesso")
    ip = models.CharField(max_length=50, verbose_name="Endereço IP")

    class Meta:
        verbose_name = "Registro de Acesso"
        verbose_name_plural = "Registros de Acesso"
        ordering = ['-data_acesso']

    def __str__(self):
        return f"Acesso a {self.entrada.titulo} em {self.data_acesso}"

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class TipoMidia(models.Model):
    nome = models.CharField(max_length=50)
    icone = models.CharField(max_length=50, help_text="Classe do ícone (ex: fas fa-image)")

    def __str__(self):
        return self.nome

class EntradaAcervo(models.Model):
    TIPO_QUALIDADE = [
        ('COMUM', 'Comum'),
        ('RARO', 'Raro'),
        ('EXCLUSIVO', 'Exclusivo'),
        ('LEGENDA', 'Lendário'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoria")
    # tipo_midia = models.ForeignKey(TipoMidia, on_delete=models.PROTECT, verbose_name="Tipo de Mídia")
    conteudo = models.TextField(verbose_name="Conteúdo")
    arquivo = models.FileField(upload_to='acervo/', blank=True, null=True, verbose_name="Arquivo (opcional)")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    data_estimada = models.DateField(verbose_name="Data Estimada")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    qualidade = models.CharField(max_length=10, choices=TIPO_QUALIDADE, default='COMUM', verbose_name="Qualidade")
    marcadores = models.CharField(max_length=200, blank=True, verbose_name="Marcadores (tags)")
    visualizacoes = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado pela Curadoria")
    contribuidor = models.ForeignKey(Contribuidor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Contribuidor")

    class Meta:
        verbose_name = "Entrada do Acervo"
        verbose_name_plural = "Entradas do Acervo"
        ordering = ['-data_cadastro']

    def __str__(self):
        return self.titulo

    def incrementar_visualizacao(self):
        self.visualizacoes += 1
        self.save()
