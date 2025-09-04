[1mdiff --git a/models.py b/models.py[m
[1mindex cba356d..8fd711b 100644[m
[1m--- a/models.py[m
[1m+++ b/models.py[m
[36m@@ -1,4 +1,4 @@[m
[31m-from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey[m
[32m+[m[32mfrom sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Time, Date[m
 from sqlalchemy.orm import relationship[m
 from database import Base[m
 [m
[36m@@ -47,25 +47,142 @@[m [mclass FacultyDetails(Base):[m
     # Relationship (optional, allows ORM joins)[m
     institute = relationship("InstituteDetails", backref="faculties")[m
 [m
[32m+[m[32mclass ClassDetails(Base):[m
[32m+[m[32m    __tablename__ = "Class_Details"[m
[32m+[m
[32m+[m[32m    class_id = Column(String, primary_key=True, index=True)[m[41m  [m
[32m+[m[32m    grade = Column(String, nullable=False)[m
[32m+[m[32m    division = Column(String, nullable=False)[m
[32m+[m[32m    batch = Column(String, nullable=False)[m
[32m+[m
[32m+[m[32m    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)[m
[32m+[m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationship with Institute[m
[32m+[m[32m    institute = relationship("InstituteDetails", backref="classes")[m
[32m+[m
[32m+[m[32mclass SubjectDetails(Base):[m
[32m+[m[32m    __tablename__ = "Subject_Details"[m
[32m+[m
[32m+[m[32m    subject_id = Column(String, primary_key=True, index=True)  # e.g., SUB1, SUB2...[m
[32m+[m[32m    subject_name = Column(String, nullable=False, unique=True)[m
[32m+[m
[32m+[m[32m    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)[m
[32m+[m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationship with Institute[m
[32m+[m[32m    institute = relationship("InstituteDetails", backref="subjects")[m
[32m+[m
[32m+[m[32mclass FacultySubjectMapping(Base):[m
[32m+[m[32m    __tablename__ = "Faculty_Subject_Mapping"[m
[32m+[m
[32m+[m[32m    faculty_id = Column(String, ForeignKey("Faculty_Details.faculty_id"), primary_key=True)[m
[32m+[m[32m    subject_id = Column(String, ForeignKey("Subject_Details.subject_id"), primary_key=True)[m
[32m+[m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationships[m
[32m+[m[32m    faculty = relationship("FacultyDetails", backref="subject_mappings")[m
[32m+[m[32m    subject = relationship("SubjectDetails", backref="faculty_mappings")[m
[32m+[m
 class StudentDetails(Base):[m
     __tablename__ = "Student_Details"[m
 [m
     student_id = Column(String, primary_key=True, index=True)  # e.g., STU1, STU2...[m
     student_name = Column(String, nullable=False)[m
     student_rollnumber = Column(String, nullable=False, unique=True)[m
[31m-    standard = Column(String, nullable=False)[m
[31m-    division = Column(String, nullable=False)[m
[31m-    batch = Column(String, nullable=False)[m
[31m-    regular_image = Column(String, nullable=True)   # can store file path / URL[m
[31m-    encoded_image = Column(String, nullable=True)   # can store face encoding (e.g., base64 string)[m
 [m
[31m-    # Foreign key to Institute_Details[m
[32m+[m[32m    # Image references[m
[32m+[m[32m    encode_image_name = Column(String, nullable=True)   # stored encoding filename[m
[32m+[m[32m    original_image_name = Column(String, nullable=True) # stored original filename[m
[32m+[m
[32m+[m[32m    # Foreign keys[m
     institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)[m
[32m+[m[32m    class_id = Column(String, ForeignKey("Class_Details.class_id"), nullable=False)[m
 [m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
     createdat = Column(DateTime(timezone=True), server_default=func.now())[m
     updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationships[m
[32m+[m[32m    institute = relationship("InstituteDetails", backref="students")[m
[32m+[m[32m    class_ = relationship("ClassDetails", backref="students")[m
[32m+[m
[32m+[m[32mclass TimeSlots(Base):[m
[32m+[m[32m    __tablename__ = "Time_Slots"[m
[32m+[m
[32m+[m[32m    timeslot_id = Column(String, primary_key=True, index=True)  # e.g., TS1, TS2...[m
[32m+[m[32m    start_time = Column(Time, nullable=False)[m
[32m+[m[32m    end_time = Column(Time, nullable=False)[m
[32m+[m
[32m+[m[32m    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)[m
[32m+[m
     isactive = Column(Boolean, default=True)[m
     isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
 [m
     # Relationship with Institute[m
[31m-    institute = relationship("InstituteDetails", backref="students")[m
\ No newline at end of file[m
[32m+[m[32m    institute = relationship("InstituteDetails", backref="timeslots")[m
[32m+[m
[32m+[m[32mclass ScheduleAttendance(Base):[m
[32m+[m[32m    __tablename__ = "Schedule_Attendance"[m
[32m+[m
[32m+[m[32m    attendance_id = Column(String, primary_key=True, index=True)  # e.g., ATT1, ATT2...[m
[32m+[m
[32m+[m[32m    # Foreign keys[m
[32m+[m[32m    class_id = Column(String, ForeignKey("Class_Details.class_id"), nullable=False)[m
[32m+[m[32m    faculty_id = Column(String, ForeignKey("Faculty_Details.faculty_id"), nullable=False)[m
[32m+[m[32m    subject_id = Column(String, ForeignKey("Subject_Details.subject_id"), nullable=False)[m
[32m+[m[32m    timeslot_id = Column(String, ForeignKey("Time_Slots.timeslot_id"), nullable=False)[m
[32m+[m
[32m+[m[32m    roomnumber = Column(String, nullable=True)[m
[32m+[m
[32m+[m[32m    # Schedule details[m
[32m+[m[32m    date = Column(Date, nullable=False)[m
[32m+[m[32m    day = Column(String, nullable=False)  # e.g., Monday[m
[32m+[m[32m    status = Column(String, nullable=True)  # e.g., "Completed", "Pending", "Cancelled"[m
[32m+[m
[32m+[m[32m    # Attendance-related data[m
[32m+[m[32m    uploaded_images_names = Column(String, nullable=True)  # store multiple filenames as CSV/JSON[m
[32m+[m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationships[m
[32m+[m[32m    class_ = relationship("ClassDetails", backref="attendance_records")[m
[32m+[m[32m    faculty = relationship("FacultyDetails", backref="attendance_records")[m
[32m+[m[32m    subject = relationship("SubjectDetails", backref="attendance_records")[m
[32m+[m[32m    timeslot = relationship("TimeSlots", backref="attendance_records")[m
[32m+[m
[32m+[m[32mclass AttendanceData(Base):[m
[32m+[m[32m    __tablename__ = "Attendance_Data"[m
[32m+[m
[32m+[m[32m    # Composite primary key (attendance_id + student_id)[m
[32m+[m[32m    attendance_id = Column(String, ForeignKey("Schedule_Attendance.attendance_id"), primary_key=True)[m
[32m+[m[32m    student_id = Column(String, ForeignKey("Student_Details.student_id"), primary_key=True)[m
[32m+[m
[32m+[m[32m    attendance_status = Column(String, nullable=False)  # e.g., "Present", "Absent", "Late"[m
[32m+[m
[32m+[m[32m    isactive = Column(Boolean, default=True)[m
[32m+[m[32m    isdelete = Column(Boolean, default=False)[m
[32m+[m[32m    createdat = Column(DateTime(timezone=True), server_default=func.now())[m
[32m+[m[32m    updatedat = Column(DateTime(timezone=True), onupdate=func.now())[m
[32m+[m
[32m+[m[32m    # Relationships[m
[32m+[m[32m    attendance = relationship("ScheduleAttendance", backref="student_attendance")[m
[32m+[m[32m    student = relationship("StudentDetails", backref="attendance_records")[m
\ No newline at end of file[m
