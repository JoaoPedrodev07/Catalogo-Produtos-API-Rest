from __future__ import annotations

import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from produtos.models import Categoria, ItemPedido, Pedido, Produto


def _build_s3_image_url(raw_url: str) -> str:
    if not raw_url:
        return ""

    if raw_url.startswith(("http://", "https://")):
        return raw_url

    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
    region = os.getenv("AWS_S3_REGION_NAME", "us-east-1").strip()
    if not bucket_name:
        return raw_url

    image_name = raw_url.rsplit("/", 1)[-1]
    object_key = f"media/product_photos/{image_name}"
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"


class Command(BaseCommand):
    help = "Load the legacy initial_data.json into the current Categoria and Produto models."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before importing.",
        )
        parser.add_argument(
            "--fixture",
            default="initial_data.json",
            help="Path to the legacy JSON fixture file relative to the project root.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = Path(options["fixture"])
        if not fixture_path.is_absolute():
            fixture_path = Path.cwd() / fixture_path

        if not fixture_path.exists():
            raise CommandError(f"Fixture file not found: {fixture_path}")

        with fixture_path.open(encoding="utf-8") as fixture_file:
            raw_items = json.load(fixture_file)

        if options["clear"]:
            # Delete in reverse FK dependency order to avoid ProtectedError:
            # ItemPedido → Pedido → Produto → Categoria
            ItemPedido.objects.all().delete()
            Pedido.objects.all().delete()
            Produto.objects.all().delete()
            Categoria.objects.all().delete()

        categories_by_old_pk: dict[int, Categoria] = {}
        product_count = 0
        category_count = 0

        for item in raw_items:
            model_name = item.get("model", "")
            fields = item.get("fields", {})
            old_pk = item.get("pk")

            if model_name == "produtos.catalogue":
                category, created = Categoria.objects.update_or_create(
                    nome=fields.get("name", f"Categoria {old_pk}"),
                    defaults={},
                )
                categories_by_old_pk[old_pk] = category
                category_count += 1 if created else 0
                continue

            if model_name != "produtos.product":
                continue

            category = categories_by_old_pk.get(fields.get("catalogue"))
            image_url = fields.get("image_url", "") or ""
            https_image_url = _build_s3_image_url(image_url)
            image_name = image_url.rsplit("/", 1)[-1] if image_url else ""
            legacy_image_url = https_image_url or (f"/media/product_photos/{image_name}" if image_name else "")

            especificacoes = {
                "name_en": fields.get("name_en", ""),
                "description_en": fields.get("description_en", ""),
                "brand": fields.get("brand", ""),
                "item_type": fields.get("item_type", ""),
                "price_tier": fields.get("price_tier", ""),
                "featured": fields.get("featured", False),
                "image_url": legacy_image_url,
            }

            produto, _ = Produto.objects.update_or_create(
                nome=fields.get("name", f"Produto {old_pk}"),
                defaults={
                    "descricao": fields.get("description", ""),
                    "preco": fields.get("price", "0.00"),
                    "categoria": category,
                    "estoque": fields.get("stock", 0) or 0,
                    "imagem_legada": legacy_image_url,
                    "especificacoes": especificacoes,
                },
            )
            product_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {category_count or len(Categoria.objects.all())} categories "
            f"and {product_count} products from {fixture_path.name}."
        ))