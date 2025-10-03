from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Time, Date,Enum, Text
from sqlalchemy.orm import relationship
from database import Base

class LoginAuthentication(Base):
    __tablename__ = "Login_Authentication"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(String, nullable=False)   # string type userid

    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())


class InstituteDetails(Base):
    __tablename__ = "Institute_Details"

    institute_id = Column(String, primary_key=True, index=True)
    institute_name = Column(String, nullable=False, unique=True)
    institute_address = Column(String, nullable=False)
    institute_contact_number = Column(String, nullable=False)
    institute_email = Column(String, nullable=False, unique=True)
    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

class FacultyDetails(Base):
    __tablename__ = "Faculty_Details"

    faculty_id = Column(String, primary_key=True, index=True)
    faculty_name = Column(String, nullable=False)
    faculty_email = Column(String, nullable=False, unique=True)
    faculty_contact_number = Column(String, nullable=False)
    faculty_profile_picture = Column(String, nullable=True)
    # Foreign key to Institute_Details
    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship (optional, allows ORM joins)
    institute = relationship("InstituteDetails", backref="faculties")

class ClassDetails(Base):
    __tablename__ = "Class_Details"

    class_id = Column(String, primary_key=True, index=True)  
    grade = Column(String, nullable=False)
    division = Column(String, nullable=False)
    batch = Column(String, nullable=True)

    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Institute
    institute = relationship("InstituteDetails", backref="classes")

class SubjectDetails(Base):
    __tablename__ = "Subject_Details"

    subject_id = Column(String, primary_key=True, index=True)  # e.g., SUB1, SUB2...
    subject_name = Column(String, nullable=False, unique=True)

    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Institute
    institute = relationship("InstituteDetails", backref="subjects")

class FacultySubjectMapping(Base):
    __tablename__ = "Faculty_Subject_Mapping"

    faculty_id = Column(String, ForeignKey("Faculty_Details.faculty_id"), primary_key=True)
    subject_id = Column(String, ForeignKey("Subject_Details.subject_id"), primary_key=True)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    faculty = relationship("FacultyDetails", backref="subject_mappings")
    subject = relationship("SubjectDetails", backref="faculty_mappings")

class StudentDetails(Base):
    __tablename__ = "Student_Details"

    student_id = Column(String, primary_key=True, index=True)  # e.g., STU1, STU2...
    student_name = Column(String, nullable=False)
    student_rollnumber = Column(String, nullable=False, unique=True)

    # Image references
    encode_image_name = Column(String, nullable=True)   # stored encoding filename
    original_image_name = Column(String, nullable=True) # stored original filename

    # Foreign keys
    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)
    class_id = Column(String, ForeignKey("Class_Details.class_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    institute = relationship("InstituteDetails", backref="students")
    class_ = relationship("ClassDetails", backref="students")

class TimeSlots(Base):
    __tablename__ = "Time_Slots"

    timeslot_id = Column(String, primary_key=True, index=True)  # e.g., TS1, TS2...
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Institute
    institute = relationship("InstituteDetails", backref="timeslots")

class ScheduleAttendance(Base):
    __tablename__ = "Schedule_Attendance"

    attendance_id = Column(String, primary_key=True, index=True)  # e.g., ATT1, ATT2...

    # Foreign keys
    class_id = Column(String, ForeignKey("Class_Details.class_id"), nullable=False)
    faculty_id = Column(String, ForeignKey("Faculty_Details.faculty_id"), nullable=False)
    subject_id = Column(String, ForeignKey("Subject_Details.subject_id"), nullable=False)
    timeslot_id = Column(String, ForeignKey("Time_Slots.timeslot_id"), nullable=False)

    roomnumber = Column(String, nullable=True)
    method = Column(String, nullable=True)
    # Schedule details
    date = Column(Date, nullable=False)
    day = Column(String, nullable=False)  # e.g., Monday
    status = Column(String, nullable=True)  # e.g., "Completed", "Pending", "Cancelled"

    # Attendance-related data
    uploaded_images_names = Column(String, nullable=True)  # store multiple filenames as CSV/JSON

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    class_ = relationship("ClassDetails", backref="attendance_records")
    faculty = relationship("FacultyDetails", backref="attendance_records")
    subject = relationship("SubjectDetails", backref="attendance_records")
    timeslot = relationship("TimeSlots", backref="attendance_records")

class AttendanceData(Base):
    __tablename__ = "Attendance_Data"

    # Composite primary key (attendance_id + student_id)
    attendance_id = Column(String, ForeignKey("Schedule_Attendance.attendance_id"), primary_key=True)
    student_id = Column(String, ForeignKey("Student_Details.student_id"), primary_key=True)

    attendance_status = Column(String, nullable=False)  # e.g., "Present", "Absent", "Late"

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    attendance = relationship("ScheduleAttendance", backref="student_attendance")
    student = relationship("StudentDetails", backref="attendance_records")


# ---------------- NOTIFICATIONS ----------------
class Notifications(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False)         # Which user gets this
    title = Column(String(255), nullable=False)      # Short title
    message = Column(Text, nullable=False)           # Full message
    type = Column(String(50))                        # info, warning, success, error
    is_read = Column(Boolean, default=False)         # Has user seen it?
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ---------------- RECENT ACTIVITY ----------------
class RecentActivity(Base):
    __tablename__ = "recent_activity"

    activity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False)             # Who performed the action
    action_title = Column(String(255), nullable=False)   # e.g. "Attendance Marked"
    action_detail = Column(Text)                         # Extra details
    impact_level = Column(String(50))                    # Low, Medium, High
    number_of_impacted_data = Column(Integer, default=0) # Count of records affected
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())