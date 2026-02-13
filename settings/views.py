from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser, Role, Permission, AppSettings
from django import forms

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserListView(ListView):
    model = CustomUser
    template_name = 'settings/users_list.html'
    context_object_name = 'users'

class UserCreateView(CreateView):
    model = CustomUser
    form_class = UserForm
    template_name = 'settings/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        if form.cleaned_data.get('password'):
            user.set_password(form.cleaned_data['password'])
        else:
            user.set_password('changeme123')  # Default password
        user.save()
        return super().form_valid(form)

class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UserForm
    template_name = 'settings/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        if form.cleaned_data.get('password'):
            user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

def roles_permissions_view(request):
    """View for managing roles and permissions"""
    roles = Role.objects.prefetch_related('permissions').all()
    
    if request.method == 'POST':
        # Handle role creation or permission updates
        pass
    
    context = {
        'roles': roles,
        'modules': Permission.MODULE_CHOICES,
        'actions': Permission.ACTION_CHOICES,
    }
    return render(request, 'settings/roles_permissions.html', context)

def branding_view(request):
    """View for customizing app appearance"""
    settings_obj = AppSettings.load()
    
    if request.method == 'POST':
        settings_obj.hotel_name = request.POST.get('hotel_name', settings_obj.hotel_name)
        settings_obj.primary_color = request.POST.get('primary_color', settings_obj.primary_color)
        settings_obj.sidebar_color = request.POST.get('sidebar_color', settings_obj.sidebar_color)
        
        if request.FILES.get('logo'):
            settings_obj.logo = request.FILES['logo']
        if request.FILES.get('favicon'):
            settings_obj.favicon = request.FILES['favicon']
        
        settings_obj.save()
        messages.success(request, 'Paramètres de personnalisation enregistrés avec succès! Rafraîchissez la page (F5) pour voir les changements.')
        return redirect('branding')
    
    return render(request, 'settings/branding.html', {'settings': settings_obj})

def general_settings_view(request):
    """View for general app settings"""
    settings_obj = AppSettings.load()
    
    if request.method == 'POST':
        settings_obj.hotel_name = request.POST.get('hotel_name', settings_obj.hotel_name)
        settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email)
        settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone)
        settings_obj.address = request.POST.get('address', settings_obj.address)
        settings_obj.currency = request.POST.get('currency', settings_obj.currency)
        settings_obj.timezone = request.POST.get('timezone', settings_obj.timezone)
        settings_obj.save()
        messages.success(request, 'Paramètres généraux enregistrés avec succès!')
        return redirect('general_settings')
    
    return render(request, 'settings/general.html', {'settings': settings_obj})
