from django import forms

class JSONFileForm(forms.Form):
    file = forms.FileField(label="Upload your ZIP file")
