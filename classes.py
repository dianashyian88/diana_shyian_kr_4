from abc import ABC, abstractmethod
import requests
import json
import os


class API(ABC):
    """
    Абстрактный класс для работы с API сайтов с вакансиями
    """

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def get_formatted_vacancies(self):
        pass


class HeadHunterAPI(API):
    """
    Класс для работы с API сайта hh.ru
    """
    def __init__(self, keyword):
        self.keyword = keyword

    def get_vacancies(self):
        """
        Метод для получения списка вакансий с сайта hh.ru
        """
        v_hh = []
        for page in range(1, 3):
            url = 'https://api.hh.ru/vacancies'
            params = {
                'page': page,
                'per_page': 2,
                'text': self.keyword,
                'type': 'open'
            }
            response = requests.get(url, params=params).json()
            v_hh.extend(response['items'])
        return v_hh

    def save_all_vacancy(self):
        """
        Метод для сохранения полученного полного списка вакансий с сайта hh.ru в файле json
        """
        with open('all_vacancy.json', 'w') as file:
            json.dump(self.get_vacancies(), file, indent=2, ensure_ascii=False)

    def get_formatted_vacancies(self):
        """
        Метод для получения отформатированного списка вакансий с сайта hh.ru
        """
        formatted_v_hh = []
        for vacancy in self.get_vacancies():
            try:
                formatted_v_hh.append({
                    'name': vacancy['name'],
                    'url': vacancy['alternate_url'],
                    'salary_from': vacancy['salary']['from'],
                    'salary_to': vacancy['salary']['to'],
                    'salary_cur': vacancy['salary']['currency'].upper(),
                    'requirement': vacancy['snippet']['requirement'],
                    'experience': vacancy['experience']['name'],
                    'employment': vacancy['employment']['name'],
                    'source': 'hh.ru'
                })
            except TypeError:
                formatted_v_hh.append({
                    'name': vacancy['name'],
                    'url': vacancy['alternate_url'],
                    'salary_from': None,
                    'salary_to': None,
                    'salary_cur': None,
                    'requirement': vacancy['snippet']['requirement'],
                    'experience': vacancy['experience']['name'],
                    'employment': vacancy['employment']['name'],
                    'source': 'hh.ru'
                })
        return formatted_v_hh


class SuperJobAPI(API):
    """
    Класс для работы с API сайта superjob.ru
    """
    api_key: str = os.getenv('SJ_API_KEY')

    def __init__(self, keyword):
        self.keyword = keyword

    def get_vacancies(self):
        """
        Метод для получения списка вакансий с сайта superjob.ru
        """
        v_sj = []
        for page in range(1, 3):
            url = 'https://api.superjob.ru/2.0/vacancies'
            params = {
                'count': 2,
                'page': page,
                'keyword': self.keyword,
                'archive': False
            }
            headers = {
                'X-Api-App-Id': SuperJobAPI.api_key
            }
            response = requests.get(url, headers=headers, params=params).json()
            v_sj.extend(response['objects'])
        return v_sj

    def save_all_vacancy(self):
        """
        Метод для сохранения полученного полного списка вакансий с сайта superjob.ru в файле json
        """
        with open('all_vacancy.json', 'w') as file:
            json.dump(self.get_vacancies(), file, indent=2, ensure_ascii=False)

    def get_formatted_vacancies(self):
        """
        Метод для получения отформатированного списка вакансий с сайта superjob.ru
        """
        formatted_v_sj = []
        for vacancy in self.get_vacancies():
            formatted_v_sj.append({
                'name': vacancy['profession'],
                'url': vacancy['link'],
                'salary_from': vacancy['payment_from'],
                'salary_to': vacancy['payment_to'],
                'salary_cur': vacancy['currency'].upper(),
                'requirement': vacancy['candidat'],
                'experience': vacancy['experience']['title'],
                'employment': vacancy['type_of_work']['title'],
                'source': 'superjob.ru'
            })
        return formatted_v_sj


class Saver(ABC):
    """
    Абстрактный класс для работы с файлом с вакансиями
    """

    @abstractmethod
    def create_file(self, all_vacancies):
        pass


class Vacancy:
    """
    Класс для работы с вакансиями
    """
    def __init__(self, vacancy):
        self.name = vacancy['name']
        self.url = vacancy['url']
        self.salary_from = vacancy['salary_from']
        self.salary_to = vacancy['salary_to']
        self.requirement = vacancy['requirement']
        self.experience = vacancy['experience']
        self.employment = vacancy['employment']
        self.source = vacancy['source']
        if self.salary_from is not None and self.salary_from != 0 and self.salary_to is not None and self.salary_to != 0:
            self.salary = str(self.salary_from) + '-' + str(self.salary_to)
        elif self.salary_from is not None and self.salary_from != 0 and (self.salary_to is None or self.salary_to == 0):
            self.salary = str(self.salary_from)
        elif (self.salary_from is None or self.salary_from == 0) and self.salary_to is not None and self.salary_to != 0:
            self.salary = str(self.salary_to)
        else:
            self.salary = 'Не указана'

    def __str__(self):
        return f"""Наименование вакансии: {self.name}
Ссылка на вакансию: {self.url}
Заработная плата в рос. рублях: {self.salary}
Описание вакансии: {self.requirement}
Требования к опыту работы: {self.experience}
Тип занятости: {self.employment}
Источник: {self.source}
"""


class JSONSaver(Saver):
    """
    Класс для работы с json-файлом с вакансиями
    """
    def __init__(self, filename, all_vacancies):
        self.filename = filename + '.json'
        self.create_file(all_vacancies)

    def create_file(self, all_vacancies):
        with open(f'data/{self.filename}', 'w') as file:
            json.dump(all_vacancies, file, indent=2, ensure_ascii=False)

    def select_file(self):
        with open(f'data/{self.filename}', 'r') as file:
            data = json.load(file)
        vacancy_data = [Vacancy(x) for x in data]
        return vacancy_data
