from django import forms
from .models import Document, Prompts

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', 'question')

class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompts
        fields = ('Variable', 'Question_head', 'Entity_context', 'Document_type', 'Output_format', 'Gpt_instruction', 'Final_prompt')
