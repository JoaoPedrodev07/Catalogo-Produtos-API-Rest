from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ItemPedidoViewSet, PedidoViewSet, ProdutoViewSet



router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'itens-pedido', ItemPedidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
