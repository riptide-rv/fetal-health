from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, UserLoginForm
from .models import UserProfile, WeekData, PatientData
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from ml.final import predict_fetal_health
from django.urls import reverse
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
import uuid


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

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    data = json.loads(request.body)
    username = data.get('username', '')
    password = data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid username or password.'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def signin(request):
    data = json.loads(request.body)
    username = data.get('username', '')
    password = data.get('password', '')
    phone_number = data.get('phNo', '')
    hospital = data.get('hospitalName', '')
    specialization = data.get('specialisation', '')
    email = data.get('email', '')   
    city = data.get('city', '')
    # Create User object
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

            # Create UserProfile object
    UserProfile.objects.create(user=user, phone_number=phone_number, hospital=hospital, specialization=specialization, city=city)
    if user is not None:
        login_view(request)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid username or password.'}, status=400)

@require_http_methods(["POST"])
def process_integers(request):
    try:
        data = json.loads(request.body)
        integers = data.get('integers', [])
        weekName = data.get('weekName', '')
        if not isinstance(integers, list):
            return JsonResponse({'error': 'Invalid data format. Expected a list of integers.'}, status=400)
        
        result = predict_fetal_health(integers)
   
        WeekData.objects.create(username=request.user.username, week_name=weekName, numbers=integers,abnormality=result)
        userprofile = UserProfile.objects.filter(user=request.user)[0]

        print(userprofile.specialization)
        
        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@require_http_methods(["POST"])
def add_patient(request):
    data = json.loads(request.body)
    patientname = data.get('patientname', '')
    doctorname = request.user.username
    age = data.get('age', '')
    relevantinfo = data.get('relevantinfo', '')
    uuid = str(uuid.uuid4())
    PatientData.objects.create(patientname=patientname, doctorname=doctorname, age=age, relevantinfo=relevantinfo, uuid=uuid)
    return JsonResponse({'success': True})
    

def patient_view(request):
    weekdatas = WeekData.objects.filter(username=request.user.username)
    weekdatas_json = serialize('json', weekdatas)
    context = {
        'range': range(1, 23),
        'process_integers_url': reverse('process_integers'),
        'user' : request.user,
        'weekdatas': weekdatas_json
        }
    return render(request, 'patients.html', context)

def signup_view(request):
   
    context = {
        'range': signup
        }
    return render(request, 'signup.html', context)


def login_view(request):
    context = {
        'range': 'login'
    }
    return render(request, 'login.html', context)

def doctor_view(request):
    patientdatas = PatientData.objects.filter(doctorname=request.user.username)
    patientdatas_json = serialize('json', patientdatas)
    userdata = UserProfile.objects.filter(user=request.user)[0]
    print(userdata)
    context = {
        'userdata' : userdata,
        'patientdatas': patientdatas_json,
    }
    return render(request, 'doctor.html', context)

def addpatient_view(request):
    context = {
        'range': 'addpatient'
    }
    return render(request, 'addpatient.html', context)