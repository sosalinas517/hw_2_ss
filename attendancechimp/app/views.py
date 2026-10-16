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

    context = {}
    return render(request, 'app/index.html', context)



# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------



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
