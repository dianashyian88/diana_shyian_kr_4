from abc import ABC, abstractmethod
import requests
import json
import os
from datetime import datetime


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
        for page in range(1, 11):
            url = 'https://api.hh.ru/vacancies'
            params = {
                'page': page,
                'per_page': 100,
                'text': self.keyword,
                'type': 'open'
            }
            response = requests.get(url, params=params).json()
            v_hh.extend(response['items'])
        return v_hh

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
                    'salary_cur': vacancy['salary']['currency'].lower(),
                    'employer': vacancy['employer']['name'],
                    'requirement': vacancy['snippet']['requirement'],
                    'experience': vacancy['experience']['name'],
                    'employment': vacancy['employment']['name'],
                    'area': vacancy['area']['name'],
                    'source': 'hh.ru'
                })
            except TypeError:
                formatted_v_hh.append({
                    'name': vacancy['name'],
                    'url': vacancy['alternate_url'],
                    'salary_from': None,
                    'salary_to': None,
                    'salary_cur': None,
                    'employer': vacancy['employer']['name'],
                    'requirement': vacancy['snippet']['requirement'],
                    'experience': vacancy['experience']['name'],
                    'employment': vacancy['employment']['name'],
                    'area': vacancy['area']['name'],
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
        for page in range(1, 11):
            url = 'https://api.superjob.ru/2.0/vacancies'
            params = {
                'count': 100,
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
                'salary_cur': vacancy['currency'].lower(),
                'employer': vacancy['firm_name'],
                'requirement': vacancy['candidat'],
                'experience': vacancy['experience']['title'],
                'employment': vacancy['type_of_work']['title'],
                'area': vacancy['town']['title'],
                'source': 'superjob.ru'
            })
        return formatted_v_sj


class Vacancy:
    """
    Класс для работы с вакансиями
    """
    def __init__(self, vacancy):
        self.name = vacancy['name']
        self.url = vacancy['url']
        self.salary_from = self.get_salary_from(vacancy)
        self.salary_to = self.get_salary_to(vacancy)
        self.salary = self.get_salary(self.salary_from, self.salary_to)
        self.employer = vacancy['employer']
        self.requirement = vacancy['requirement']
        self.experience = vacancy['experience']
        self.employment = vacancy['employment']
        self.area = vacancy['area']
        self.source = vacancy['source']

    def __str__(self):
        return f"""Наименование вакансии: {self.name}
Ссылка на вакансию: {self.url}
Заработная плата в рос. рублях: {self.salary}
Работодатель: {self.employer}
Описание вакансии: {self.requirement}
Требования к опыту работы: {self.experience}
Тип занятости: {self.employment}
Местоположение: {self.area}
Источник: {self.source}
"""

    def get_salary_from(self, vacancy):
        """
        Метод для определения salary_from в российских рублях
        """
        if vacancy['salary_from'] is not None and vacancy['salary_cur'] is not None:
            if vacancy['salary_cur'] == 'rur':
                salary_from = vacancy['salary_from']
            else:
                salary_from = round(vacancy['salary_from'] / self.get_currency_rate(vacancy['salary_cur']))
        elif vacancy['salary_from'] is None and vacancy['salary_to'] is not None and vacancy['salary_cur'] is not None:
            if vacancy['salary_cur'] == 'rur':
                salary_from = vacancy['salary_to']
            else:
                salary_from = round(vacancy['salary_to'] / self.get_currency_rate(vacancy['salary_cur']))
        else:
            salary_from = 0
        return salary_from

    def get_salary_to(self, vacancy):
        """
        Метод для определения salary_to в российских рублях
        """
        if vacancy['salary_to'] is not None and vacancy['salary_cur'] is not None:
            if vacancy['salary_cur'] == 'rur':
                salary_to = vacancy['salary_to']
            else:
                salary_to = round(vacancy['salary_to'] / self.get_currency_rate(vacancy['salary_cur']))
        else:
            salary_to = 0
        return salary_to

    @staticmethod
    def get_salary(salary_from, salary_to):
        """
        Метод для определения salary в российских рублях в удобном для пользователя формате
        """
        if salary_from != 0 and salary_to != 0 and salary_from != salary_to:
            salary = str(salary_from) + '-' + str(salary_to)
        elif salary_from != 0 and salary_to != 0 and salary_from == salary_to:
            salary = str(salary_from)
        elif salary_from != 0 and salary_to == 0:
            salary = str(salary_from)
        elif salary_from == 0 and salary_to != 0:
            salary = str(salary_to)
        else:
            salary = 'Не указана'
        return salary

    @staticmethod
    def get_currency_rate(currency):
        """
        Метод для получения курса валюты заработной платы к российскому рублю
        """
        current_date = datetime.now().date()
        url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/' + str(current_date) + '/currencies/rub.json'
        response = requests.get(url).json()
        currency_rate = response['rub'][currency]
        return currency_rate

    def __gt__(self, other):
        """
        Метод определяет поведение оператора больше
        """
        return self.salary_from > other.salary_from

    def __lt__(self, other):
        """
        Метод определяет поведение оператора меньше
        """
        return self.salary_from < other.salary_from


class Saver(ABC):
    """
    Абстрактный класс для работы с файлом с вакансиями
    """

    @abstractmethod
    def create_file(self, all_vacancies):
        pass

    @abstractmethod
    def select_file(self):
        pass

    @abstractmethod
    def delete_vacancy(self):
        pass


class JSONSaver(Saver):
    """
    Класс для работы с json-файлом с вакансиями
    """
    def __init__(self, filename, all_vacancies):
        self.filename = filename + '.json'
        self.create_file(all_vacancies)

    def create_file(self, all_vacancies):
        """
        Метод для сохранения отформатированного списка вакансий в json-файл
        """
        with open(f'data/{self.filename}', 'w', encoding='utf-8') as file:
            json.dump(all_vacancies, file, indent=2, ensure_ascii=False)

    def select_file(self):
        """
        Метод для получения полного списка вакансий из json-файла
        """
        with open(f'data/{self.filename}', 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancy_data = [Vacancy(x) for x in data]
        return vacancy_data

    def sorted_by_salary(self):
        """
        Метод для получения из json-файла списка вакансий, отсортированных по убыванию заработной платы
        """
        vacancy_data = self.select_file()
        sorted_vacancy_data = sorted(vacancy_data, key=lambda vacancy: vacancy.salary_from, reverse=True)
        return sorted_vacancy_data

    def get_top_10_vacancy(self):
        """
        Метод для получения из json-файла десяти вакансий с наибольшим размером заработной платы
        """
        sorted_vacancy_data = self.sorted_by_salary()
        return sorted_vacancy_data[:10]

    def get_vacancy_full_emp(self):
        """
        Метод для получения из json-файла вакансий с полной занятостью
        """
        full_emp_vacancy_data = []
        sorted_vacancy_data = self.sorted_by_salary()
        for vacancy in sorted_vacancy_data:
            if vacancy.employment == 'Полная занятость' or vacancy.employment == 'Полный рабочий день':
                full_emp_vacancy_data.append(vacancy)
        return full_emp_vacancy_data

    def delete_vacancy(self):
        """
        Метод для удаления из json-файла вакансий с незаполненной или нулевой заработной платой
        """
        update_vacancy_data = []
        with open(f'data/{self.filename}', 'r') as file:
            data = json.load(file)
        for item in data:
            if item['salary_from'] is not None and item['salary_from'] != 0:
                update_vacancy_data.append(item)
            elif item['salary_to'] is not None and item['salary_to'] != 0:
                update_vacancy_data.append(item)
        self.create_file(update_vacancy_data)
        return self.sorted_by_salary()
