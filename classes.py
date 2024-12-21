"""Модуль, где инициализируются классы"""

# Модели данных для кандидатов и вакансий
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