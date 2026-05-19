from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import database
from database import (
    add_course,
    add_enrollment,
    add_student,
    delete_course,
    delete_student,
    get_courses,
    get_enrollments,
    get_student_by_id,
    get_students,
    remove_enrollment,
    update_course,
    update_student,
)


class StudentFormDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.setWindowTitle("Студент")
        self.student = student
        self.full_name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()

        form = QFormLayout()
        form.addRow("ФИО:", self.full_name_input)
        form.addRow("Возраст:", self.age_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Телефон:", self.phone_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(save_button)
        self.setLayout(layout)

        if student:
            self.full_name_input.setText(student.full_name)
            self.age_input.setText(str(student.age))
            self.email_input.setText(student.email)
            self.phone_input.setText(student.phone)

    def get_data(self):
        return (
            self.full_name_input.text().strip(),
            int(self.age_input.text().strip() or 0),
            self.email_input.text().strip(),
            self.phone_input.text().strip(),
        )


class CourseFormDialog(QDialog):
    def __init__(self, parent=None, course=None):
        super().__init__(parent)
        self.setWindowTitle("Курс")
        self.course = course
        self.title_input = QLineEdit()
        self.teacher_input = QLineEdit()
        self.duration_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Название:", self.title_input)
        form.addRow("Преподаватель:", self.teacher_input)
        form.addRow("Длительность:", self.duration_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(save_button)
        self.setLayout(layout)

        if course:
            self.title_input.setText(course.title)
            self.teacher_input.setText(course.teacher)
            self.duration_input.setText(course.duration)

    def get_data(self):
        return (
            self.title_input.text().strip(),
            self.teacher_input.text().strip(),
            self.duration_input.text().strip(),
        )


class BaseTab(QWidget):
    def create_table(self, headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    def show_message(self, message: str):
        QMessageBox.information(self, "Информация", message)


class StudentTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени...")
        self.search_input.textChanged.connect(self.load_students)

        self.table = self.create_table(["ID", "ФИО", "Возраст", "Email", "Телефон"])

        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Изменить")
        delete_button = QPushButton("Удалить")

        add_button.clicked.connect(self.add_student)
        edit_button.clicked.connect(self.edit_student)
        delete_button.clicked.connect(self.delete_student)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Студенты"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_students()

    def load_students(self):
        search_text = self.search_input.text().strip()
        students = get_students(search_text)
        self.table.setRowCount(0)

        for student in students:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            self.table.setItem(row, 1, QTableWidgetItem(student.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(student.age)))
            self.table.setItem(row, 3, QTableWidgetItem(student.email))
            self.table.setItem(row, 4, QTableWidgetItem(student.phone))

    def selected_student_id(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        return int(selected[0].text())

    def add_student(self):
        dialog = StudentFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            full_name, age, email, phone = dialog.get_data()
            if not full_name or age <= 0 or not email or not phone:
                self.show_error("Все поля студента должны быть заполнены корректно.")
                return
            add_student(full_name, age, email, phone)
            self.load_students()

    def edit_student(self):
        student_id = self.selected_student_id()
        if student_id is None:
            self.show_error("Выберите студента для изменения.")
            return
        student = get_student_by_id(student_id)
        if student is None:
            self.show_error("Студент не найден.")
            return
        dialog = StudentFormDialog(self, student)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            full_name, age, email, phone = dialog.get_data()
            if not full_name or age <= 0 or not email or not phone:
                self.show_error("Все поля студента должны быть заполнены корректно.")
                return
            update_student(student_id, full_name, age, email, phone)
            self.load_students()

    def delete_student(self):
        student_id = self.selected_student_id()
        if student_id is None:
            self.show_error("Выберите студента для удаления.")
            return
        confirm = QMessageBox.question(
            self,
            "Удалить студента",
            "Вы действительно хотите удалить выбранного студента?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_student(student_id)
            self.load_students()


class CourseTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию курса...")
        self.search_input.textChanged.connect(self.load_courses)

        self.table = self.create_table(["ID", "Название", "Преподаватель", "Длительность"])

        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Изменить")
        delete_button = QPushButton("Удалить")

        add_button.clicked.connect(self.add_course)
        edit_button.clicked.connect(self.edit_course)
        delete_button.clicked.connect(self.delete_course)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Курсы"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_courses()

    def load_courses(self):
        search_text = self.search_input.text().strip()
        courses = get_courses(search_text)
        self.table.setRowCount(0)

        for course in courses:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(course.id)))
            self.table.setItem(row, 1, QTableWidgetItem(course.title))
            self.table.setItem(row, 2, QTableWidgetItem(course.teacher))
            self.table.setItem(row, 3, QTableWidgetItem(course.duration))

    def selected_course_id(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        return int(selected[0].text())

    def add_course(self):
        dialog = CourseFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, teacher, duration = dialog.get_data()
            if not title or not teacher or not duration:
                self.show_error("Все поля курса должны быть заполнены.")
                return
            add_course(title, teacher, duration)
            self.load_courses()

    def edit_course(self):
        course_id = self.selected_course_id()
        if course_id is None:
            self.show_error("Выберите курс для изменения.")
            return
        course = get_course_by_id(course_id)
        if course is None:
            self.show_error("Курс не найден.")
            return
        dialog = CourseFormDialog(self, course)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, teacher, duration = dialog.get_data()
            if not title or not teacher or not duration:
                self.show_error("Все поля курса должны быть заполнены.")
                return
            update_course(course_id, title, teacher, duration)
            self.load_courses()

    def delete_course(self):
        course_id = self.selected_course_id()
        if course_id is None:
            self.show_error("Выберите курс для удаления.")
            return
        confirm = QMessageBox.question(
            self,
            "Удалить курс",
            "Вы действительно хотите удалить выбранный курс?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_course(course_id)
            self.load_courses()


class EnrollmentTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.student_combo = QComboBox()
        self.course_combo = QComboBox()

        self.table = self.create_table(["ID студента", "Студент", "ID курса", "Курс"])

        enroll_button = QPushButton("Записать на курс")
        remove_button = QPushButton("Удалить запись")
        refresh_button = QPushButton("Обновить список")

        enroll_button.clicked.connect(self.enroll_student)
        remove_button.clicked.connect(self.remove_enrollment)
        refresh_button.clicked.connect(self.load_enrollments)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Студент:"))
        top_layout.addWidget(self.student_combo)
        top_layout.addWidget(QLabel("Курс:"))
        top_layout.addWidget(self.course_combo)
        top_layout.addWidget(enroll_button)
        top_layout.addWidget(remove_button)
        top_layout.addWidget(refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Записи на курсы"))
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_comboboxes()
        self.load_enrollments()

    def load_comboboxes(self):
        self.student_combo.clear()
        self.course_combo.clear()
        for student in get_students():
            self.student_combo.addItem(f"{student.full_name} ({student.id})", student.id)
        for course in get_courses():
            self.course_combo.addItem(f"{course.title} ({course.id})", course.id)

    def load_enrollments(self):
        enrollments = get_enrollments()
        self.table.setRowCount(0)
        for student, course in enrollments:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            self.table.setItem(row, 1, QTableWidgetItem(student.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(course.id)))
            self.table.setItem(row, 3, QTableWidgetItem(course.title))

    def selected_enrollment(self):
        selected = self.table.selectedItems()
        if not selected:
            return None, None
        student_id = int(selected[0].text())
        course_id = int(selected[2].text())
        return student_id, course_id

    def enroll_student(self):
        student_id = self.student_combo.currentData()
        course_id = self.course_combo.currentData()
        if student_id is None or course_id is None:
            self.show_error("Выберите студента и курс.")
            return
        add_enrollment(student_id, course_id)
        self.load_enrollments()
        self.show_message("Студент успешно записан на курс.")

    def remove_enrollment(self):
        student_id, course_id = self.selected_enrollment()
        if student_id is None or course_id is None:
            self.show_error("Выберите запись для удаления.")
            return
        remove_enrollment(student_id, course_id)
        self.load_enrollments()
        self.show_message("Запись удалена.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Course Manager")
        self.resize(940, 640)

        tabs = QTabWidget()
        tabs.addTab(StudentTab(), "Студенты")
        tabs.addTab(CourseTab(), "Курсы")
        tabs.addTab(EnrollmentTab(), "Записи")

        self.setCentralWidget(tabs)


def create_main_window() -> MainWindow:
    return MainWindow()
