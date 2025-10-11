from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas import *
import services
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from datetime import date

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection error middleware
@app.middleware("http")
async def db_connection_error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except OperationalError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Server is down. Please try again later."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred. Please try again later."}
        )

# ----------------- LOGIN -----------------
@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return services.login(req, db)


# ----------------- FACULTY DASHBOARD -----------------
@app.post("/faculty_dashboard")
def faculty_dashboard(req: FacultyDashboardRequest, user_id: str, db: Session = Depends(get_db)):
    return services.post_faculty_dashboard(req, user_id, db)

# ----------------- FACULTY PROFILE -----------------
@app.get("/faculty_profile")
def get_faculty_profile(user_id: str, db: Session = Depends(get_db)):
    return services.get_faculty_profile(user_id, db)

@app.put("/faculty_profile")
def update_faculty_profile(
    req: FacultyProfileUpdateRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    return services.update_faculty_profile(req, user_id, db)

# ----------------- NOTIFICATIONS -----------------
# @app.get("/notification_actives")
# def get_notifications(user_id: str):
#     return services.get_notifications(user_id)



@app.put("/processed_attendance_detail")
async def update_processed_attendance_detail(req: ProcessedAttendanceUpdateRequest, user_id: str):
    return services.update_processed_attendance_detail(req.attendance_id, req, user_id)

@app.post("/processed_attendance_detail")
def process_attendance_detail(user_id: str, req: ProcessedAttendanceDetailRequest, db: Session = Depends(get_db)):
    return services.process_attendance_detail(req, user_id, db)

@app.post("/processing_attendance_detail")
def get_processing_attendance_detail(req: ProcessingAttendanceDetailRequest, user_id: str, db: Session = Depends(get_db)):
    return services.get_processing_attendance_detail(req, user_id, db)

# @app.post("/processing_attendance_detail/{id}")
# def post_processing_attendance_detail(id: str, req: ProcessingAttendanceRequest, user_id: str):
#     return services.post_processing_attendance_detail(id, req, user_id)

@app.post("/student_record")
def get_student_record(user_id: str, req: ManualAttendanceGetRequest , db: Session = Depends(get_db)):
    return services.get_student_record(req, user_id, db)

@app.post("/manual_attendance")
def post_manual_attendance(user_id: str, req: ManualAttendanceRequest, db: Session = Depends(get_db)):
    return services.post_manual_attendance(req, user_id, db)

@app.post("/image_upload_attendance")
def image_upload_attendance(req: ImageUploadRequest, user_id: str, db: Session = Depends(get_db)):
    return services.image_upload_attendance(req, user_id, db)

# @app.get("/CCTV_attendance/{id}")
# def get_cctv_attendance(id: str, user_id: str):
#     return services.get_cctv_attendance(id, user_id)

@app.post("/unschedule_lecture")
def create_unschedule_lecture(req: UnscheduleLectureRequest, user_id: str, db: Session = Depends(get_db)):
    return services.create_unschedule_lecture(req, user_id, db)



@app.get("/faculty/summary")
def faculty_summary(
    user_id: str,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    if not user_id.upper().startswith("FAC"):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid faculty ID")
    return services.get_faculty_summary(
        user_id=user_id,
        db=db,
        start_date=start_date,
        end_date=end_date
    )
