from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import logging
from .forms import LoginForm, SignUpForm, CustomUserCreationForm, CustomUserChangeForm

logger = logging.getLogger(__name__)

# Função para verificar se a requisição é AJAX
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

# Mixin para tratar a resposta AJAX
class AjaxFormMixin:
    template_name_ajax = None

    def form_invalid(self, form):
        """Se o formulário for inválido, responde com os erros em JSON para AJAX."""
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        """Se o formulário for válido, responde com uma mensagem de sucesso em JSON para AJAX."""
        self.object = form.save()
        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Operação realizada com sucesso!'})
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        """Método GET para tratar requisições AJAX."""
        if is_ajax(request):
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None
            context = self.get_context_data()
            return render(request, self.template_name_ajax or self.template_name, context)
        return super().get(request, *args, **kwargs)

# CBV para login de usuário
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'  # Redireciona para a home após login

    def form_valid(self, form):
        """Valida as credenciais e faz o login do usuário."""
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            # Redireciona para a URL solicitada originalmente ou para o success_url
            next_page = self.request.GET.get('next', self.success_url)
            return redirect(next_page)  # Redireciona para a URL correta
        else:
            messages.error(self.request, 'Credenciais inválidas.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retorna uma mensagem de erro quando o formulário é inválido."""
        messages.error(self.request, 'Erro ao validar o formulário.')
        return super().form_invalid(form)

# CBV para registro de usuário
class RegisterView(FormView):
    form_class = SignUpForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        """Cria o usuário e realiza o login automaticamente após o registro."""
        user = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        messages.success(self.request, 'Usuário criado com sucesso.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Mensagem de erro caso o registro falhe."""
        messages.error(self.request, 'Erro ao registrar usuário.')
        return super().form_invalid(form)

# CBV para listar usuários com paginação e filtragem
class CustomUserListView(AjaxFormMixin, ListView):
    model = get_user_model()
    template_name = 'accounts/lista_usuarios.html'
    partial_template_name = 'accounts/_lista_usuarios.html'
    context_object_name = 'accounts'
    paginate_by = 10

    def get_queryset(self):
        """Filtra e pagina a lista de usuários com base nos parâmetros passados."""
        queryset = get_user_model().objects.all().order_by('-date_joined')
        nome = self.request.GET.get('nome', '')
        email = self.request.GET.get('email', '')
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if email:
            queryset = queryset.filter(email__icontains=email)
        return queryset

# CBV para criar um novo usuário
class CustomUserCreateView(AjaxFormMixin, CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'accounts/form_usuario.html'
    success_url = reverse_lazy('accounts:lista_usuarios')

    @transaction.atomic
    def form_valid(self, form):
        """Cria um novo usuário e retorna um sucesso em caso de formulário válido."""
        response = super().form_valid(form)
        messages.success(self.request, 'Usuário criado com sucesso!')
        return response

# CBV para detalhamento de um usuário específico
class CustomUserDetailView(DetailView):
    model = get_user_model()
    template_name = 'accounts/detalhes_usuario_modal.html'
    context_object_name = 'accounts'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Busca o usuário utilizando o slug."""
        return get_object_or_404(get_user_model(), slug=self.kwargs.get(self.slug_url_kwarg))

    def get(self, request, *args, **kwargs):
        """Exibe o detalhe do usuário no formato de modal com AJAX."""
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

# CBV para atualizar um usuário existente
class CustomUserUpdateView(AjaxFormMixin, UpdateView):
    model = get_user_model()
    form_class = CustomUserChangeForm
    template_name = 'accounts/form_usuario.html'
    success_url = reverse_lazy('accounts:lista_usuarios')
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Busca o usuário pelo slug para edição."""
        return get_object_or_404(get_user_model(), slug=self.kwargs.get(self.slug_url_kwarg))

    @transaction.atomic
    def form_valid(self, form):
        """Atualiza o usuário e exibe uma mensagem de sucesso."""
        response = super().form_valid(form)
        if is_ajax(self.request):
            return JsonResponse({'success': True, 'message': 'Usuário atualizado com sucesso!'})
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return response

# CBV para excluir um usuário
class CustomUserDeleteView(DeleteView):
    model = get_user_model()
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('accounts:lista_usuarios')
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Busca o usuário pelo slug antes de deletá-lo."""
        return get_object_or_404(get_user_model(), slug=self.kwargs.get(self.slug_url_kwarg))

    def post(self, request, *args, **kwargs):
        """Deleta o usuário e responde com JSON em caso de requisição AJAX."""
        self.object = self.get_object()
        email = self.object.email
        try:
            self.object.delete()
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': f'Usuário "{email}" excluído com sucesso!'})
            messages.success(request, f'Usuário "{email}" excluído com sucesso!')
            return redirect(self.success_url)
        except Exception as e:
            logger.error(f"Erro ao excluir usuário {email}: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Erro ao excluir o usuário.'})

# CBV para logout de usuário
class LogoutView(FormView):
    """View para realizar o logout e redirecionar para a home ou outra página."""
    def get(self, request, *args, **kwargs):
        logout(request)  # Realiza o logout
        messages.success(request, 'Você foi desconectado com sucesso.')
        return redirect('/')  # Redireciona para a home ou página desejada