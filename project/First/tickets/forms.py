from django import forms


class TicketCreateUpdateForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    file = forms.FileField(required=False)
