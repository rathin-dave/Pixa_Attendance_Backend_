from pydantic import BaseModel
from typing import List, Optional

# ---------- LOGIN ----------
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

# ---------- FACULTY DASHBOARD ----------
class FacultyDashboardRequest(BaseModel):
    date: str

# ---------- FACULTY PROFILE ----------
class FacultyProfileUpdateRequest(BaseModel):
    faculty_name: str
    faculty_contact_number: str
    faculty_email: str
    password: str

# ---------- ATTENDANCE ----------
class ProcessedAttendanceUpdateRequest(BaseModel):
    attendance_id: str
    student_attendance_updated_data: List[dict]

class ProcessingAttendanceRequest(BaseModel):
    operation: str
    images: List[str]

class ManualAttendanceRequest(BaseModel):
    student_attendance_updated_data: List[dict]

class ImageUploadRequest(BaseModel):
    images: List[str]

# ---------- UNSCHEDULED LECTURE ----------
class UnscheduleLectureRequest(BaseModel):
    class_id: str
    roomnumber: str
    status: str
    subject: str
    date: str
    day: str
    timeslot_id: str
