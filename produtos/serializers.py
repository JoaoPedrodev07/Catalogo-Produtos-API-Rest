from rest_framework import serializers

from .models import Categoria, ItemPedido, Pedido, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome"]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source="categoria", write_only=True, required=False, allow_null=True
    )
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "descricao",
            "preco",
            "estoque",
            "imagem",
            "imagem_legada",
            "imagem_url",
            "especificacoes",
            "data_criacao",
            "categoria_nome",
            "categoria_id",
        ]

    def get_imagem_url(self, obj):
        request = self.context.get("request")
        url = obj.imagem_origem
        if not url:
            return None
        if url.startswith(("http://", "https://", "s3://")):
            return url
        if request:
            return request.build_absolute_uri(url)
        return url


class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)

    class Meta:
        model = ItemPedido
        fields = ["id", "pedido", "produto", "produto_nome", "quantidade", "preco_unitario", "subtotal"]


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ["id", "numero", "status", "cliente_nome", "cliente_email", "total", "itens", "criado_em", "atualizado_em"]