from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import path
from tickets.models import all_tickets_per_day, chars_per_user, user_tickets_per_day, most_used_words
from django import forms
from django.core.cache import cache


class UserInputForm(forms.Form):
    user_id = forms.CharField(max_length=100)


@staff_member_required
def admin_total_statistics_view(request):
    ticket_per_day_chart_data = all_tickets_per_day()
    if cache.get('chars_per_user_chart_data'):
        chars_per_user_chart_data = cache.get('chars_per_user_chart_data')
    else:
        chars_per_user_chart_data = chars_per_user()
        cache.set('chars_per_user_chart_data', chars_per_user_chart_data)
    return render(request, 'admin/total_statistics.html', {
        'title': 'Statistics',
        'tickets_labels': list(ticket_per_day_chart_data[0]),
        'tickets_data': list(ticket_per_day_chart_data[1]),
        'chars_labels': list(chars_per_user_chart_data.keys()),
        'chars_data': list(chars_per_user_chart_data.values()),
    })


@staff_member_required
def admin_user_input_view(request):
    if request.method == 'GET':
        form = UserInputForm()
        return render(request, 'admin/user_input.html', {'form': form})
    elif request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user_id = cd['user_id']
            return redirect(f'/admin/statistics/per_user/{user_id}')


@staff_member_required
def admin_user_statistics_view(request, user_id):
    user_ticket_per_day_chart_data = user_tickets_per_day(user_id)
    most_used_words_data = most_used_words(user_id)
    print(most_used_words_data)
    return render(request, 'admin/user_statistics.html', {
        'title': 'Statistics',
        'tickets_labels': list(user_ticket_per_day_chart_data[0]),
        'tickets_data': list(user_ticket_per_day_chart_data[1]),
        'most_used_words': most_used_words_data,
    })


class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_list += [
            {
                'name': 'Statistics',
                'app_label': 'statistics_app',
                'models': [
                    {
                        'name': 'Total',
                        'object_name': 'total',
                        'admin_url': '/admin/statistics/total',
                        'view_only': True,
                    },
                    {
                        'name': 'Per User',
                        'object_name': 'per_user',
                        'admin_url': '/admin/statistics/user_input',
                        'view_only': True,
                    }
                ],
            }
        ]
        return app_list

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path('admin/statistics/total', admin_total_statistics_view),
            path('admin/statistics/user_input', admin_user_input_view),
            path('admin/statistics/per_user/<int:user_id>', admin_user_statistics_view),
        ]
        return urls
