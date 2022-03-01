from django.contrib import admin
from django.urls import path, include
from accounts import views
from .admin import admin_total_statistics_view, admin_user_statistics_view, admin_user_input_view


urlpatterns = [
    path('admin/statistics/total', admin_total_statistics_view),
    path('admin/statistics/user_input', admin_user_input_view),
    path('admin/statistics/per_user/<int:user_id>', admin_user_statistics_view),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tickets/', include('tickets.urls')),
    path('downloads/', include('downloads.urls')),

    path('', views.redirect_to_accounts),
]
