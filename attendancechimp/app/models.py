"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                            # allows using logger.warning(), logger.error(), 
                                                            # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------
class InstructorProfile(models.Model):
    """An instructor who teaches one or more courses."""
    instructor_id = models.AutoField(null=False, primary_key= True)
    name = models.CharField(max_length = 150, null = False)
    department = models.CharField(max_length = 150)

class StudentProfile(models.Model):
    """A student who can enroll in courses and can upload QR codes."""
    student_id = models.AutoField(null= False, primary_key=True)
    name = models.CharField(null= False, max_length=150)

# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------
class Course(models.Model):
    """A course taught by a singular instructor with a recurring meeting schedule."""
    course_id = models.AutoField(null = False, primary_key=True)
    course_name = models.CharField(max_length=200, null = False)
    instructor_id = models.ForeignKey(InstructorProfile, on_delete = models.CASCADE, related_name="courses")
    meeting_schedule = models.CharField(max_length = 200, null= False)
# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------
class Enrollment(models.Model):
    """Links many students to multiple courses with the enrollment date."""
    student_id = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(null = False)


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
class Lecture(models.Model):
    """A lecture meeting of a course with a date and QR identifier."""
    lecture_id = models.AutoField(primary_key=True, null = False)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lectures")
    lecture_date = models.DateField(null = False)
    qr_identifier = models.CharField(max_length=150, null = False)



# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------
class QRCodeUpload(models.Model):
    """A student's QR code submission, optionally matched to a lecture."""
    upload_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture_id = models.ForeignKey(Lecture, null=True, on_delete=models.SET_NULL)
    qr_identifier = models.CharField(max_length=150, null = False)
    uploaded_at = models.DateTimeField(auto_now_add=True, null = False)


# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------
def get_enrolled_students(course):
    """Return all students enrolled in the given course."""
    return StudentProfile.objects.filter(enrollment__course = course)

def instructor_courses(instructor):
    """Returns all courses an instructor teaches"""
    return InstructorProfile.objects.filter(instructor = instructor)

def get_lecture_attendees(lecture):
    """Return all students who uploaded a QR code for the given lecture."""
    return StudentProfile.objects.filter(qrcodeupload__lecture = lecture).distinct()



