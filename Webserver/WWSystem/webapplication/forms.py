from django import forms
from .models import Upload

class UploadForm(forms.Form):
    class Meta:
        model = Upload
        fields = ('titel', 'file')