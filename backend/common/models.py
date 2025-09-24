from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    """Categorias das notícias"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class News(models.Model):
    """Notícias do sistema"""
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Conteúdo")
    summary = models.TextField(max_length=500, blank=True, verbose_name="Resumo")
    source = models.CharField(max_length=100, verbose_name="Fonte")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news', verbose_name="Categoria")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news', verbose_name="Autor")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Publicado em")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """Perfil estendido do usuário"""
    USER_TYPES = (
        ('admin', 'Administrador'),
        ('reader', 'Leitor'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Usuário")
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='reader', verbose_name="Tipo de usuário")
    preferred_categories = models.ManyToManyField(Category, blank=True, related_name='preferred_by', verbose_name="Categorias preferidas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin' or self.user.is_superuser
    
    @property
    def is_reader(self):
        return self.user_type == 'reader'


# Signal para criar automaticamente UserProfile quando um usuário é criado
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um UserProfile quando um novo usuário é criado"""
    if created:
        # Se é superuser, criar como admin, senão como reader
        user_type = 'admin' if instance.is_superuser else 'reader'
        UserProfile.objects.create(user=instance, user_type=user_type)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o UserProfile quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
