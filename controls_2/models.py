from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

enrollment_table = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(40), nullable=False)

    courses = relationship(
        "Course",
        secondary=enrollment_table,
        back_populates="students",
    )

    def __repr__(self):
        return f"<Student(id={self.id}, full_name={self.full_name})>"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    teacher = Column(String(120), nullable=False)
    duration = Column(String(60), nullable=False)

    students = relationship(
        "Student",
        secondary=enrollment_table,
        back_populates="courses",
    )

    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title})>"
