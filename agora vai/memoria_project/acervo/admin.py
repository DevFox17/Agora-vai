from django.contrib import admin
from .models import Categoria, EntradaAcervo, Contribuidor, RegistroAcesso, TipoMidia

# Registre seus modelos aqui
admin.site.register(Categoria)
admin.site.register(EntradaAcervo)
admin.site.register(Contribuidor)
admin.site.register(RegistroAcesso)
admin.site.register(TipoMidia)

