from schemas import *

def login(req: LoginRequest):
    return {"success": True, "token": "dummy-token"}

def get_faculty_dashboard(token: str):
    return {"message": "faculty dashboard data"}

def post_faculty_dashboard(token: str, req: FacultyDashboardRequest):
    return {"message": "faculty dashboard filtered"}

def get_faculty_profile(token: str):
    return {"message": "faculty profile data"}

def update_faculty_profile(token: str, req: FacultyProfileUpdateRequest):
    return {"success": True}

def get_notifications(token: str):
    return [{"title": "New Lecture", "message": "You have 1 new lecture", "color": "blue"}]

def get_faculty_attendance_record(token: str):
    return {"message": "attendance records"}

def get_completed_attendance_detail(id: str, token: str):
    return {"message": f"completed attendance {id}"}

def get_processed_attendance_detail(id: str, token: str):
    return {"message": f"processed attendance {id}"}

def update_processed_attendance_detail(id: str, token: str, req: ProcessedAttendanceUpdateRequest):
    return {"success": True}

def get_processing_attendance_detail(id: str, token: str):
    return {"message": f"processing attendance {id}"}

def post_processing_attendance_detail(id: str, token: str, req: ProcessingAttendanceRequest):
    return {"success": True}

def get_manual_attendance(id: str, token: str):
    return {"message": f"manual attendance {id}"}

def post_manual_attendance(id: str, token: str, req: ManualAttendanceRequest):
    return {"success": True}

def image_upload_attendance(id: str, token: str, req: ImageUploadRequest):
    return {"success": True}

def get_cctv_attendance(id: str, token: str):
    return {"success": True}

def create_unschedule_lecture(token: str, req: UnscheduleLectureRequest):
    return {"success": True, "attendance_id": "ATT1001"}

def get_unschedule_lecture_data(token: str):
    return {"timeslot": [], "subject": [], "classes": [], "roomnumber": []}
