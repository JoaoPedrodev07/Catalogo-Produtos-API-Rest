rom django.db import migrations
import re


def fix_s3_urls(apps, schema_editor):
    Produto = apps.get_model('produtos', 'Produto')

    for produto in Produto.objects.all():
        changed = False

        # Fix imagem_legada field
        if produto.imagem_legada and produto.imagem_legada.startswith('s3://'):
            match = re.match(r's3://([^/]+)/(.+)', produto.imagem_legada)
            if match:
                bucket, key = match.groups()
                region_match = re.search(
                    r'(us-east-1|us-east-2|us-west-1|us-west-2)', bucket
                )
                region = region_match.group(1) if region_match else 'us-east-1'
                produto.imagem_legada = (
                    f'https://{bucket}.s3.{region}.amazonaws.com/{key}'
                )
                changed = True

        # Fix especificacoes["image_url"] field
        if isinstance(produto.especificacoes, dict):
            img_url = produto.especificacoes.get('image_url', '')
            if img_url and img_url.startswith('s3://'):
                match = re.match(r's3://([^/]+)/(.+)', img_url)
                if match:
                    bucket, key = match.groups()
                    region_match = re.search(
                        r'(us-east-1|us-east-2|us-west-1|us-west-2)', bucket
                    )
                    region = region_match.group(1) if region_match else 'us-east-1'
                    produto.especificacoes['image_url'] = (
                        f'https://{bucket}.s3.{region}.amazonaws.com/{key}'
                    )
                    changed = True

        if changed:
            produto.save()


def reverse_fix(apps, schema_editor):
    pass  # intentionally irreversible


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0007_produto_imagem_legada'),
    ]

    operations = [
        migrations.RunPython(fix_s3_urls, reverse_fix),
    ]
