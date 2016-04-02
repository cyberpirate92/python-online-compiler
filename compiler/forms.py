from django import forms
from django.forms import Form

languages = [(1,"python")]
languages = [(1,"python")]

class CodeExecutorForm(Form):
    has_template = forms.BooleanField(required=False,label='Enable Template?')
    template = forms.CharField(widget=forms.Textarea,label='Template')
    code = forms.CharField(widget=forms.Textarea,label='Code')
    input = forms.CharField(widget=forms.Textarea,label='Input')
    output = forms.CharField(widget=forms.Textarea,label='Output')
    language=forms.ChoiceField(choices=languages,label='Language')
