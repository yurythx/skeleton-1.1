from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class Projeto(models.Model):
    TIPO_CHOICES = [
        ('interno', 'Interno'),
        ('externo', 'Externo'),
    ]

    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('pausado', 'Pausado'),
    ]

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='interno')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='em_andamento')
  

    def clean(self):
        if Projeto.objects.exclude(id=self.id).filter(titulo=self.titulo).exists():
            raise ValidationError("Já existe um projeto com esse título.")
        if Projeto.objects.exclude(id=self.id).filter(slug=self.slug).exists():
            raise ValidationError("Já existe um projeto com esse slug.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.titulo} ({self.get_status_display()})'


class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    projeto = models.ForeignKey(Projeto, related_name='tarefas', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    responsavel = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    

    def clean(self):
        if len(self.titulo.strip()) < 3:
            raise ValidationError("O título da tarefa deve ter pelo menos 3 caracteres.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.titulo} | Status: {self.get_status_display()} | '
            f'Prioridade: {self.get_prioridade_display()}'
        )


class HistoricoTarefa(models.Model):
    tarefa = models.ForeignKey(Tarefa, related_name='historicos', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.TextField()

    def __str__(self):
        return f'Histórico de "{self.tarefa.titulo}" por {self.usuario.username}'


class ComentarioTarefa(models.Model):
    tarefa = models.ForeignKey(Tarefa, related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()

    def __str__(self):
        return f'Comentário de {self.usuario.username} sobre "{self.tarefa.titulo}"'
