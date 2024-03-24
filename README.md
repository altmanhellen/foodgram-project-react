![Build Status](https://github.com/altmanhellen/foodgram-project-react/actions/workflows/master.yml/badge.svg)

# Описание

Foodgram - платформа управления рецептами. Включает в себя функционал создания, просмотра и редактирования рецептов. Рецепты можно фильтровать по тегам «Завтрак», «Обед», «Ужин», добавлять в «Избранное», а также в список покупок. Список покупок можно скачать (необходимое количество ингредиентов для всех рецептов будут для удобства суммированы). Проект предлагает функционал авторизации и аутентификации пользователей⁠.

# Установка

1. Клонируйте репозиторий проекта на ваш локальный компьютер.

2. Перейдите в корневую директорию проекта.

3. Создайте файл .env в корневой директории. Используя .env.example в качестве шаблона, заполните необходимые переменные окружения.

4. Запустите все контейнеры с помощью Docker Compose:

```
docker-compose up -d
```

После запуска контейнеров проект будет доступен по адресу https://foodgram-alt.zapto.org.

# Примеры запросов к API

### Регистрация пользователя

POST .../api/users/
```
{
    "email": "yourmail@mail.com",
    "username": "your-username",
    "first_name": "YourFirstName",
    "last_name": "YourLastName",
    "password": "your-password"
}
```

Результат:
```
{
    "email": "yourmail@mail.com",
    "username": "your-username",
    "first_name": "YourFirstName",
    "last_name": "YourLastName",
    "id": 4
}
```

### Получение токена

POST .../api/token/login/
```
{
    "email": "yourmail@mail.com",
    "password": "your-password"
}
```

Результат
```
{"auth_token":"hereyouseegeneratedtokenfromdigitsandletters387465493"}
```

### Получить список всех рецептов для обеда

GET .../api/recipes/?page=1&limit=2&tags=lunch

Результат
```
{
    "count": 8,
    "next": "http://foodgram-yap.zapto.org/api/recipes/?limit=2&page=2&tags=lunch",
    "previous": null,
    "results": [
        {
            "id": 14,
            "tags": [
                {
                    "id": 2,
                    "name": "Обед",
                    "color": "#F7CB15",
                    "slug": "lunch"
                },
                {
                    "id": 3,
                    "name": "Ужин",
                    "color": "#76BED0",
                    "slug": "dinner"
                }
            ],
            "author": {
                "id": 5,
                "email": "igorantipin@mail.ru",
                "username": "igorantipin",
                "first_name": "Игорь",
                "last_name": "Антипин",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 1881,
                    "amount": 200,
                    "name": "тунец консервированный",
                    "measurement_unit": "г"
                },
                {
                    "id": 557,
                    "amount": 150,
                    "name": "картофель вареный",
                    "measurement_unit": "г"
                },
                {
                    "id": 2182,
                    "amount": 40,
                    "name": "яйца куриные",
                    "measurement_unit": "г"
                },
                {
                    "id": 1053,
                    "amount": 80,
                    "name": "морковь",
                    "measurement_unit": "г"
                },
                {
                    "id": 899,
                    "amount": 80,
                    "name": "майонез",
                    "measurement_unit": "г"
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "Салат «Мимоза»",
            "image": "http://foodgram-yap.zapto.org/media/recipes/temp_NcUZqr4.jpeg",
            "text": "Вкусный, яркий, любимый — на праздничный стол! Салат Мимоза с тунцом не менее аппетитный, чем с привычной консервированной сайрой. Отличный выбор для любителей рыбных салатов не только в праздник, но и для семейного ужина.",
            "cooking_time": 60
        },
        {
            "id": 13,
            "tags": [
                {
                    "id": 2,
                    "name": "Обед",
                    "color": "#F7CB15",
                    "slug": "lunch"
                },
                {
                    "id": 3,
                    "name": "Ужин",
                    "color": "#76BED0",
                    "slug": "dinner"
                }
            ],
            "author": {
                "id": 5,
                "email": "igorantipin@mail.ru",
                "username": "igorantipin",
                "first_name": "Игорь",
                "last_name": "Антипин",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 780,
                    "amount": 200,
                    "name": "куриное филе",
                    "measurement_unit": "г"
                },
                {
                    "id": 1354,
                    "amount": 150,
                    "name": "помидоры черри",
                    "measurement_unit": "г"
                },
                {
                    "id": 149,
                    "amount": 80,
                    "name": "брынза",
                    "measurement_unit": "по вкусу"
                },
                {
                    "id": 975,
                    "amount": 50,
                    "name": "маслины",
                    "measurement_unit": "г"
                },
                {
                    "id": 1241,
                    "amount": 150,
                    "name": "перец болгарский",
                    "measurement_unit": "г"
                },
                {
                    "id": 1138,
                    "amount": 80,
                    "name": "огурцы",
                    "measurement_unit": "г"
                },
                {
                    "id": 1529,
                    "amount": 30,
                    "name": "салат листовой",
                    "measurement_unit": "г"
                },
                {
                    "id": 1236,
                    "amount": 2,
                    "name": "перец",
                    "measurement_unit": "г"
                },
                {
                    "id": 1685,
                    "amount": 2,
                    "name": "соль",
                    "measurement_unit": "г"
                },
                {
                    "id": 1162,
                    "amount": 45,
                    "name": "оливковое масло",
                    "measurement_unit": "г"
                },
                {
                    "id": 851,
                    "amount": 15,
                    "name": "лимонный сок",
                    "measurement_unit": "г"
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "Салат Греческий",
            "image": "http://foodgram-yap.zapto.org/media/recipes/temp_5mhh0Sv.jpeg",
            "text": "Простой, яркий, сытный, праздничный, из свежих овощей! Греческий классический салат с курицей известен на весь мир. В этом рецепте сочное блюдо из свежих хрустящих овощей с сыром дополнено нежным куриным мясом, запеченным со специями в фольге.",
            "cooking_time": 40
        }
    ]
}
```

# Админка для ревьюера :)

Для проверки работы админки используйте следующие данные:

логин: admin
пароль: admin

# Использованные технологии

* Python 3.9
* Django и Django REST Framework для бэкенда.
* React для фронтенда.
* PostgreSQL для хранения данных.
* Docker и Docker Compose для контейнеризации и оркестрации.
* Nginx как веб-сервер и reverse proxy.
* GitHub Actions для автоматизации CI/CD процессов.

# Автор

Елена Альтман ([GitHub](https://github.com/altmanhellen/))

# CI/CD

CI/CD процессы настроены с помощью GitHub Actions, обеспечивая сборку и деплой приложения. Статус последнего деплоя можно увидеть в бейдже в начале README.md файла в репозитории.
