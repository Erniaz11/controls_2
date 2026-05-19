from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import joinedload, sessionmaker

from models import Base, Student, Course, enrollment_table

SQLITE_URL = "sqlite:///students_courses.db"
engine = create_engine(SQLITE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def init_db():
    Base.metadata.create_all(engine)


def get_students(search: str | None = None) -> list[Student]:
    with SessionLocal() as session:
        query = select(Student)
        if search:
            query = query.where(Student.full_name.ilike(f"%{search}%"))
        return session.scalars(query.order_by(Student.id)).all()


def get_student_by_id(student_id: int) -> Student | None:
    with SessionLocal() as session:
        return session.get(Student, student_id)


def add_student(full_name: str, age: int, email: str, phone: str) -> Student:
    with SessionLocal() as session:
        student = Student(full_name=full_name, age=age, email=email, phone=phone)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


def update_student(student_id: int, full_name: str, age: int, email: str, phone: str) -> None:
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        if student is None:
            return
        student.full_name = full_name
        student.age = age
        student.email = email
        student.phone = phone
        session.commit()


def delete_student(student_id: int) -> None:
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        if student is None:
            return
        session.delete(student)
        session.commit()


def get_courses(search: str | None = None) -> list[Course]:
    with SessionLocal() as session:
        query = select(Course)
        if search:
            query = query.where(Course.title.ilike(f"%{search}%"))
        return session.scalars(query.order_by(Course.id)).all()


def get_course_by_id(course_id: int) -> Course | None:
    with SessionLocal() as session:
        return session.get(Course, course_id)


def add_course(title: str, teacher: str, duration: str) -> Course:
    with SessionLocal() as session:
        course = Course(title=title, teacher=teacher, duration=duration)
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


def update_course(course_id: int, title: str, teacher: str, duration: str) -> None:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return
        course.title = title
        course.teacher = teacher
        course.duration = duration
        session.commit()


def delete_course(course_id: int) -> None:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return
        session.delete(course)
        session.commit()


def get_enrollments() -> list[tuple[Student, Course]]:
    with SessionLocal() as session:
        students = session.scalars(select(Student).options(joinedload(Student.courses))).unique().all()
        result: list[tuple[Student, Course]] = []
        for student in students:
            for course in student.courses:
                result.append((student, course))
        return result


def add_enrollment(student_id: int, course_id: int) -> None:
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        course = session.get(Course, course_id)
        if student is None or course is None:
            return
        if course not in student.courses:
            student.courses.append(course)
            session.commit()


def remove_enrollment(student_id: int, course_id: int) -> None:
    with SessionLocal() as session:
        session.execute(
            delete(enrollment_table).where(
                enrollment_table.c.student_id == student_id,
                enrollment_table.c.course_id == course_id,
            )
        )
        session.commit()
