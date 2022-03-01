import os.path
from django.urls import reverse

from django.shortcuts import render, redirect
from django.views import View
from .forms import TicketCreateUpdateForm
from . import models
from .models import user_can_ticket
from ipware import get_client_ip
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from threading import Thread
from django.core.files.storage import FileSystemStorage
from First.settings import MEDIA_ROOT


class TicketCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if not user_can_ticket(request.user):
            messages.warning(request,
                             f'You cannot send more than {models.Ticket.TICKET_PER_HOUR_LIMIT} tickets per hour')
            return redirect('user_profile')
        form = TicketCreateUpdateForm()
        return render(request, 'tickets/create.html', {'form': form})

    def post(self, request):
        form = TicketCreateUpdateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ticket = models.Ticket(
                user_id=request.user.id,
                text=cd['text'],
                ip=get_client_ip(request)[0],
                browser=request.user_agent.browser.family
            )
            ticket.insert()
            # cache
            cache.delete('chars_per_user_chart_data')
            if request.FILES.get('file'):
                ticket_id = models.Ticket.get_last_ticket_id()
                file = models.File(ticket_id=ticket_id, filename=f"({ticket_id})-{request.FILES['file'].name}")
                file.insert()
                fss = FileSystemStorage(os.path.join(MEDIA_ROOT, 'uploaded_files'))
                fss.save(file.filename, request.FILES.get('file'))

            thread = Thread(target=ticket.send_email)
            thread.start()

            messages.success(request, 'Ticket created successfully')
            return redirect('user_profile')
        return render(request, 'tickets/create.html', {'form': form})


class TicketDetailsView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = models.Ticket.get(ticket_id)
        context = {'ticket': ticket}
        if ticket.has_file():
            context['file'] = models.File.get(ticket_id)
        if ticket.user_id == request.user.id:
            return render(request, 'tickets/details.html', context)
        else:
            messages.error(request, 'No such ticket in your tickets')
        return redirect('user_profile')


class TicketDeleteView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = models.Ticket.get(ticket_id)
        if ticket.user_id == request.user.id:
            if ticket.has_file():
                file = models.File.get(ticket.id)
                fss = FileSystemStorage(os.path.join(MEDIA_ROOT, 'uploaded_files'))
                fss.delete(file.filename)
                file.remove()
            ticket.remove()
            # cache
            cache.delete('chars_per_user_chart_data')
            messages.success(request, 'Ticket deleted successfully')
        else:
            messages.error(request, 'You cannot delete this ticket')
        return redirect('user_profile')


class TicketUpdateView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.ticket_instance = models.Ticket.get(kwargs['ticket_id'])
        if self.ticket_instance.has_file():
            self.file_instance = models.File.get(self.ticket_instance.id)
        else:
            self.file_instance = None
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        ticket = self.ticket_instance
        if not request.user.id == ticket.user_id:
            return redirect('user_profile')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ticket = self.ticket_instance
        form = TicketCreateUpdateForm(initial={'text': ticket.text})
        return render(request, 'tickets/update.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = TicketCreateUpdateForm(request.POST)
        ticket = self.ticket_instance
        file = self.file_instance
        if form.is_valid():
            cd = form.cleaned_data
            ticket.text = cd['text']
            ticket.update()
            # cache
            cache.delete('chars_per_user_chart_data')
            fss = FileSystemStorage(os.path.join(MEDIA_ROOT, 'uploaded_files'))
            if request.FILES.get('file'):
                if file:
                    fss.delete(file.filename)
                    file.filename = f"({file.ticket_id})-{request.FILES['file'].name}"
                    fss.save(file.filename, request.FILES.get('file'))
                    file.update()
                else:
                    file = models.File(ticket_id=ticket.id, filename=f"({ticket.id})-{request.FILES['file'].name}")
                    file.insert()
                    fss.save(file.filename, request.FILES.get('file'))
            messages.success(request, 'Ticket edited successfully')
        return redirect('ticket_details', ticket.id)


class TicketFileDeleteView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = models.Ticket.get(ticket_id)
        file = models.File.get(ticket_id)
        if ticket.user_id == request.user.id:
            fss = FileSystemStorage(os.path.join(MEDIA_ROOT, 'uploaded_files'))
            fss.delete(file.filename)
            file.remove()
            return redirect(reverse('ticket_details', args=[ticket_id]))
