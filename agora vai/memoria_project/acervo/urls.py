from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('registros-historicos/', views.registros_historicos, name='registros_historicos'),
    path('banco-emocional/', views.banco_emocional, name='banco_emocional'),
    path('arquivos-culturais/', views.arquivos_culturais, name='arquivos_culturais'),
    path('contribuidores/', views.contribuidores, name='contribuidores'),
    path('curadoria/', views.curadoria, name='curadoria'),
    path('enviar-memoria/', views.enviar_memoria, name='enviar_memoria'),
    path('entrada/<int:entrada_id>/', views.detalhe_entrada, name='detalhe_entrada'),
    
    # URLs de autenticação
    path('registrar/', views.registrar, name='registrar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)