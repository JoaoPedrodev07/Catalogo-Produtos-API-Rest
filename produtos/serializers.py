from rest_framework import serializers
from .models import Produto, Categoria
        
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']
        
class ProdutoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset = Categoria.objects.all(), source ='categoria', write_only = True
    )
    class Meta:
        model = Produto
        fields = ['id', 'nome','descricao','preco','imagem', 'data_criacao', 'categoria', 'categoria_id']
        
        
        def __str__ (self):
            return self.nome