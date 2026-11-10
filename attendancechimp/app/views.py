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
from .models import Course, Lecture, QRCodeUpload, StudentProfile, InstructorProfile
from datetime import datetime
import zoneinfo
import json
import io
import random
import string

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)
def is_instructor(user):
    return user.is_authenticated and hasattr(user, "instructorprofile")

def is_student(user):
    return user.is_authenticated and hasattr(user, "studentprofile")

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
@csrf_exempt
def createCourse(request):
    if not is_instructor(request.user):
        return HttpResponse(status=401)
    if request.method != "POST":
        return HttpResponse(status=405)

    day_keys = [("day-mon", "Mon"), ("day-tue", "Tue"), ("day-wed", "Wed"),
                ("day-thu", "Thu"), ("day-fri", "Fri")]
    days = [label for key, label in day_keys if key in request.POST]
    if not days:
        return HttpResponseBadRequest("Select at least one day")

    name = request.POST["course-name"]
    if Course.objects.filter(course_name=name).exists():
        return HttpResponse("Course name already exists", status=409)

    schedule = (f"{','.join(days)} "
                f"{request.POST['start-time']}-{request.POST['end-time']}")
    Course.objects.create(
        course_name=name,
        instructor_id=request.user.instructorprofile,
        meeting_schedule=schedule,
    )
    return HttpResponse(status=200)


@csrf_exempt
def createLecture(request):
    if not is_instructor(request.user):
        return HttpResponse(status=401)
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        course = Course.objects.get(course_name=request.POST.get("choice"))
    except Course.DoesNotExist:
        return HttpResponseBadRequest("No such course")

    Lecture.objects.create(
        course_id=course,
        lecture_date=datetime.now(CDT).date(),
        qr_identifier="".join(random.choices(string.ascii_letters + string.digits, k=20)),
    )
    return HttpResponse(status=200)


@csrf_exempt
def createQRCodeUpload(request):
    if not is_student(request.user):
        return HttpResponse(status=401)
    if request.method != "POST":
        return HttpResponse(status=405)

    image = request.FILES.get("imageUpload")
    if image is None:
        return HttpResponseBadRequest("Missing imageUpload")

    QRCodeUpload.objects.create(
        student_id=request.user.studentprofile,
        image=image,
        qr_identifier="",   # not decoded in HW5; uploaded_at fills itself in
    )
    return HttpResponse(status=200)


def dumpUploads(request):
    if not is_instructor(request.user):
        return HttpResponse(status=401)
    if request.method != "GET":
        return HttpResponse(status=405)

    uploads = QRCodeUpload.objects.select_related("student_id__user")
    data = [
        {
            "username": u.student_id.user.username,
            "upload_time": u.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for u in uploads
    ]
    return JsonResponse(data, safe=False)

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

def new_course(request):
    return render(request, "app/new_course.html")

def new_lecture(request):
    courses = Course.objects.all()
    return render(request, "app/new_lecture.html", {"courses": courses})

def new_qr_upload(request):
    return render(request, "app/new_qr_upload.html")