"""Модуль для работы с базой данных"""

import json
import sqlite3
from classes import Candidate, Vacancy

# Класс для работы с базой данных
class HRDatabase:
    def __init__(self, db_name="кадровое агентство сельгира.db"):
        self.conn = sqlite3.connect(db_name)  # Подключение к базе данных
        self.create_tables()  # Создание таблиц при инициализации базы данных

    def create_tables(self):
        # Создание таблиц в базе данных (если их нет)
        with self.conn:
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

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            if filename.endswith('.json'):
                data = json.load(file)
            elif filename.endswith('.txt'):
                import ast
                data = ast.literal_eval(file.read())
            else:
                raise ValueError("Поддерживаются только файлы .json или .txt")

        # Очистка таблиц перед загрузкой
        with self.conn:
            self.conn.execute("DELETE FROM Candidates")
            self.conn.execute("DELETE FROM Vacancies")

        # Загрузка данных в базу
        candidates = data.get('candidates', [])
        vacancies = data.get('vacancies', [])

        for candidate in candidates:
            self.add_candidate(Candidate(candidate['name'], candidate['skills'], candidate['experience']))

        for vacancy in vacancies:
            self.add_vacancy(Vacancy(vacancy['title'], vacancy['employer_id'], vacancy['requirements']))

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
