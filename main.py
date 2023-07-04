from classes import HeadHunterAPI, SuperJobAPI, JSONSaver


if __name__ == '__main__':
    keyword = input('Введите ключевое слово для поиска ')

    #Создание экземпляра класса для работы с API сайтов с вакансиями
    hh_api = HeadHunterAPI(keyword)
    sj_api = SuperJobAPI(keyword)

    source = input('''Поиск осуществляется по сайтам hh.ru и superjob.ru. 
Введите 1 - для ограничения поиска по hh.ru, 
2 - для ограничения поиска по superjob.ru, 
или нажмите ENTER ''')

    #Получение списка вакансий в зависимости от выбранного пользователем ресурса
    if source == 1:
        all_vacancies = hh_api.get_formatted_vacancies()
    elif source == 2:
        all_vacancies = sj_api.get_formatted_vacancies()
    else:
        all_vacancies = hh_api.get_formatted_vacancies() + sj_api.get_formatted_vacancies()

    #Сохранение информации о вакансиях в файл
    JS = JSONSaver(keyword, all_vacancies)

    #Получение вакансий из файла
    vacancies = JS.select_file()
    for v in vacancies:
        print(v)
