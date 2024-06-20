from django.db import models

# Create your models here.
class Document(models.Model):
    document=models.FileField(upload_to='documents/')
    question=models.FileField(upload_to='documents/',blank=True,null=True)
class Prompts(models.Model):
    ml=5000
    Variable=models.TextField(max_length=ml)
    Question_head=models.TextField(max_length=ml)
    Entity_context=models.TextField(max_length=ml)
    Document_type=models.TextField(max_length=ml,default='none')
    Output_format=models.TextField(max_length=ml)
    Gpt_instruction=models.TextField(max_length=ml)
    Final_prompt=models.TextField(max_length=ml)

        