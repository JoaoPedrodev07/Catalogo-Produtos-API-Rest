import random

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Categoria, ItemPedido, Pedido, Produto
from .serializers import CategoriaSerializer, ItemPedidoSerializer, PedidoSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nome")
    serializer_class = CategoriaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.select_related("categoria").all().order_by("nome")
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        categoria_id = params.get("categoria")
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        search = params.get("search")
        if search:
            queryset = queryset.filter(Q(nome__icontains=search) | Q(descricao__icontains=search))

        nome = params.get("nome")
        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        preco_min = params.get("preco_min")
        if preco_min:
            queryset = queryset.filter(preco__gte=preco_min)

        preco_max = params.get("preco_max")
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)

        estoque_min = params.get("estoque_min")
        if estoque_min:
            queryset = queryset.filter(estoque__gte=estoque_min)

        estoque_max = params.get("estoque_max")
        if estoque_max:
            queryset = queryset.filter(estoque__lte=estoque_max)

        marca = params.get("marca")
        if marca:
            queryset = queryset.filter(especificacoes__marca__icontains=marca)

        ordering = params.get("ordering")
        if ordering in {"preco", "-preco", "nome", "-nome", "data_criacao", "-data_criacao"}:
            queryset = queryset.order_by(ordering)

        return queryset


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.prefetch_related("itens").all().order_by("-criado_em")
    serializer_class = PedidoSerializer

    def generate_order_number(self):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        suffix = random.randint(100, 999)
        return f"PED{timestamp}{suffix}"

    def create(self, request, *args, **kwargs):
        cliente_nome = request.data.get("cliente_nome")
        cliente_email = request.data.get("cliente_email")
        itens_data = request.data.get("itens", [])

        if not cliente_nome or not cliente_email:
            return Response(
                {"detail": "Nome e email são obrigatórios para criar um pedido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(itens_data, list) or not itens_data:
            return Response(
                {"detail": "O pedido deve conter pelo menos um item."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pedido = Pedido.objects.create(
            numero=self.generate_order_number(),
            cliente_nome=cliente_nome,
            cliente_email=cliente_email,
            total=0,
        )

        total = 0
        for item_data in itens_data:
            produto_id = item_data.get("produto")
            quantidade = item_data.get("quantidade")

            if not produto_id or not quantidade:
                pedido.delete()
                return Response(
                    {"detail": "Cada item deve incluir produto e quantidade."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                produto = Produto.objects.get(pk=produto_id)
            except Produto.DoesNotExist:
                pedido.delete()
                return Response(
                    {"detail": f"Produto com id {produto_id} não encontrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            item = ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco,
            )
            total += item.subtotal

        pedido.total = total
        pedido.save()

        serializer = self.get_serializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.select_related("pedido", "produto").all().order_by("id")
    serializer_class = ItemPedidoSerializer


def home(request):
    return render(request, "index.html")