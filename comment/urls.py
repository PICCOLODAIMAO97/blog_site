from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    path('updatecomment/', views.update_comment, name='update_comment'),

]