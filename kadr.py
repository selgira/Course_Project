import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QInputDialog)
from PyQt5.QtCore import Qt

# Модели данных для кандидатов, работодателей и вакансий
class Employer:
    def __init__(self, name, industry, description):
        self.name = name  # Название работодателя
        self.industry = industry  # Отрасль
        self.description = description  # Описание работодателя

class Candidate:
    def __init__(self, name, skills, experience):
        self.name = name  # Имя кандидата
        self.skills = skills  # Навыки кандидата
        self.experience = experience  # Опыт кандидата (в годах)

class Vacancy:
    def __init__(self, title, employer_id, requirements):
        self.title = title  # Название вакансии
        self.employer_id = employer_id  # ID работодателя, которому принадлежит вакансия
        self.requirements = requirements  # Требования к вакансии

# Класс для работы с базой данных
class HRDatabase:
    def __init__(self, db_name="кадровое агентство сельгира.db"):
        self.conn = sqlite3.connect(db_name)  # Подключение к базе данных
        self.create_tables()  # Создание таблиц при инициализации базы данных

    def create_tables(self):
        # Создание таблиц в базе данных (если их нет)
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
        # Добавление нового кандидата в базу данных (если его нет)
        with self.conn:
            existing_candidates = self.conn.execute("SELECT * FROM Candidates WHERE name = ?",
                                                    (candidate.name,)).fetchall()
            if not existing_candidates:  # Если кандидат еще не существует в базе
                self.conn.execute("INSERT INTO Candidates (name, skills, experience) VALUES (?, ?, ?)",
                                  (candidate.name, candidate.skills, candidate.experience))

    def add_vacancy(self, vacancy: Vacancy):
        # Добавление новой вакансии в базу данных (если она не существует)
        with self.conn:
            existing_vacancies = self.conn.execute("SELECT * FROM Vacancies WHERE title = ?", (vacancy.title,)).fetchall()
            if not existing_vacancies:  # Если вакансия еще не существует в базе
                self.conn.execute("INSERT INTO Vacancies (title, employer_id, requirements) VALUES (?, ?, ?)",
                                  (vacancy.title, vacancy.employer_id, vacancy.requirements))

    def get_candidates(self, skill_filter=None):
        # Получение всех кандидатов (или кандидатов с определенными навыками)
        with self.conn:
            if skill_filter:
                return self.conn.execute("SELECT * FROM Candidates WHERE skills LIKE ?", (f"%{skill_filter}%",)).fetchall()
            return self.conn.execute("SELECT * FROM Candidates").fetchall()

    def edit_candidate(self, candidate_id, name, skills, experience):
        # Редактирование данных кандидата
        with self.conn:
            self.conn.execute('''UPDATE Candidates 
                                 SET name = ?, skills = ?, experience = ? 
                                 WHERE id = ?''', (name, skills, experience, candidate_id))

    def get_vacancies(self):
        # Получение всех вакансий
        with self.conn:
            return self.conn.execute("SELECT * FROM Vacancies").fetchall()

    def find_matching_candidates(self, requirements):
        # Поиск кандидатов, соответствующих требованиям вакансии
        with self.conn:
            return self.conn.execute('''SELECT * FROM Candidates WHERE skills LIKE ?''', (f"%{requirements}%",)).fetchall()

    def add_vacancy(self, vacancy: Vacancy):
        with self.conn:
            self.conn.execute("INSERT INTO Vacancies (title, employer_id, requirements) VALUES (?, ?, ?)",
                              (vacancy.title, vacancy.employer_id, vacancy.requirements))

    def find_vacancies_by_skill(self, skills):
        # Поиск вакансий по навыкам
        skill_list = [skill.strip() for skill in skills.split(',')]  # Разделение навыков по запятой
        query = "SELECT * FROM Vacancies WHERE " + " AND ".join(
            ["requirements LIKE ?" for _ in skill_list])
        params = [f"%{skill}%" for skill in skill_list]
        with self.conn:
            return self.conn.execute(query, tuple(params)).fetchall()

    def find_matching_candidates(self, skills):
        # Поиск кандидатов по навыкам
        skill_list = [skill.strip() for skill in skills.split(',')]  # Разделение навыков по запятой
        query = "SELECT * FROM Candidates WHERE " + " AND ".join(
            ["skills LIKE ?" for _ in skill_list])
        params = [f"%{skill}%" for skill in skill_list]
        with self.conn:
            return self.conn.execute(query, tuple(params)).fetchall()

# Главный класс приложения
class HRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кадровое агентство")  # Устанавливаем заголовок окна
        self.db = HRDatabase()  # Создание объекта базы данных
        self.init_ui()  # Инициализация пользовательского интерфейса

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        label = QLabel('Добро пожаловать в кадровое агентство "SELA"!')  # Приветственное сообщение
        label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(label)
        main_widget.setLayout(main_layout)

        # Основной горизонтальный макет для разделения блоков
        main_horizontal_layout = QHBoxLayout()

        # Блок для кандидатов
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

        # Блок для вакансий
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

        # Кнопка для поиска вакансий и кандидатов
        match_vacancies_btn = QPushButton("Поиск вакансий и кандидатов")
        match_vacancies_btn.clicked.connect(self.show_match_candidates)

        # Добавление столбцов и кнопок в основной макет
        main_horizontal_layout.addLayout(candidates_layout)
        main_horizontal_layout.addLayout(vacancies_layout)

        main_layout.addLayout(main_horizontal_layout)
        main_layout.addWidget(match_vacancies_btn)

        main_widget.setLayout(main_layout)

    def show_edit_vacancy_dialog(self):
        # Диалоговое окно для редактирования вакансий
        vacancies = self.db.get_vacancies()
        vacancy_ids = [str(v[0]) for v in vacancies]
        selected_id, ok = QInputDialog.getItem(self, "Редактировать вакансию", "Выберите ID вакансии:", vacancy_ids, 0,
                                               False)

        if ok:
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать вакансию")
            layout = QVBoxLayout()
            vacancy = next(v for v in vacancies if v[0] == int(selected_id))

            title_input = QLineEdit(vacancy[1])  # Название вакансии
            employer_input = QLineEdit(str(vacancy[2]))  # ID работодателя
            requirements_input = QLineEdit(vacancy[3])  # Требования к вакансии

            def update_vacancy():
                # Обновление данных вакансии
                title = title_input.text().strip()
                employer_id = employer_input.text().strip()
                requirements = requirements_input.text().strip()
                if not title or not employer_id.isdigit() or not requirements:
                    QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                    return
                self.db.conn.execute('''UPDATE Vacancies 
                                                SET title = ?, employer_id = ?, requirements = ? 
                                                WHERE id = ?''',
                                     (title, int(employer_id), requirements, int(selected_id)))
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
        # Создаем диалоговое окно для добавления вакансии
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить вакансию")
        layout = QVBoxLayout()

        # Создаем поля ввода для описания вакансии, ID работодателя и требований
        title_input = QLineEdit()
        title_input.setPlaceholderText("Описание (через запятую)")
        employer_input = QLineEdit()
        employer_input.setPlaceholderText("ID работодателя")
        requirements_input = QLineEdit()
        requirements_input.setPlaceholderText("Требования")

        # Функция для добавления вакансии в базу данных
        def add_vacancy():
            title = title_input.text().strip()
            employer_id = employer_input.text().strip()
            requirements = requirements_input.text().strip()

            # Проверка корректности введенных данных
            if not title or not employer_id.isdigit() or not requirements:
                QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                return

            # Создаем объект вакансии и добавляем его в базу данных
            vacancy = Vacancy(title, int(employer_id), requirements)
            self.db.add_vacancy(vacancy)

            # Показываем сообщение об успешном добавлении вакансии
            QMessageBox.information(dialog, "Успех", "Вакансия добавлена!")
            dialog.accept()

        # Создаем кнопку для добавления вакансии
        submit_btn = QPushButton("Добавить")
        submit_btn.clicked.connect(add_vacancy)

        layout.addWidget(title_input)
        layout.addWidget(employer_input)
        layout.addWidget(requirements_input)
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_add_candidate_dialog(self):
        # Создаем диалоговое окно для добавления нового кандидата
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить кандидата")  # заголовок окна
        layout = QVBoxLayout()
        # Создаем поля ввода для имени, навыков и опыта кандидата
        name_input = QLineEdit()
        name_input.setPlaceholderText("Имя (Имя и Фамилия)")
        skills_input = QLineEdit()
        skills_input.setPlaceholderText("Навыки")
        experience_input = QLineEdit()
        experience_input.setPlaceholderText("Опыт (в годах)")

        # Функция для добавления нового кандидата в базу данных
        def add_candidate():
            name = name_input.text().strip()
            skills = skills_input.text().strip()
            experience = experience_input.text().strip()
            # Проверка корректности введенных данных
            if not name or not skills or not experience.isdigit():
                QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                return
            # Создаем объект кандидата и добавляем его в базу данных
            candidate = Candidate(name, skills, int(experience))
            self.db.add_candidate(candidate)
            # Показываем сообщение об успешном добавлении кандидата
            QMessageBox.information(dialog, "Успех", "Кандидат добавлен!")
            dialog.accept()  # Закрываем диалог

        # Создаем кнопку для добавления кандидата
        submit_btn = QPushButton("Добавить")
        submit_btn.clicked.connect(add_candidate)  # Привязываем действие кнопки к функции

        layout.addWidget(name_input)
        layout.addWidget(skills_input)
        layout.addWidget(experience_input)
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_edit_candidate_dialog(self):
        # Получаем список всех кандидатов из базы данных
        candidates = self.db.get_candidates()
        candidate_ids = [str(c[0]) for c in candidates]  # Извлекаем ID кандидатов для выбора

        selected_id, ok = QInputDialog.getItem(self, "Редактировать кандидата", "Выберите ID кандидата:", candidate_ids,
                                               0, False)

        if ok:
            # диалоговое окно для редактирования данных выбранного кандидата
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать кандидата")
            layout = QVBoxLayout()

            # Заполняем поля ввода текущими данными кандидата
            name_input = QLineEdit(candidates[int(selected_id) - 1][1])
            skills_input = QLineEdit(candidates[int(selected_id) - 1][2])
            experience_input = QLineEdit(str(candidates[int(selected_id) - 1][3]))

            # Функция для обновления данных кандидата в базе данных
            def update_candidate():
                name = name_input.text().strip()
                skills = skills_input.text().strip()
                experience = experience_input.text().strip()
                # Проверка корректности введенных данных
                if not name or not skills or not experience.isdigit():
                    QMessageBox.warning(dialog, "Ошибка", "Введите корректные данные!")
                    return
                # Обновляем данные кандидата в базе данных
                self.db.edit_candidate(int(selected_id), name, skills, int(experience))
                # Показываем сообщение об успешном обновлении данных
                QMessageBox.information(dialog, "Успех", "Данные кандидата обновлены!")
                dialog.accept()

            # Создаем кнопку для сохранения изменений
            submit_btn = QPushButton("Сохранить")
            submit_btn.clicked.connect(update_candidate)  # Привязываем действие кнопки к функции

            layout.addWidget(name_input)
            layout.addWidget(skills_input)
            layout.addWidget(experience_input)
            layout.addWidget(submit_btn)
            dialog.setLayout(layout)
            dialog.exec_()

    def show_candidates(self):
        # Отображаем таблицу с кандидатами, получая данные из базы
        self.show_table("Кандидаты", self.db.get_candidates())

    def show_vacancies(self):
        # Отображаем таблицу с вакансиями, получая данные из базы
        self.show_table("Вакансии", self.db.get_vacancies())

    def show_match_candidates(self):
        # Диалог для выбора категории поиска (вакансии или кандидаты)
        category, ok = QInputDialog.getItem(
            self,
            "Поиск",
            "Выберите категорию для поиска:",
            ["Поиск вакансий", "Поиск кандидатов"],
            0,
            False
        )
        if ok and category:
            # Диалог для ввода навыка, по которому будет производиться поиск
            skill, ok = QInputDialog.getText(self, f"Поиск для {category}", "Введите навык (например, Python):")
            if ok and skill.strip():
                skill = skill.strip()  # лишние пробелы
                # В зависимости от выбранной категории поиска, выполняем поиск по навыку
                if category == "Поиск вакансий":
                    results = self.db.find_vacancies_by_skill(skill)  # Ищем вакансии по навыку
                    self.show_table(f"Вакансии для навыка: {skill}", results)
                elif category == "Поиск кандидатов":
                    results = self.db.find_matching_candidates(skill)  # Ищем кандидатов по навыку
                    self.show_table(f"Кандидаты для навыка: {skill}", results)

    def show_table(self, title, data):
        # Отображаем таблицу с данными (например, кандидаты или вакансии)
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        table = QTableWidget()
        if data:
            # Если данные есть, устанавливаем количество строк и столбцов
            table.setRowCount(len(data))
            table.setColumnCount(len(data[0]))
            for row, record in enumerate(data):
                for col, item in enumerate(record):
                    table.setItem(row, col, QTableWidgetItem(str(item)))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    #данные для заполнения базы
    candidates = [
        Candidate("Сельгира Сангаджи-Горяева", "Python, Django, SQL", 5),
        Candidate("Мария Смирнова", "JavaScript, React, HTML, CSS", 3),
        Candidate("Алексей Кузнецов", "Java, Spring, MySQL", 4),
        Candidate("Елена Попова", "C++, Qt, OpenGL", 7),
        Candidate("Дмитрий Сидоров", "Python, Flask, Docker", 6),
        Candidate("Анна Петрова", "Project Management, Agile, Scrum", 8),
        Candidate("Максим Волков", "JavaScript, Node.js, MongoDB", 2),
        Candidate("Светлана Николаева", "Python, Machine Learning, TensorFlow", 4),
        Candidate("Ольга Васильева", "PHP, Laravel, SQL", 5),
        Candidate("Григорий Крылов", "C#, .NET, Azure", 3),
        Candidate("Наталья Орлова", "Data Analysis, Python, SQL", 6),
        Candidate("Павел Михайлов", "DevOps, AWS, Kubernetes", 5),
        Candidate("Виктория Сергеева", "UI/UX Design, Figma, Adobe XD", 2),
        Candidate("Николай Романов", "Java, Android Development", 4),
        Candidate("Ирина Шестакова", "Marketing, SEO, Google Analytics", 7)
    ]

    vacancies = [
        Vacancy("Backend-разработчик", 1, "Python, Django, SQL"),
        Vacancy("Frontend-разработчик", 2, "JavaScript, React, HTML, CSS"),
        Vacancy("Java-разработчик", 3, "Java, Spring, MySQL"),
        Vacancy("C++ разработчик", 4, "C++, Qt, OpenGL"),
        Vacancy("DevOps-инженер", 5, "DevOps, AWS, Kubernetes"),
        Vacancy("Data Scientist", 6, "Python, Machine Learning, TensorFlow"),
        Vacancy("PHP-разработчик", 7, "PHP, Laravel, SQL"),
        Vacancy("Project Manager", 8, "Project Management, Agile, Scrum"),
        Vacancy("UI/UX Designer", 9, "UI/UX Design, Figma, Adobe XD"),
        Vacancy("Mobile-разработчик", 10, "Java, Android Development"),
        Vacancy("Маркетолог", 11, "Marketing, SEO, Google Analytics"),
        Vacancy("Системный аналитик", 12, "Data Analysis, Python, SQL"),
        Vacancy("Cloud Engineer", 13, "C#, .NET, Azure"),
        Vacancy("Fullstack-разработчик", 14, "JavaScript, Node.js, MongoDB"),
        Vacancy("Python-разработчик", 15, "Python, Flask, Docker")
    ]

    # заливаем данные в базу только если таблицы пусты
    db = HRDatabase()  # создаём объект для работы с базой данных

    # проверяем, есть ли кандидаты в базе
    existing_candidates = db.get_candidates()
    if not existing_candidates:
        # если кандидаты не найдены, добавляем их
        for candidate in candidates:
            db.add_candidate(candidate)  # добавляем кандидата в базу

    # проверяем, есть ли вакансии в базе
    existing_vacancies = db.get_vacancies()
    if not existing_vacancies:
        # если вакансии не найдены, добавляем их
        for idx, vacancy in enumerate(vacancies, start=1):
            vacancy.employer_id = idx  # связываем вакансии с работодателями (например, уникальные ID)
            db.add_vacancy(vacancy)  # добавляем вакансию в базу

# основной блок для запуска приложения
if __name__ == "__main__":
    app = QApplication([])
    window = HRApp()
    window.show()
    app.exec_()