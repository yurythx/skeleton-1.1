from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone

class Motorista(models.Model):
    """Modelo representando um motorista para cadastro."""

    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)  # Formato: XXX.XXX.XXX-XX
    cnh = models.CharField(max_length=20, unique=True)  # Número da CNH
    data_validade_cnh = models.DateField()  # Data de validade da CNH
    endereco = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Formato: (XX) XXXXX-XXXX
    email = models.EmailField(blank=True, null=True)

    # Alteração para usar 'veiculos.Veiculo' como referência do modelo 'Veiculo'
    veiculo = models.ForeignKey('veiculos.Veiculo', on_delete=models.SET_NULL, null=True, blank=True, related_name='motoristas')

    slug = models.SlugField(unique=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['cpf']),
        ]

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    def clean(self):
        # Validação personalizada
        if not self.cnh:
            raise ValidationError({'cnh': 'O número da CNH não pode estar vazio.'})
        
        # Validação da data de validade da CNH
        if self.data_validade_cnh < timezone.now().date():
            raise ValidationError({'data_validade_cnh': 'A CNH está vencida!'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.nome}-{self.cpf}")
            slug = base_slug
            counter = 1
            while Motorista.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('motorista_detail', kwargs={'slug': self.slug})