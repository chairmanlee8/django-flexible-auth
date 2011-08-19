from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout

def login_django(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    to = request.POST.get('redirect', '/')
    
    user = authenticate(username=username, password=password)
    
    if user is not None and user.is_active:
        login(request, user)
        
    return redirect(to)

def logout_django(request):
    logout(request)
    return redirect('/')