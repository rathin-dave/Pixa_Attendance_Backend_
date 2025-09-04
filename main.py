from fastapi import FastAPI, Depends
from schemas import *
import services

app = FastAPI()

# ----------------- LOGIN -----------------
@app.post("/login")
def login(req: LoginRequest):
    return services.login(req)

# ----------------- FACULTY DASHBOARD -----------------
@app.get("/faculty_dashboard")
def get_faculty_dashboard(token: str):
    return services.get_faculty_dashboard(token)

@app.post("/faculty_dashboard")
def post_faculty_dashboard(req: FacultyDashboardRequest, token: str):
    return services.post_faculty_dashboard(token, req)

# ----------------- FACULTY PROFILE -----------------
@app.get("/faculty_profile")
def get_faculty_profile(token: str):
    return services.get_faculty_profile(token)

@app.put("/faculty_profile")
def update_faculty_profile(req: FacultyProfileUpdateRequest, token: str):
    return services.update_faculty_profile(token, req)

# ----------------- NOTIFICATIONS -----------------
@app.get("/notification_actives")
def get_notifications(token: str):
    return services.get_notifications(token)

# ----------------- ATTENDANCE RECORD -----------------
@app.get("/faculty_attendance_record")
def get_faculty_attendance_record(token: str):
    return services.get_faculty_attendance_record(token)

@app.get("/completed_attendance_detail/{id}")
def get_completed_attendance_detail(id: str, token: str):
    return services.get_completed_attendance_detail(id, token)

@app.get("/processed_attendance_detail/{id}")
def get_processed_attendance_detail(id: str, token: str):
    return services.get_processed_attendance_detail(id, token)

@app.put("/processed_attendance_detail/{id}")
def update_processed_attendance_detail(id: str, req: ProcessedAttendanceUpdateRequest, token: str):
    return services.update_processed_attendance_detail(id, token, req)

@app.get("/processing_attendance_detail/{id}")
def get_processing_attendance_detail(id: str, token: str):
    return services.get_processing_attendance_detail(id, token)

@app.post("/processing_attendance_detail/{id}")
def post_processing_attendance_detail(id: str, req: ProcessingAttendanceRequest, token: str):
    return services.post_processing_attendance_detail(id, token, req)

@app.get("/manual_attendance/{id}")
def get_manual_attendance(id: str, token: str):
    return services.get_manual_attendance(id, token)

@app.post("/manual_attendance/{id}")
def post_manual_attendance(id: str, req: ManualAttendanceRequest, token: str):
    return services.post_manual_attendance(id, token, req)

@app.post("/image_upload_attendance/{id}")
def image_upload_attendance(id: str, req: ImageUploadRequest, token: str):
    return services.image_upload_attendance(id, token, req)

@app.get("/CCTV_attendance/{id}")
def get_cctv_attendance(id: str, token: str):
    return services.get_cctv_attendance(id, token)

# ----------------- UNSCHEDULED LECTURE -----------------
@app.post("/unschedule_lecture")
def create_unschedule_lecture(req: UnscheduleLectureRequest, token: str):
    return services.create_unschedule_lecture(token, req)

@app.get("/unschedule_lecture")
def get_unschedule_lecture_data(token: str):
    return services.get_unschedule_lecture_data(token)
