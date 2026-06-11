from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    especificacoes = models.JSONField(default=dict, blank=True)
    imagem_legada = models.CharField(max_length=255, blank=True, default="")
    data_criacao = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produtos",
    )

    def __str__(self):
        return self.nome

    @property
    def imagem_origem(self):
        if self.imagem:
            return self.imagem.url
        if self.imagem_legada:
            return self.imagem_legada
        if isinstance(self.especificacoes, dict):
            return self.especificacoes.get("image_url") or self.especificacoes.get("imagem")
        return None


class Pedido(models.Model):
    STATUS_PENDENTE = "pendente"
    STATUS_CONFIRMADO = "confirmado"
    STATUS_ENVIADO = "enviado"
    STATUS_ENTREGUE = "entregue"
    STATUS_CANCELADO = "cancelado"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_CONFIRMADO, "Confirmado"),
        (STATUS_ENVIADO, "Enviado"),
        (STATUS_ENTREGUE, "Entregue"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    numero = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    cliente_nome = models.CharField(max_length=255)
    cliente_email = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.numero}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="itens_pedido")
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
     




