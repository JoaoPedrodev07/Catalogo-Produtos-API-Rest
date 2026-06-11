from django.contrib import admin
from .models import Categoria, ItemPedido, Pedido, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = ("id", "nome")
	search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
	list_display = ("id", "nome", "categoria", "preco", "estoque", "data_criacao")
	list_filter = ("categoria",)
	search_fields = ("nome", "descricao")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
	list_display = ("id", "numero", "cliente_nome", "cliente_email", "status", "total", "criado_em")
	list_filter = ("status",)
	search_fields = ("numero", "cliente_nome", "cliente_email")


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
	list_display = ("id", "pedido", "produto", "quantidade", "preco_unitario", "subtotal")
	search_fields = ("pedido__numero", "produto__nome")