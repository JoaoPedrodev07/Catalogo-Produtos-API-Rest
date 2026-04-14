from django.shortcuts import render
from rest_framework import viewsets
from .models import Produto,Categoria
from .serializers import ProdutoSerializer, CategoriaSerializer

# Create your views here.

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.select_related('categoria').all()
    serializer_class = ProdutoSerializer
    
    
    
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


def home(request):
    return render(request, 'index.html')