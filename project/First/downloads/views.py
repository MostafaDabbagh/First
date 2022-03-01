import os

from django.http import HttpResponse
from django.shortcuts import render
from First.settings import BASE_DIR


def download_test_view(request):
    filename = 'yourvideo.mp4'
    filepath = os.path.join(BASE_DIR, 'media/downloads/myvideo.mp4')
    path = open(filepath, 'rb')
    # mimetype = mimetypes.guess_type(filepath)
    response = HttpResponse(path)
    response['Content-Disposition'] = f"attachment; filename={filename}"
    return response

