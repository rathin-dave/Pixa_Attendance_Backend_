from pydantic import BaseModel
from typing import List, Optional, Dict

# ---------- LOGIN ----------
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None


# ---------- FACULTY DASHBOARD ----------
class FacultyDashboardRequest(BaseModel):
    date: str

# ---------- FACULTY PROFILE ----------
class FacultyProfileUpdateRequest(BaseModel):
    faculty_name: str
    faculty_contact_number: str
    faculty_email: str
    profile_image: Optional[str] = None


# ---------- ATTENDANCE ----------
class ProcessedAttendanceUpdateRequest(BaseModel):
    attendance_id: str
    student_attendance_updated_data: List[dict]

class ProcessingAttendanceRequest(BaseModel):
    operation: str
    images: List[str]

class ProcessingAttendanceDetailRequest(BaseModel):
    attendance_id: str

class StudentAttendanceStatus(BaseModel):
    student_id: str
    status: str

class ManualAttendanceRequest(BaseModel):
    attendance_id: str
    attendance: List[StudentAttendanceStatus]
    
class ManualAttendanceGetRequest(BaseModel):
    attendance_id: str

class ImageUploadRequest(BaseModel):
    images: List[str]
    attendance_id: str

# ---------- UNSCHEDULED LECTURE ----------
class UnscheduleLectureRequest(BaseModel):
    class_id: str
    roomnumber: str
    status: str
    subject: str
    date: str
    day: str
    timeslot_id: str
