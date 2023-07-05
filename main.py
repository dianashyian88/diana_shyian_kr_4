from classes import HeadHunterAPI, SuperJobAPI, JSONSaver


def user_interaction():
    keyword = input('Здравствуйте!\nВведите ключевое слово для поиска ')

    #Создание экземпляра класса для работы с API сайтов с вакансиями
    hh_api = HeadHunterAPI(keyword)
    sj_api = SuperJobAPI(keyword)

    source = input('''\nПоиск осуществляется по сайтам hh.ru и superjob.ru. 
Введите 1 - для получения информации с сайта hh.ru, 
2 - для получения информации с сайта superjob.ru, 
или нажмите ENTER ''')

    #Получение списка вакансий в зависимости от выбранного пользователем ресурса
    if source == str(1):
        all_vacancies = hh_api.get_formatted_vacancies()
    elif source == str(2):
        all_vacancies = sj_api.get_formatted_vacancies()
    else:
        all_vacancies = hh_api.get_formatted_vacancies() + sj_api.get_formatted_vacancies()

    #Сохранение информации о вакансиях в файл
    json_saver = JSONSaver(keyword, all_vacancies)

    #Получение вакансий из файла
    while True:
        param = input('''\nПолучить все вакансии - введите 1
Получить все вакансии, отсортированные по убыванию размера заработной платы - введите 2
Получить 10 вакансий с самой высокой заработной платой - введите 3
Получить вакансии с полной занятостью - введите 4
Удалить вакансии с незаполненной или нулевой заработной платой - введите 5
Для завершения нажмите ENTER ''')
        if param == str(1):
            vacancies = json_saver.select_file()
        elif param == str(2):
            vacancies = json_saver.sorted_by_salary()
        elif param == str(3):
            vacancies = json_saver.get_top_10_vacancy()
        elif param == str(4):
            vacancies = json_saver.get_vacancy_full_emp()
        elif param == str(5):
            vacancies = json_saver.delete_vacancy()
        else:
            print('\nДо новых встреч!')
            break
        for v in vacancies:
            print(f'\n{v}')


if __name__ == '__main__':
    user_interaction()
