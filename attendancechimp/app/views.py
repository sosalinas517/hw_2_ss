"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction, IntegrityError
from .models import StudentProfile, InstructorProfile
from datetime import datetime
import zoneinfo
import json
import io

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)

CDT = zoneinfo.ZoneInfo("America/Chicago")

def view_time(request):
	now = datetime.now(CDT)
	return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")

# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now(CDT)
    username = request.user.username if request.user.is_authenticated else None
    context = {
        "current_time": now.strftime("%H:%M"),
        "username": username,
    }
    return render(request, 'app/index.html', context)



# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------
@require_GET
def new(request):
    """Render the sign-up form (GET only)."""
    return render(request, 'app/new.html', {})


@csrf_exempt
@require_POST
def createUser(request):
    """Create a User and a student/instructor profile, then sign them in."""
    email = request.POST.get('email', '').strip()
    user_name = request.POST.get('user_name', '').strip()
    password = request.POST.get('password', '')
    is_student_raw = request.POST.get('is_student', '')

    if not (email and user_name and password and is_student_raw):
        return HttpResponseBadRequest("Missing required field")

    is_student = is_student_raw.strip().lower() in ('1', 'true', 'yes', 'on')

    if User.objects.filter(email__iexact=email).exists():
        return HttpResponse("A user with that email already exists", status=409)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=user_name, email=email, password=password
            )
            if is_student:
                StudentProfile.objects.create(user=user)
            else:
                InstructorProfile.objects.create(user=user)
    except IntegrityError:
        return HttpResponse("That user name is already taken", status=409)

    user = authenticate(request, username=user_name, password=password)
    if user is not None:
        login(request, user)

    return HttpResponse("User created and signed in") 
    
# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# HW2 endpoints: time and sum
# ---------------------------------------------------------------------------

def time_view(request):
    """Return the current Central time as plain text, formatted HH:MM."""
    now = datetime.now(CDT)
    return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")


def _to_number(value):
    """Convert a string to int if it's a whole number, otherwise float."""
    try:
        return int(value)
    except ValueError:
        return float(value)


def sum_view(request):
    """Return {"sum": n1 + n2} as JSON, reading n1 and n2 from the query string."""
    try:
        n1 = _to_number(request.GET.get("n1"))
        n2 = _to_number(request.GET.get("n2"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("n1 and n2 must be numbers")
    return HttpResponse(f"<p>{n1 + n2}</p>")
