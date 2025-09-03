from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class LoginAuthentication(Base):
    __tablename__ = "Login_Authentication"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
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
    
    # Foreign key to Institute_Details
    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship (optional, allows ORM joins)
    institute = relationship("InstituteDetails", backref="faculties")

class StudentDetails(Base):
    __tablename__ = "Student_Details"

    student_id = Column(String, primary_key=True, index=True)  # e.g., STU1, STU2...
    student_name = Column(String, nullable=False)
    student_rollnumber = Column(String, nullable=False, unique=True)
    standard = Column(String, nullable=False)
    division = Column(String, nullable=False)
    batch = Column(String, nullable=False)
    regular_image = Column(String, nullable=True)   # can store file path / URL
    encoded_image = Column(String, nullable=True)   # can store face encoding (e.g., base64 string)

    # Foreign key to Institute_Details
    institute_id = Column(String, ForeignKey("Institute_Details.institute_id"), nullable=False)

    createdat = Column(DateTime(timezone=True), server_default=func.now())
    updatedat = Column(DateTime(timezone=True), onupdate=func.now())
    isactive = Column(Boolean, default=True)
    isdelete = Column(Boolean, default=False)

    # Relationship with Institute
    institute = relationship("InstituteDetails", backref="students")