from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import *
from schemas import *
from datetime import datetime, timedelta
from sqlalchemy import func, case, and_
from datetime import date
from collections import Counter
import os, base64
from fastapi.responses import FileResponse
BASE_DIR = "./Images"
# ----------------- LOGIN -----------------
def login(req: LoginRequest, db: Session = Depends(get_db)):
    
    user = db.query(LoginAuthentication).filter(
        LoginAuthentication.username == req.username,
        LoginAuthentication.password == req.password,  # hash in prod!
        LoginAuthentication.role == req.role,
        LoginAuthentication.isactive == True,
        LoginAuthentication.isdelete == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid credentials",
                "user_id": None
            }
        )

    # ✅ Insert into RecentActivity (Insert type action)
    activity = RecentActivity(
        user_id=str(user.userid),
        action_title="Login",
        action_detail=f"User {user.username} logged in.",
        impact_level="Low",
        number_of_impacted_data=0
    )
    db.add(activity)

    # ✅ Insert into Notifications
    notification = Notifications(
        user_id=str(user.userid),
        title="Login Successful",
        message=f"Welcome {user.username}, you have successfully logged in.",
        type="success"
    )
    db.add(notification)

    db.commit()

    return {
        "success": True,
        "message": "Login successful",
        "user_id": str(user.userid)
    }


def post_faculty_dashboard(req: FacultyDashboardRequest, user_id: str, db: Session):
    # 1) Validate faculty id
    if not isinstance(user_id, str) or not user_id.upper().startswith("FAC"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

    # 2) Parse req.date (accepts "YYYY-MM-DD" string or a date object)
    raw_date = req.date
    if isinstance(raw_date, str):
        try:
            selected_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
    elif isinstance(raw_date, _date):
        selected_date = raw_date
    else:
        raise HTTPException(status_code=400, detail="Invalid date value")

    # 3) Compute week range: Monday (start_of_week) -> Saturday (end_of_week)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=5)  # Saturday

    # 4) number_of_lecture_per_week (between Monday and Saturday inclusive)
    number_of_lecture_per_week = (
        db.query(func.count())
        .select_from(ScheduleAttendance)
        .filter(
            ScheduleAttendance.faculty_id == user_id,
            ScheduleAttendance.date >= start_of_week,
            ScheduleAttendance.date <= end_of_week,
            ScheduleAttendance.isactive == True,
            ScheduleAttendance.isdelete == False,
        )
        .scalar() or 0
    )

    # 5) number_of_lecture_today (on selected_date)
    number_of_lecture_today = (
        db.query(func.count())
        .select_from(ScheduleAttendance)
        .filter(
            ScheduleAttendance.faculty_id == user_id,
            ScheduleAttendance.date == selected_date,
            ScheduleAttendance.isactive == True,
            ScheduleAttendance.isdelete == False,
        )
        .scalar() or 0
    )

    # 6) pending & processed counts up to and including selected_date (exclude future)
    number_of_pending_attendance = (
        db.query(func.count())
        .select_from(ScheduleAttendance)
        .filter(
            ScheduleAttendance.faculty_id == user_id,
            ScheduleAttendance.date <= date.today(),
            ScheduleAttendance.status.ilike("pending"),
            ScheduleAttendance.isactive == True,
            ScheduleAttendance.isdelete == False,
        )
        .scalar() or 0
    )

    number_of_processed_attendance = (
        db.query(func.count())
        .select_from(ScheduleAttendance)
        .filter(
            ScheduleAttendance.faculty_id == user_id,
            ScheduleAttendance.date <= date.today(),
            ScheduleAttendance.status.ilike("processed"),
            ScheduleAttendance.isactive == True,
            ScheduleAttendance.isdelete == False,
        )
        .scalar() or 0
    )

    # 7) Fetch schedule_lecture_for_week with joined readable fields
    rows = (
        db.query(
            ScheduleAttendance.attendance_id,
            ClassDetails.grade,
            ClassDetails.division,
            ClassDetails.batch,
            ScheduleAttendance.roomnumber,
            ScheduleAttendance.status,
            SubjectDetails.subject_name,
            ScheduleAttendance.date,
            ScheduleAttendance.day,
            TimeSlots.start_time,
            TimeSlots.end_time,
        )
        .join(ClassDetails, ScheduleAttendance.class_id == ClassDetails.class_id)
        .join(SubjectDetails, ScheduleAttendance.subject_id == SubjectDetails.subject_id)
        .join(TimeSlots, ScheduleAttendance.timeslot_id == TimeSlots.timeslot_id)
        .filter(
            ScheduleAttendance.faculty_id == user_id,
            ScheduleAttendance.date >= start_of_week,
            ScheduleAttendance.date <= end_of_week,
            ScheduleAttendance.isactive == True,
            ScheduleAttendance.isdelete == False,
        )
        .order_by(ScheduleAttendance.date, TimeSlots.start_time)
        .all()
    )

    schedule_lecture_for_week = []
    for r in rows:
        # r is a tuple aligned with the selected columns
        attendance_id = r[0]
        grade = r[1]
        division = r[2]
        batch = r[3]
        room = r[4]
        status = r[5] or ""
        subject_name = r[6]
        lecture_date = r[7]
        day = r[8]
        start_time = r[9]
        end_time = r[10]

        # student_division_batch like "10-A" or "10-A-batch"
        student_division_batch = f"{grade}-{division}"
        if batch:
            student_division_batch += f"-{batch}"

        # format timeslot: "HH:MM-HH:MM"
        try:
            timeslot_str = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        except Exception:
            # fallback to string
            timeslot_str = f"{start_time}-{end_time}"

        schedule_lecture_for_week.append({
            "attendance_id": attendance_id,
            "student_division_batch": student_division_batch,
            "room_number": room,
            "status": status.capitalize() if isinstance(status, str) else status,
            "subject": subject_name,
            "date": str(lecture_date),
            "day": day,
            "timeslot": timeslot_str
        })
        unique_timeslots = []
    try:
        unique_timeslots = (
            db.query(
                TimeSlots.start_time,
                TimeSlots.end_time
            )
            .join(ScheduleAttendance, ScheduleAttendance.timeslot_id == TimeSlots.timeslot_id)
            .filter(
                ScheduleAttendance.faculty_id == user_id,
                ScheduleAttendance.isactive == True,
                ScheduleAttendance.isdelete == False,
            )
            .distinct()
            .order_by(TimeSlots.start_time)
            .all()
        )
    except Exception as e:
        print("Error while fetching timeslots:", e)

    timeslot_array = []
    for t in unique_timeslots or []:
        try:
            timeslot_str = f"{t.start_time.strftime('%H:%M')}-{t.end_time.strftime('%H:%M')}"
        except Exception:
            timeslot_str = f"{t.start_time}-{t.end_time}"
        timeslot_array.append(timeslot_str)
    # 8) Final response (matches GET structure)
    return {
        "number_of_lecture_per_week": number_of_lecture_per_week,
        "number_of_lecture_today": number_of_lecture_today,
        "number_of_pending_attendance": number_of_pending_attendance,
        "number_of_processed_attendance": number_of_processed_attendance,
        "schedule_lecture_for_week": schedule_lecture_for_week,
        "timeslots": timeslot_array,
        "date": str(selected_date)
    }

def get_faculty_profile(user_id: str, db: Session = Depends(get_db)):
    if not user_id.startswith("FAC"):
        raise HTTPException(status_code=400, detail="Invalid user id, must start with FAC")
    faculty = (
        db.query(
            FacultyDetails.faculty_name,
            FacultyDetails.faculty_contact_number,
            FacultyDetails.faculty_email,
            FacultyDetails.faculty_profile_picture,
            FacultyDetails.institute_id,
            InstituteDetails.institute_name
        )
        .join(InstituteDetails, FacultyDetails.institute_id == InstituteDetails.institute_id)
        .filter(FacultyDetails.faculty_id == user_id,
                FacultyDetails.isactive == True,
                FacultyDetails.isdelete == False)
        .first()
    )

    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    # ⚠️ No activity insert (just a read operation)
    subjects = db.query(SubjectDetails.subject_name)\
        .join(FacultySubjectMapping, FacultySubjectMapping.subject_id == SubjectDetails.subject_id)\
        .filter(FacultySubjectMapping.faculty_id == user_id)\
        .all()
    subject_names = "|".join([s.subject_name for s in subjects]) if subjects else None
    file_path = os.path.join(
        BASE_DIR,
        faculty.institute_id,
        "Profile_Image_Repo",
        "Faculty_Profile",
        faculty.faculty_profile_picture
    )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    with open(file_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

    return {
        "faculty_name": faculty.faculty_name,
        "faculty_contact_number": faculty.faculty_contact_number,
        "faculty_email": faculty.faculty_email,
        "subjects": subject_names,
        "institute_name": faculty.institute_name,
        "profile_image": encoded_string
    }

def update_faculty_profile(req, user_id: str, db: Session):
    import os
    import base64
    
    if not user_id.startswith("FAC"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid faculty ID"
        )

    faculty = db.query(FacultyDetails).filter(
        FacultyDetails.faculty_id == user_id,
        FacultyDetails.isactive == True,
        FacultyDetails.isdelete == False
    ).first()

    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Get institute ID for image path
    institute_id = faculty.institute_id
    
    # Check if email has changed
    old_email = faculty.faculty_email
    new_email = req.faculty_email
    email_changed = old_email != new_email
    
    # Update fields (Update action)
    faculty.faculty_name = req.faculty_name
    faculty.faculty_contact_number = req.faculty_contact_number
    faculty.faculty_email = req.faculty_email
    
    # Handle profile image if provided
    if req.profile_image:
        try:
            # Create directory if it doesn't exist
            profile_dir = f"./Images/{institute_id}/Profile_Image_Repo"
            os.makedirs(profile_dir, exist_ok=True)
            
            # Get current profile image filename or create a new one
            current_image = faculty.faculty_profile_picture
            if not current_image:
                current_image = f"{user_id}_profile.jpg"
                faculty.faculty_profile_picture = current_image
            
            # Save the image with the same filename
            image_path = os.path.join(profile_dir, current_image)
            
            # Decode base64 image and save
            image_data = base64.b64decode(req.profile_image.split(",")[1] if "," in req.profile_image else req.profile_image)
            with open(image_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save profile image: {str(e)}"
            )
    
    # Update email in login authentication table if changed
    if email_changed:
        login_user = db.query(LoginAuthentication).filter(
            LoginAuthentication.userid == user_id,
            LoginAuthentication.isactive == True,
            LoginAuthentication.isdelete == False
        ).first()
        
        if login_user:
            login_user.username = new_email
            
    try:
        db.commit()
        db.refresh(faculty)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

    # ✅ Log activity (Update type)
    activity = RecentActivity(
        user_id=user_id,
        action_title="Update Faculty Profile",
        action_detail=f"Faculty profile updated for {user_id}",
        impact_level="Medium",
        number_of_impacted_data=1
    )
    db.add(activity)

    # ✅ Add notification
    notification = Notifications(
        user_id=user_id,
        title="Profile Updated",
        message=f"Your profile has been updated successfully.",
        type="info"
    )
    db.add(notification)

    db.commit()
    
    return {
        "success": True,
        "message": "Faculty profile updated successfully",
        "faculty_id": faculty.faculty_id,
        "faculty_name": faculty.faculty_name,
        "faculty_contact_number": faculty.faculty_contact_number,
        "faculty_email": faculty.faculty_email,
        "profile_image_updated": req.profile_image is not None,
        "email_updated_in_login": email_changed
    }

# ----------------- NOTIFICATIONS -----------------
def get_notifications(user_id: str):
    return [{"title": "New Lecture", "message": "You have 1 new lecture", "color": "blue"}]

# ----------------- ATTENDANCE RECORD -----------------
def get_faculty_attendance_record(user_id: str):
    return {"message": "attendance records"}

def get_completed_attendance_detail(id: str, user_id: str):
    return {"message": f"completed attendance {id}"}

def get_processed_attendance_detail(id: str, user_id: str):
    return {"message": f"processed attendance {id}"}

def update_processed_attendance_detail(id: str, req: ProcessedAttendanceUpdateRequest, user_id: str):
    return {"success": True}

def get_processing_attendance_detail(req: ProcessingAttendanceDetailRequest, user_id: str, db: Session = Depends(get_db)):
    # Validate user_id starts with FAC
    if not user_id.startswith("FAC"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid faculty ID"
        )
    
    # Get attendance record
    attendance_record = db.query(ScheduleAttendance).filter(
        ScheduleAttendance.attendance_id == req.attendance_id,
        ScheduleAttendance.status == "processing"
    ).first()
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found or not in processing status"
        )
    
    # Get institute ID from faculty
    faculty = db.query(FacultyDetails).filter(
        FacultyDetails.faculty_id == user_id
    ).first()
    
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    
    institute_id = faculty.institute_id
    
    # Path to images
    image_folder = f"{BASE_DIR}/{institute_id}/Image_Upload/{req.attendance_id}"
    
    # Check if folder exists
    if not os.path.exists(image_folder):
        return {
            "success": True,
            "message": "No images found for this attendance",
            "images": []
        }
    
    # Get all image files from the folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
    
    # Create full paths for images
    image_paths = [f"{image_folder}/{image_file}" for image_file in image_files]
    
    # Encode images in base64
    base64_images = []
    for image_path in image_paths:
        try:
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                base64_images.append(encoded_string)
        except Exception as e:
            print(f"Error encoding image {image_path}: {str(e)}")
    
    return {
        "success": True,
        "message": "Images retrieved successfully",
        "images": image_files,
        "base64_images": base64_images
    }

def post_processing_attendance_detail(id: str, req: ProcessingAttendanceRequest, user_id: str):
    return {"success": True}

def get_student_record(req: ManualAttendanceGetRequest, user_id: str, db: Session = Depends(get_db)):
    # Validate user_id starts with FAC
    if not user_id.startswith("FAC"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid faculty ID"
        )
    
    # Get attendance record
    attendance_record = db.query(ScheduleAttendance).filter(
        ScheduleAttendance.attendance_id == req.attendance_id,
        ScheduleAttendance.isactive == True,
        ScheduleAttendance.isdelete == False
    ).first()
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Get class details
    class_details = db.query(ClassDetails).filter(
        ClassDetails.class_id == attendance_record.class_id,
        ClassDetails.isactive == True,
        ClassDetails.isdelete == False
    ).first()
    
    if not class_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class details not found"
        )
    
    # Get institute ID from class details
    institute_id = class_details.institute_id
    
    # Check if batch is set
    if class_details.batch:
        # If batch is set, fetch students with the same class_id
        students = db.query(
            StudentDetails.student_id,
            StudentDetails.student_name,
            StudentDetails.student_rollnumber,
            StudentDetails.original_image_name
        ).filter(
            StudentDetails.class_id == class_details.class_id,
            StudentDetails.isactive == True,
            StudentDetails.isdelete == False
        ).all()
    else:
        # If batch is not set, fetch all students with same grade and division
        class_ids = db.query(ClassDetails.class_id).filter(
            ClassDetails.grade == class_details.grade,
            ClassDetails.division == class_details.division,
            ClassDetails.isactive == True,
            ClassDetails.isdelete == False
        ).all()
        
        class_id_list = [c.class_id for c in class_ids]
        
        students = db.query(
            StudentDetails.student_id,
            StudentDetails.student_name,
            StudentDetails.student_rollnumber,
            StudentDetails.original_image_name
        ).filter(
            StudentDetails.class_id.in_(class_id_list),
            StudentDetails.isactive == True,
            StudentDetails.isdelete == False
        ).all()
    
    # Format student details
    student_list = []
    for student in students:
        # Get base64 encoded image
        image_base64 = None
        image_path = None
        if student.original_image_name:
            # First try the path with Profile_Image_Repo
            image_path = f"./Images/{institute_id}/Profile_Image_Repo/Student_Image_Repo/Student_Profile/{student.original_image_name}"
            
            # If that doesn't exist, try the alternative path structure
            if not os.path.exists(image_path):
                image_path = f"./Images/{institute_id}/Profile_Image_Repo/Student_Profile/{student.original_image_name}"
            
            # Debug info
            print(f"Looking for image at: {image_path}")
            print(f"File exists: {os.path.exists(image_path)}")
            
            try:
                if os.path.exists(image_path):
                    with open(image_path, "rb") as img_file:
                        image_data = img_file.read()
                        print(f"Image size: {len(image_data)} bytes")
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
            except Exception as e:
                print(f"Error reading image file: {e}")
        
        student_list.append({
            "student_id": student.student_id,
            "student_name": student.student_name,
            "roll_number": student.student_rollnumber,
            "image_base64": image_base64,
            "image_path": image_path
        })
    
    return {
        "success": True,
        "message": "Student details retrieved successfully",
        "attendance_id": req.attendance_id,
        "students": student_list
    }

def post_manual_attendance(req: ManualAttendanceRequest, user_id: str, db: Session = Depends(get_db)):
    # Validate user_id starts with FAC
    if not user_id.startswith("FAC"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid faculty ID"
        )
    
    # Get attendance record
    attendance_record = db.query(ScheduleAttendance).filter(
        ScheduleAttendance.attendance_id == req.attendance_id,
        ScheduleAttendance.isactive == True,
        ScheduleAttendance.isdelete == False
    ).first()
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    try:
        # Insert attendance data for all students
        for student_attendance in req.attendance:
            # Check if record already exists
            existing_record = db.query(AttendanceData).filter(
                AttendanceData.attendance_id == req.attendance_id,
                AttendanceData.student_id == student_attendance.student_id
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.attendance_status = student_attendance.status
                existing_record.updatedat = func.now()
            else:
                # Create new record
                attendance_data = AttendanceData(
                    attendance_id=req.attendance_id,
                    student_id=student_attendance.student_id,
                    attendance_status=student_attendance.status
                )
                db.add(attendance_data)
        
        # Update schedule attendance status to completed and method to manual
        attendance_record.status = "Completed"
        attendance_record.method = "Manual"
        attendance_record.updatedat = func.now()
        
        # Add activity record
        activity = RecentActivity(
            user_id=user_id,
            action_title="Manual Attendance",
            action_detail=f"Manual attendance recorded for {req.attendance_id}",
            impact_level="Medium",
            number_of_impacted_data=len(req.attendance)
        )
        db.add(activity)
        
        # Add notification
        notification = Notifications(
            user_id=user_id,
            title="Attendance Recorded",
            message=f"Manual attendance for {req.attendance_id} has been recorded successfully.",
            type="success"
        )
        db.add(notification)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Manual attendance recorded successfully",
            "attendance_id": req.attendance_id
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record attendance: {str(e)}"
        )

def image_upload_attendance(req: ImageUploadRequest, user_id: str, db: Session = Depends(get_db)):
    # Validate faculty ID
    if not user_id.startswith("FAC"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid faculty ID"
        )
    
    # Validate attendance ID
    attendance_id = req.attendance_id
    
    # Check if attendance record exists
    attendance_record = db.query(ScheduleAttendance).filter(
        ScheduleAttendance.attendance_id == attendance_id,
        ScheduleAttendance.isactive == True,
        ScheduleAttendance.isdelete == False
    ).first()
    
    if not attendance_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )
    
    # Validate number of images (maximum 5)
    if len(req.images) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images allowed"
        )
    
    # Create directory path for storing images
    upload_dir = os.path.join(BASE_DIR, "INST1", "Image_Upload", attendance_id)
    
    # Delete directory if it exists
    if os.path.exists(upload_dir):
        import shutil
        shutil.rmtree(upload_dir)
    
    # Create directory
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save images to the directory
    saved_image_paths = []
    for i, image_base64 in enumerate(req.images):
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            
            # Save image to file
            image_filename = f"image_{i+1}.jpg"
            image_path = os.path.join(upload_dir, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_data)
            
            saved_image_paths.append(image_filename)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing image {i+1}: {str(e)}"
            )
    
    # Update attendance record status to "processing"
    attendance_record.status = "processing"
    attendance_record.uploaded_images_names = ",".join(saved_image_paths)
    db.commit()
    
    # Log activity
    activity = RecentActivity(
        user_id=user_id,
        action_title="Upload Attendance Images",
        action_detail=f"Uploaded {len(saved_image_paths)} images for attendance ID {attendance_id}",
        impact_level="Medium",
        number_of_impacted_data=len(saved_image_paths)
    )
    db.add(activity)
    
    # Add notification
    notification = Notifications(
        user_id=user_id,
        title="Images Uploaded",
        message=f"Your {len(saved_image_paths)} images for attendance ID {attendance_id} have been uploaded and are being processed.",
        type="info"
    )
    db.add(notification)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Successfully uploaded {len(saved_image_paths)} images for attendance ID {attendance_id}",
        "attendance_id": attendance_id,
        "status": "processing"
    }

def get_cctv_attendance(id: str, user_id: str):
    return {"success": True}

# ----------------- UNSCHEDULED LECTURE -----------------
def create_unschedule_lecture(req: UnscheduleLectureRequest, user_id: str):
    return {"success": True, "attendance_id": "ATT1001"}

def get_unschedule_lecture_data(user_id: str):
    return {"timeslot": [], "subject": [], "classes": [], "roomnumber": []}


def get_faculty_summary(user_id: str, db: Session, start_date: date = None, end_date: date = None):
    today = date.today()

    # ✅ Determine date range
    if start_date and end_date:
        min_date = start_date
        max_date = end_date
    else:
        # find earliest and latest lecture dates for this faculty
        min_date = db.query(func.min(ScheduleAttendance.date))\
            .filter(
                ScheduleAttendance.faculty_id == user_id,
                ScheduleAttendance.isactive == True,
                ScheduleAttendance.isdelete == False
            ).scalar()

        max_date = db.query(func.max(ScheduleAttendance.date))\
            .filter(
                ScheduleAttendance.faculty_id == user_id,
                ScheduleAttendance.date <= today,
                ScheduleAttendance.isactive == True,
                ScheduleAttendance.isdelete == False
            ).scalar()

    # ✅ If no lectures found
    if not min_date or not max_date:
        return {
            "faculty_id": user_id,
            "min_date": None,
            "max_date": None,
            "classes": [],
            "stats": {"Pending": 0, "Processed": 0, "Processing": 0, "Completed": 0},
            "lectures": [],
            "method_stats": {}
        }

    # ✅ Unique classes
    classes = db.query(
        ClassDetails.class_id,
        ClassDetails.grade,
        ClassDetails.division,
        ClassDetails.batch
    ).join(ScheduleAttendance, ScheduleAttendance.class_id == ClassDetails.class_id)\
     .filter(
         ScheduleAttendance.faculty_id == user_id,
         ScheduleAttendance.isactive == True,
         ScheduleAttendance.isdelete == False
     ).distinct().all()

    classes_list = [
        {"class_id": c.class_id, "standard_division_batch": f"{c.grade}-{c.division}-{c.batch}"}
        for c in classes
    ]

    # ✅ Lecture stats
    stats = {}
    for status in ["Pending", "Processed", "Processing", "Completed"]:
        stats[status] = db.query(func.count(ScheduleAttendance.attendance_id))\
            .filter(
                ScheduleAttendance.faculty_id == user_id,
                ScheduleAttendance.status == status,
                ScheduleAttendance.date >= min_date,
                ScheduleAttendance.date <= max_date,
                ScheduleAttendance.isactive == True,
                ScheduleAttendance.isdelete == False
            ).scalar() or 0

    # ✅ Lectures
    lectures = db.query(
        ScheduleAttendance.date,
        ScheduleAttendance.day,
        TimeSlots.start_time,
        TimeSlots.end_time,
        SubjectDetails.subject_name,
        ClassDetails.grade,
        ClassDetails.division,
        ClassDetails.batch,
        ScheduleAttendance.status,
        ScheduleAttendance.roomnumber,
        ScheduleAttendance.method,
    ).join(ClassDetails, ScheduleAttendance.class_id == ClassDetails.class_id)\
     .join(SubjectDetails, ScheduleAttendance.subject_id == SubjectDetails.subject_id)\
     .join(TimeSlots, ScheduleAttendance.timeslot_id == TimeSlots.timeslot_id)\
     .filter(
         ScheduleAttendance.faculty_id == user_id,
         ScheduleAttendance.date >= min_date,
         ScheduleAttendance.date <= max_date,
         ScheduleAttendance.isactive == True,
         ScheduleAttendance.isdelete == False
     ).order_by(ScheduleAttendance.date.asc()).all()

    lectures_list = []
    method_counter = Counter()

    for lec in lectures:
        timeslot_str = f"{lec.start_time.strftime('%H:%M')}-{lec.end_time.strftime('%H:%M')}"
        lecture_info = {
            "date": lec.date,
            "day": lec.day,
            "timeslot": timeslot_str,
            "subject": lec.subject_name,
            "class": f"{lec.grade}-{lec.division}-{lec.batch}",
            "status": lec.status,
            "roomnumber": lec.roomnumber,
        }
        # ✅ If completed, include method & update counter
        if lec.status.lower() == "completed":
            lecture_info["method"] = lec.method
            if lec.method:
                method_counter[lec.method] += 1

        lectures_list.append(lecture_info)

    # ✅ Prepare method statistics
    method_stats = {
        "total_completed": sum(method_counter.values()),
        "by_method": dict(method_counter)
    }

    return {
        "faculty_id": user_id,
        "min_date": min_date,
        "max_date": max_date,
        "classes": classes_list,
        "stats": stats,
        "lectures": lectures_list,
        "method_stats": method_stats
    }
