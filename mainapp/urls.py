from django.urls import path
from .views import plot_view,main,file_list,upload_file,run_spider,run_parser

urlpatterns = [
    path('',main,name='main'),
    path('files/', file_list, name='file_list'),
    path('files/<str:filename>/plot/', plot_view, name='plot_view'),
    path('upload/', upload_file, name='upload_file'),
    path('run_spider/',run_spider,name='run_spider'),
    path('run_parser/',run_parser,name='run_parser'),
]