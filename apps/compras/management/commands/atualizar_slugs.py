from django.core.management.base import BaseCommand
from apps.compras.models import Compra
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Atualiza os slugs das compras existentes'

    def handle(self, *args, **options):
        compras = Compra.objects.all()
        total = compras.count()
        atualizadas = 0

        self.stdout.write(f'Iniciando atualização de {total} compras...')

        for compra in compras:
            if not compra.slug:
                compra.slug = slugify(f"compra-{compra.id}-{compra.produto.nome}-{compra.fornecedor.nome}")
                compra.save(update_fields=['slug'])
                atualizadas += 1
                self.stdout.write(f'Compra {compra.id} atualizada com slug: {compra.slug}')

        self.stdout.write(self.style.SUCCESS(f'Processo concluído! {atualizadas} compras foram atualizadas.')) 