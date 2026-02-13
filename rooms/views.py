from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Room, RoomCategory

# Room Views
class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        status = self.request.GET.get('status')
        if category_id:
            queryset = queryset.filter(categorie_id=category_id)
        if status:
            queryset = queryset.filter(statut=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RoomCategory.objects.all()
        context['status_choices'] = Room.STATUS_CHOICES
        context['current_category'] = self.request.GET.get('category')
        context['current_status'] = self.request.GET.get('status')
        return context

class RoomCreateView(CreateView):
    model = Room
    fields = ['numero', 'categorie', 'statut', 'cleaning_status']
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room_list')

class RoomUpdateView(UpdateView):
    model = Room
    fields = ['numero', 'categorie', 'statut', 'cleaning_status']
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room_list')

# RoomCategory Views
class RoomCategoryListView(ListView):
    model = RoomCategory
    template_name = 'rooms/room_category_list.html'
    context_object_name = 'categories'

class RoomCategoryCreateView(CreateView):
    model = RoomCategory
    fields = ['nom', 'prix', 'description']
    template_name = 'rooms/room_category_form.html'
    success_url = reverse_lazy('room_category_list')

class RoomCategoryUpdateView(UpdateView):
    model = RoomCategory
    fields = ['nom', 'prix', 'description']
    template_name = 'rooms/room_category_form.html'
    success_url = reverse_lazy('room_category_list')

class RoomCategoryDeleteView(DeleteView):
    model = RoomCategory
    template_name = 'rooms/room_category_confirm_delete.html'
    success_url = reverse_lazy('room_category_list')

