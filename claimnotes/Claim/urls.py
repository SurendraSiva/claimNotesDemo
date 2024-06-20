from django.urls import path
#now import the views.py file into this code
from . import views
urlpatterns=[
  path('',views.model_form_upload,name='upload_file'),
  path('save-table-data/', views.save_table_data, name='save_table_data')
]