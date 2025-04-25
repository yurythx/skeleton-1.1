from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone

class Veiculo(models.Model):
    """Modelo representando um veículo para cadastro."""

    TIPO_CHOICES = [
        ('carro', 'Carro'),
        ('moto', 'Moto'),
        ('caminhao', 'Caminhão'),
        ('outro', 'Outro'),
    ]

    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()
    placa = models.CharField(max_length=10, unique=True)
    cor = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='carro')
    chassi = models.CharField(max_length=50, unique=True)
    renavam = models.CharField(max_length=20, unique=True)
    observacoes = models.TextField(blank=True, null=True)

    slug = models.SlugField(unique=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['marca', 'modelo', 'ano']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['placa']),
        ]

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

    def clean(self):
        # Validações personalizadas
        ano_atual = timezone.now().year
        if self.ano < 1900 or self.ano > ano_atual + 1:
            raise ValidationError({'ano': f"Ano do veículo deve estar entre 1900 e {ano_atual + 1}."})

        if len(self.placa) < 7:
            raise ValidationError({'placa': "A placa deve conter pelo menos 7 caracteres."})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.marca}-{self.modelo}-{self.placa}")
            slug = base_slug
            counter = 1
            while Veiculo.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('veiculo_detail', kwargs={'slug': self.slug})