from django.db import models

# Create your models here.

class Categoria (models.Model):
    nome = models.CharField(max_length = 20 , unique = True)
    def __str__(self):
        return self.nome
class Produto(models.Model):
     
     nome = models.CharField(max_length = 100)
     descricao = models.TextField(max_length = 500)   
     preco = models.DecimalField(max_digits = 10, decimal_places = 2)
     imagem = models.ImageField(upload_to ='produtos', blank = True, null = True)
     data_criacao = models.DateTimeField(auto_now_add = True)
     categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null = True, blank = True)
  
     def __str__ (self):
         return self.nome
     
     
     
     