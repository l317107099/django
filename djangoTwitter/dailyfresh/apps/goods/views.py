from django.shortcuts import render,redirect
from django.urls import reverse

# Create your views here.

def index(request):
    return render(request,'index.html')


    # render (request,redirect(reverse('goods:index')))