from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Count, Q
from datetime import datetime
import random

from .models import EntradaAcervo, Contribuidor, Categoria, RegistroAcesso, TipoMidia
from .forms import EntradaAcervoForm

def index(request):
    busca = request.GET.get('q')
    entradas = EntradaAcervo.objects.filter(aprovado=True)
    
    if busca:
        entradas = entradas.filter(
            Q(titulo__icontains=busca) |
            Q(categoria__nome__icontains=busca) |
            Q(conteudo__icontains=busca)
        )
    
    hoje = datetime.now().date()
    random.seed(hoje.toordinal())
    entradas_ids = list(entradas.values_list('id', flat=True))
    aleatoria_id = random.choice(entradas_ids) if entradas_ids else None
    aleatoria = EntradaAcervo.objects.get(id=aleatoria_id) if aleatoria_id else None
    
    categorias_stats = (
        EntradaAcervo.objects.filter(aprovado=True)
        .values('categoria__nome')
        .annotate(total=Count('id'))
    )
    
    qualidade_stats = (
        EntradaAcervo.objects.filter(aprovado=True)
        .values('qualidade')
        .annotate(total=Count('id'))
    )
    
    context = {
        'entradas': entradas,
        'aleatoria': aleatoria,
        'categorias_stats': categorias_stats,
        'qualidade_stats': qualidade_stats,
        'total_entradas': entradas.count(),
        'total_contribuidores': Contribuidor.objects.count(),
    }
    
    return render(request, 'acervo/index.html', context)

def registros_historicos(request):
    categoria_historia = Categoria.objects.get(nome="História")
    memorias_historia = EntradaAcervo.objects.filter(categoria=categoria_historia)
    return render(request, 'registros_historicos.html', {'memorias': memorias_historia})

def banco_emocional(request):
    categoria_emocoes = Categoria.objects.get(nome="Emoções")
    memorias_emocionais = EntradaAcervo.objects.filter(categoria=categoria_emocoes)
    return render(request, 'banco_emocional.html', {'memorias': memorias_emocionais})

def arquivos_culturais(request):
    categoria_cultura = Categoria.objects.get(nome="Cultura")
    memorias_culturais = EntradaAcervo.objects.filter(categoria=categoria_cultura)
    return render(request, 'arquivos_culturais.html', {'memorias': memorias_culturais})

def contribuidores(request):
    termo = request.GET.get('q')
    if termo:
        contribuidores = Contribuidor.objects.filter(usuario__username__icontains=termo)
    else:
        contribuidores = Contribuidor.objects.all()

    return render(request, 'acervo/contribuidores.html', {'contribuidores': contribuidores})

def curadoria(request):
    if request.method == "POST":
        for entrada in EntradaAcervo.objects.filter(aprovado=False):
            qualidade_key = f'qualidade_{entrada.id}'
            if qualidade_key in request.POST:
                nova_qualidade = request.POST.get(qualidade_key)
                if nova_qualidade in dict(EntradaAcervo.TIPO_QUALIDADE).keys():
                    entrada.qualidade = nova_qualidade
                    entrada.aprovado = True
                    entrada.save()
        messages.success(request, "Avaliações salvas com sucesso.")
        return redirect('curadoria')

    entradas_pendentes = EntradaAcervo.objects.filter(aprovado=False)
    return render(request, 'acervo/curadoria.html', {'memorias': entradas_pendentes})



# @login_required
# def enviar_memoria(request):
#     if request.method == 'POST':
#         form = EntradaAcervoForm(request.POST)
#         if form.is_valid():
#             nova_entrada = form.save(commit=False)
#             nova_entrada.aprovado = False 
#             nova_entrada.save()
#             messages.success(request, 'Memória enviada com sucesso para a curadoria!')
#             return redirect('index')
#     else:
#         form = EntradaAcervoForm()
#     
#     return render(request, 'acervo/enviar_memoria.html', {'form': form})

@login_required
def enviar_memoria(request):
    if request.method == 'POST':
        form = EntradaAcervoForm(request.POST, request.FILES)
        if form.is_valid():
            nova_entrada = form.save(commit=False)
            nova_entrada.aprovado = False

            contribuidor, created = Contribuidor.objects.get_or_create(
                usuario=request.user,
                defaults={'bio': '', 'nivel_acesso': 1, 'ativo': True}
            )
            nova_entrada.contribuidor = contribuidor
            nova_entrada.save()

            messages.success(request, 'Memória enviada com sucesso para a curadoria!')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao enviar a memória. Verifique os dados e tente novamente.')

    else:
        form = EntradaAcervoForm()

    return render(request, 'acervo/enviar_memoria.html', {'form': form})

# Detalhe da entrada
def detalhe_entrada(request, entrada_id):
    entrada = EntradaAcervo.objects.get(id=entrada_id)
    entrada.incrementar_visualizacao()
    
    # Registrar acesso
    if request.META.get('REMOTE_ADDR'):
        RegistroAcesso.objects.create(
            entrada=entrada,
            usuario=request.user if request.user.is_authenticated else None,
            ip=request.META.get('REMOTE_ADDR'),
            tipo_midia=entrada.tipo_midia
        )
        
    
    return render(request, 'acervo/detalhe_entrada.html', {'entrada': entrada})

# @login_required
# def enviar_memoria(request):
#     if request.method == 'POST':
#         form = EntradaAcervoForm(request.POST, request.FILES)
#         if form.is_valid():
#             nova_entrada = form.save(commit=False)
#             nova_entrada.aprovado = False
#             
#             # Associar ao contribuidor (cria se não existir)
#             contribuidor, created = Contribuidor.objects.get_or_create(
#                 usuario=request.user,
#                 defaults={'bio': '', 'nivel_acesso': 1, 'ativo': True}
#             )
#             nova_entrada.contribuidor = contribuidor
#             nova_entrada.save()
#             
#             messages.success(request, 'Memória enviada com sucesso para a curadoria!')
#             return redirect('index')
#     else:
#         form = EntradaAcervoForm()
#     
#     return render(request, 'acervo/enviar_memoria.html', {'form': form})

def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Criar perfil de contribuidor
            Contribuidor.objects.create(
                usuario=user,
                bio='',
                nivel_acesso=1,
                ativo=True
            )
            
            # Autenticar e logar o usuário
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, 'Registro concluído com sucesso!')
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'acervo/registrar.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Você está logado como {username}.")
                return redirect('index')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'acervo/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('index')

@login_required
def perfil(request):
    contribuidor = request.user.contribuidor
    entradas = EntradaAcervo.objects.filter(contribuidor=contribuidor).order_by('-data_cadastro')
    
    if request.method == 'POST':
        # Atualizar bio
        nova_bio = request.POST.get('bio', '')
        contribuidor.bio = nova_bio
        contribuidor.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')
    
    return render(request, 'acervo/perfil.html', {
        'contribuidor': contribuidor,
        'entradas': entradas,
        'total_entradas': entradas.count(),
    })
