from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone

class Motorista(models.Model):
    """Modelo para cadastro de motoristas."""
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    cnh = models.CharField(max_length=20, unique=True)
    data_validade_cnh = models.DateField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField()
    veiculo = models.ForeignKey('veiculos.Veiculo', on_delete=models.SET_NULL, null=True, blank=True, related_name='motoristas')
    slug = models.SlugField(unique=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['cnh']),
            models.Index(fields=['data_validade_cnh']),
        ]

    def __str__(self):
        return f"{self.nome} - {self.cnh}"

    def clean(self):
        # Validação personalizada
        if not self.cnh:
            raise ValidationError({'cnh': 'O número da CNH não pode estar vazio.'})
        
        # Validação da data de validade da CNH
        if self.data_validade_cnh < timezone.now().date():
            raise ValidationError({'data_validade_cnh': 'A CNH está vencida!'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.nome}-{self.cnh}")
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