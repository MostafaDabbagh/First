from django.urls import path
from tickets import views

urlpatterns = [
    path('create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('details/<int:ticket_id>/', views.TicketDetailsView.as_view(), name='ticket_details'),
    path('delete/<int:ticket_id>/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    path('update/<int:ticket_id>/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('file_delete/<int:ticket_id>/', views.TicketFileDeleteView.as_view(), name='ticket_file_delete'),
]
