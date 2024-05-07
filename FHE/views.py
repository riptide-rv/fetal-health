from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, UserLoginForm
from .models import UserProfile, WeekData
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from ml.final import predict_fetal_health
from django.urls import reverse

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Handle invalid login
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password.'})
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    context = {}
    if request.user.is_authenticated:
        context['is_logged_in'] = True
    else:
        context['is_logged_in'] = False
    return render(request, 'home.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            hospital = form.cleaned_data['hospital']
            specialization = form.cleaned_data['specialization']
            city = form.cleaned_data['city']
            password = form.cleaned_data['password']

            # Create User object
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Create UserProfile object
            UserProfile.objects.create(user=user, phone_number=phone_number, hospital=hospital, specialization=specialization, city=city)

            return redirect('signup_success')  # Redirect to success page
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def signup_success(request):
    return render(request, 'signup_success.html')

@require_http_methods(["POST"])
def process_integers(request):
    try:
        data = json.loads(request.body)
        integers = data.get('integers', [])
        weekName = data.get('weekName', '')
        if not isinstance(integers, list):
            return JsonResponse({'error': 'Invalid data format. Expected a list of integers.'}, status=400)
        
        result = predict_fetal_health(integers)
       # WeekData.objects.create(user=request.user.username, week_name=weekName, week_data=integers, week_abnormality=result)
        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

def input_form_view(request):
    
    context = {
        'range': range(1, 23),
        'process_integers_url': reverse('process_integers'),
        'user' : request.user,
        'weekdatas': ""
        }
    return render(request, 'patients.html', context)
