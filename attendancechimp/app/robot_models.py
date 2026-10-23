
# Created by ChatGPT
# models.py
# Specifications:
# - Separate InstructorProfile and StudentProfile tables instead of one Users table
# - Course table with name, instructor, and meeting schedule
# - Enrollment table linking students and courses (many-to-many)
# - Lecture table linked to a course, with a date and QR identifier
# - QRCodeUpload table linked to a student and optionally a lecture

import uuid

from django.conf import settings
from django.db import models


# Specification: InstructorProfile table
# Stores instructor-specific information separately from student information.
# Each profile is linked one-to-one with a Django User account.
class InstructorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Specification: StudentProfile table
# Stores student-specific information separately from instructor information.
# A separate profile structure allows each role to have different fields.
class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    student_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Specification: Course table
# Each course has a name, an instructor, and a meeting schedule.
# The ForeignKey links each course to one instructor.
# An instructor can teach multiple courses.
class Course(models.Model):
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    meeting_schedule = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Specification: Enrollment table
# Connects students to courses through a many-to-many relationship.
# A student can enroll in multiple courses, and each course can have
# multiple students.
# The unique constraint prevents a student from enrolling in the
# same course more than once.
class Enrollment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"


# Specification: Lecture table
# Each lecture belongs to one course and stores its date.
# The UUID serves as a unique QR identifier for the lecture.
# A UUID helps avoid predictable, sequential QR identifiers.
class Lecture(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures",
    )
    date = models.DateField()
    qr_identifier = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    def __str__(self):
        return f"{self.course.name} - {self.date}"


# Specification: QRCodeUpload table
# Each upload is linked to a student.
# The lecture relationship is optional (null=True, blank=True),
# allowing an upload to exist before its lecture is identified.
# uploaded_at records when the upload was created.
class QRCodeUpload(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="qr_uploads",
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_uploads",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.uploaded_at}"
