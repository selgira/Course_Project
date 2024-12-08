#файл: hr_agency.py
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QInputDialog)

#модели
class Employer:
    def __init__(self, name, industry, description):
        self.name = name
        self.industry = industry
        self.description = description

class Candidate:
    def __init__(self, name, skills, experience):
        self.name = name
        self.skills = skills
        self.experience = experience

class Vacancy:
    def __init__(self, title, employer_id, requirements):
        self.title = title
        self.employer_id = employer_id
        self.requirements = requirements

#управление базой данных
class HRDatabase:
    def __init__(self, db_name="кадровое агенство сельгира.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS Employers (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    industry TEXT NOT NULL,
                                    description TEXT)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS Candidates (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    skills TEXT NOT NULL,
                                    experience INTEGER NOT NULL)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS Vacancies (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT NOT NULL,
                                    employer_id INTEGER NOT NULL,
                                    requirements TEXT,
                                    FOREIGN KEY (employer_id) REFERENCES Employers (id))''')

    def add_candidate(self, candidate: Candidate):
        with self.conn:
            self.conn.execute("INSERT INTO Candidates (name, skills, experience) VALUES (?, ?, ?)",
                              (candidate.name, candidate.skills, candidate.experience))

    def get_candidates(self, skill_filter=None):
        with self.conn:
            if skill_filter:
                return self.conn.execute("SELECT * FROM Candidates WHERE skills LIKE ?", (f"%{skill_filter}%",)).fetchall()
            return self.conn.execute("SELECT * FROM Candidates").fetchall()

    def edit_candidate(self, candidate_id, name, skills, experience):
        with self.conn:
            self.conn.execute('''UPDATE Candidates 
                                 SET name = ?, skills = ?, experience = ? 
                                 WHERE id = ?''', (name, skills, experience, candidate_id))

    def get_vacancies(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM Vacancies").fetchall()

    def find_matching_candidates(self, requirements):
        with self.conn:
            return self.conn.execute('''SELECT * FROM Candidates WHERE skills LIKE ?''', (f"%{requirements}%",)).fetchall()

    def add_vacancy(self, vacancy: Vacancy):
        with self.conn:
            self.conn.execute("INSERT INTO Vacancies (title, employer_id, requirements) VALUES (?, ?, ?)",
                              (vacancy.title, vacancy.employer_id, vacancy.requirements))

#интерфейс
class HRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кадровое агентство")
        self.db = HRDatabase()
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        #основной горизонтальный макет
        main_horizontal_layout = QHBoxLayout()

        #слева - столбец для кандидатов
        candidates_layout = QVBoxLayout()
        candidates_label = QLabel("Кандидаты")
        candidates_label.setAlignment(Qt.AlignCenter)
        add_candidate_btn = QPushButton("Добавить кандидата")
        add_candidate_btn.clicked.connect(self.show_add_candidate_dialog)
        edit_candidate_btn = QPushButton("Редактировать кандидата")
        edit_candidate_btn.clicked.connect(self.show_edit_candidate_dialog)
        view_candidates_btn = QPushButton("Список кандидатов")
        view_candidates_btn.clicked.connect(self.show_candidates)

        candidates_layout.addWidget(candidates_label)
        candidates_layout.addWidget(add_candidate_btn)
        candidates_layout.addWidget(edit_candidate_btn)
        candidates_layout.addWidget(view_candidates_btn)

        #спрао - столбец для вакансий
        vacancies_layout = QVBoxLayout()
        vacancies_label = QLabel("Вакансии")
        vacancies_label.setAlignment(Qt.AlignCenter)
        add_vacancy_btn = QPushButton("Добавить вакансию")
        add_vacancy_btn.clicked.connect(self.show_add_vacancy_dialog)
        edit_vacancy_btn = QPushButton("Редактировать вакансию")
        edit_vacancy_btn.clicked.connect(self.show_edit_vacancy_dialog)
        view_vacancies_btn = QPushButton("Список вакансий")
        view_vacancies_btn.clicked.connect(self.show_vacancies)

        vacancies_layout.addWidget(vacancies_label)
        vacancies_layout.addWidget(add_vacancy_btn)
        vacancies_layout.addWidget(edit_vacancy_btn)
        vacancies_layout.addWidget(view_vacancies_btn)

        #снизу посерединке
        match_vacancies_btn = QPushButton("Подбор кандидатов для вакансий")
        match_vacancies_btn.clicked.connect(self.show_match_candidates)

        #добавить столбцы и кнопку в основной макет
        main_horizontal_layout.addLayout(candidates_layout)
        main_horizontal_layout.addLayout(vacancies_layout)

        main_layout.addLayout(main_horizontal_layout)
        main_layout.addWidget(match_vacancies_btn)

        main_widget.setLayout(main_layout)

    def show_edit_vacancy_dialog(self):
        vacancies = self.db.get_vacancies()
        vacancy_ids = [str(v[0]) for v in vacancies]
        selected_id, ok = QInputDialog.getItem(self, "Редактировать вакансию", "Выберите ID вакансии:", vacancy_ids, 0, False)

        if ok:
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать вакансию")
            layout = QVBoxLayout()
            vacancy = next(v for v in vacancies if v[0] == int(selected_id))

            title_input = QLineEdit(vacancy[1])  #название вакансии
            employer_input = QLineEdit(str(vacancy[2]))  #ID работодателя
            requirements_input = QLineEdit(vacancy[3])  #требования

            def update_vacancy():
                title = title_input.text().strip()
                employer_id = employer_input.text().strip()
                requirements = requirements_input.text().strip()
                if not title or not employer_id.isdigit() or not requirements:
                    QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                    return
                self.db.conn.execute('''UPDATE Vacancies 
                                        SET title = ?, employer_id = ?, requirements = ? 
                                        WHERE id = ?''', (title, int(employer_id), requirements, int(selected_id)))
                QMessageBox.information(dialog, "Успех", "Вакансия обновлена!")
                dialog.accept()

            submit_btn = QPushButton("Сохранить изменения")
            submit_btn.clicked.connect(update_vacancy)

            layout.addWidget(title_input)
            layout.addWidget(employer_input)
            layout.addWidget(requirements_input)
            layout.addWidget(submit_btn)
            dialog.setLayout(layout)
            dialog.exec_()

    def show_add_vacancy_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить вакансию")
        layout = QVBoxLayout()

        title_input = QLineEdit()
        title_input.setPlaceholderText("Описание (через запятую)")
        employer_input = QLineEdit()
        employer_input.setPlaceholderText("ID работодателя")
        requirements_input = QLineEdit()
        requirements_input.setPlaceholderText("Требования")

        def add_vacancy():
            title = title_input.text().strip()
            employer_id = employer_input.text().strip()
            requirements = requirements_input.text().strip()
            if not title or not employer_id.isdigit() or not requirements:
                QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                return
            vacancy = Vacancy(title, int(employer_id), requirements)
            self.db.add_vacancy(vacancy)
            QMessageBox.information(dialog, "Успех", "Вакансия добавлена!")
            dialog.accept()

        submit_btn = QPushButton("Добавить")
        submit_btn.clicked.connect(add_vacancy)

        layout.addWidget(title_input)
        layout.addWidget(employer_input)
        layout.addWidget(requirements_input)
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_add_candidate_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить кандидата")
        layout = QVBoxLayout()

        name_input = QLineEdit()
        name_input.setPlaceholderText("Имя")
        skills_input = QLineEdit()
        skills_input.setPlaceholderText("Навыки (через запятую)")
        experience_input = QLineEdit()
        experience_input.setPlaceholderText("Опыт (в годах)")

        def add_candidate():
            name = name_input.text().strip()
            skills = skills_input.text().strip()
            experience = experience_input.text().strip()
            if not name or not skills or not experience.isdigit():
                QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                return
            candidate = Candidate(name, skills, int(experience))
            self.db.add_candidate(candidate)
            QMessageBox.information(dialog, "Успех", "Кандидат добавлен!")
            dialog.accept()

        submit_btn = QPushButton("Добавить")
        submit_btn.clicked.connect(add_candidate)

        layout.addWidget(name_input)
        layout.addWidget(skills_input)
        layout.addWidget(experience_input)
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_edit_candidate_dialog(self):
        candidates = self.db.get_candidates()
        candidate_ids = [str(c[0]) for c in candidates]
        selected_id, ok = QInputDialog.getItem(self, "Редактировать кандидата", "Выберите ID кандидата:", candidate_ids, 0, False)

        if ok:
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать кандидата")
            layout = QVBoxLayout()

            name_input = QLineEdit(candidates[int(selected_id) - 1][1])
            skills_input = QLineEdit(candidates[int(selected_id) - 1][2])
            experience_input = QLineEdit(str(candidates[int(selected_id) - 1][3]))

            def update_candidate():
                name = name_input.text().strip()
                skills = skills_input.text().strip()
                experience = experience_input.text().strip()
                if not name or not skills or not experience.isdigit():
                    QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                    return
                self.db.edit_candidate(int(selected_id), name, skills, int(experience))
                QMessageBox.information(dialog, "Успех", "Данные кандидата обновлены!")
                dialog.accept()

            submit_btn = QPushButton("Сохранить")
            submit_btn.clicked.connect(update_candidate)

            layout.addWidget(name_input)
            layout.addWidget(skills_input)
            layout.addWidget(experience_input)
            layout.addWidget(submit_btn)
            dialog.setLayout(layout)
            dialog.exec_()

    def show_candidates(self):
        self.show_table("Кандидаты", self.db.get_candidates())

    def show_vacancies(self):
        self.show_table("Вакансии", self.db.get_vacancies())

    def show_match_candidates(self):
        vacancies = self.db.get_vacancies()
        vacancy_titles = [v[1] for v in vacancies]
        selected_vacancy, ok = QInputDialog.getItem(self, "Подбор кандидатов", "Выберите вакансию:", vacancy_titles, 0, False)

        if ok:
            vacancy = next(v for v in vacancies if v[1] == selected_vacancy)
            candidates = self.db.find_matching_candidates(vacancy[3])
            self.show_table("Подходящие кандидаты", candidates)

    def show_table(self, title, data):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()

        table = QTableWidget()
        if data:
            table.setRowCount(len(data))
            table.setColumnCount(len(data[0]))
            for row, record in enumerate(data):
                for col, item in enumerate(record):
                    table.setItem(row, col, QTableWidgetItem(str(item)))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication([])
    window = HRApp()
    window.show()
    app.exec_()