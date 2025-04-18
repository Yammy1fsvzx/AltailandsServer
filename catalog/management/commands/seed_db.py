import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from faker import Faker
import decimal
import json # Добавим для работы с JSON schema

# Импортируем ваши модели
from catalog.models import (
    Location, Feature, LandUseType, LandCategory,
    LandPlot, PropertyType, GenericProperty
)
from contacts.models import Contact, ContactSubmission, WorkingHours
from news.models import NewsArticle, Category as NewsCategory
from quizzes.models import Quiz, Question, Answer
from requests_app.models import Request

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with mock data for the entire project'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, help='Base number of items to create for major models', default=10)
        parser.add_argument('--clear', action='store_true', help='Clear existing relevant data before seeding')

    def handle(self, *args, **options):
        fake = Faker('ru_RU')
        number_of_items = options['number']
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            # Удаляем в порядке зависимостей
            WorkingHours.objects.all().delete()
            Answer.objects.all().delete()
            Question.objects.all().delete()
            Quiz.objects.all().delete()
            Request.objects.all().delete()
            ContactSubmission.objects.all().delete()
            Contact.objects.all().delete()
            NewsArticle.objects.all().delete()
            NewsCategory.objects.all().delete()
            GenericProperty.objects.all().delete() # Удаляем перед PropertyType
            PropertyType.objects.all().delete()
            LandPlot.objects.all().delete()
            LandCategory.objects.all().delete()
            LandUseType.objects.all().delete()
            Feature.objects.all().delete()
            Location.objects.all().delete()
            # Удаляем всех пользователей, КРОМЕ суперюзеров
            User.objects.filter(is_superuser=False).delete()
            # Удаляем суперюзера admin, если он есть, чтобы создать заново
            User.objects.filter(username="admin", is_superuser=True).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        self.stdout.write(f'Seeding database with ~{number_of_items} items per model...')

        # --- Создаем единственного суперпользователя --- #
        superuser = self._seed_superuser()
        if not superuser:
            self.stdout.write(self.style.ERROR('Failed to create superuser. Aborting seeding.'))
            return
        # Список users теперь содержит только суперпользователя
        users = [superuser]

        # --- Сидинг зависимостей --- #
        company_contacts = self._seed_company_contacts(fake, 1)
        news_categories = self._seed_news_categories()
        self._seed_land_categories()
        self._seed_land_use_types()
        self._seed_features(fake)
        locations = self._seed_locations(fake, number_of_items)

        # --- Сидинг основных моделей каталога --- #
        property_types = self._seed_property_types() # Сначала типы
        generic_properties = self._seed_generic_properties(fake, number_of_items * 2, property_types, locations) # Передаем superuser
        land_plots = self._seed_land_plots(fake, number_of_items, locations) # Участки

        # --- Сидинг остальных приложений --- #
        self._seed_news(fake, number_of_items // 2, news_categories)
        self._seed_contact_submissions(fake, number_of_items, users)
        quizzes = self._seed_quizzes(fake, number_of_items // 3)
        questions = self._seed_questions(fake, number_of_items, quizzes)
        self._seed_answers(fake, number_of_items * 4, questions)

        # Собираем все объекты каталога для заявок
        properties_for_requests = list(land_plots) + list(generic_properties)
        self._seed_requests(fake, number_of_items * 2, users, properties_for_requests)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    # --- Методы сидинга (дополненные и новые) --- #

    def _seed_superuser(self):
        """ Создает или получает одного суперпользователя """
        username = "admin"
        email = "altailands@mail.ru"
        password = "admin"
        try:
            superuser, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "password": password, # Будет хеширован
                    "is_superuser": True,
                    "is_staff": True,
                    "is_active": True
                }
            )
            if created:
                # Устанавливаем пароль правильно, если пользователь был создан
                superuser.set_password(password)
                superuser.save()
                self.stdout.write(self.style.SUCCESS(f"Created superuser {username}/{password}"))
            else:
                 self.stdout.write(self.style.WARNING(f"Superuser {username} already exists."))
            return superuser
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Could not create or get superuser {username}: {e}"))
            return None

    def _seed_company_contacts(self, fake, count):
        self.stdout.write('Seeding Company Contacts...')
        contacts = []
        for _ in range(count):
            contact = Contact.objects.create(
                phone=fake.phone_number(),
                whatsapp=fake.phone_number(),
                email=fake.company_email(),
                office_address=fake.address()
            )
            # Добавляем часы работы для этого контакта
            for day in range(7): # 0-6
                is_workday = day < 5 # Пн-Пт рабочие
                WorkingHours.objects.create(
                    contact=contact,
                    day_of_week=day,
                    start_time=timezone.datetime(2000, 1, 1, 9, 0).time() if is_workday else None,
                    end_time=timezone.datetime(2000, 1, 1, 18, 0).time() if is_workday else None,
                    is_active=is_workday
                )
            contacts.append(contact)
        return contacts

    def _seed_land_categories(self):
        self.stdout.write('Seeding Land Categories...')
        categories = [
            'Земли населённых пунктов',
            'Земли сельскохозяйственного назначения',
            'Земли промышленности, энергетики, транспорта',
            'Земли особо охраняемых территорий и объектов',
            'Земли лесного фонда',
            'Земли водного фонда',
            'Земли запаса'
        ]
        for name in categories:
            LandCategory.objects.get_or_create(name=name)

    def _seed_land_use_types(self):
        self.stdout.write('Seeding Land Use Types...')
        use_types = [
            'Индивидуальное жилищное строительство (ИЖС)',
            'Ведение личного подсобного хозяйства (ЛПХ)',
            'Садоводство',
            'Огородничество',
            'Сельскохозяйственное производство',
            'Дачное строительство',
            'Рекреация',
            'Коммерческое использование',
            'Промышленное использование'
        ]
        for name in use_types:
            LandUseType.objects.get_or_create(name=name)

    def _seed_features(self, fake):
        self.stdout.write('Seeding Features...')
        feature_types = Feature.FEATURE_TYPE_CHOICES
        features_data = {
            'communication': ['Электричество', 'Газ', 'Водопровод', 'Канализация', 'Интернет', 'Подъездные пути'],
            'plot_feature': ['У воды', 'В лесу', 'Ровный', 'С уклоном', 'Видовой', 'Огорожен'],
            'complex_infrastructure': ['Охрана', 'Парковка', 'Детская площадка', 'Бассейн', 'Магазин', 'Ресторан', 'СПА'],
            'unit_feature': ['С отделкой', 'Без отделки', 'Меблировка', 'Панорамные окна', 'Терраса', 'Вид на горы']
            # Можно добавить 'generic_feature': ['Паркинг', 'Балкон', 'Лифт']
        }

        for type_key, names in features_data.items():
            for name in names:
                Feature.objects.get_or_create(name=name, type=type_key)

    def _seed_locations(self, fake, count):
        self.stdout.write('Seeding Locations...')
        locations = []
        for _ in range(count):
            location = Location.objects.create(
                region=random.choice(['Алтайский край', 'Республика Алтай']),
                locality=fake.city_name(),
                address_line=fake.street_address(),
                latitude=decimal.Decimal(fake.latitude()),
                longitude=decimal.Decimal(fake.longitude())
            )
            locations.append(location)
        return locations

    # --- Новые методы сидинга для PropertyType и GenericProperty --- #

    def _seed_property_types(self):
        self.stdout.write('Seeding Property Types...')
        types_data = {
            "Квартира": {
                "area_sqm": {"type": "number", "label": "Площадь (кв.м.)", "required": True},
                "rooms": {"type": "integer", "label": "Кол-во комнат"},
                "floor": {"type": "integer", "label": "Этаж"},
                "total_floors": {"type": "integer", "label": "Этажность дома"},
                "has_balcony": {"type": "boolean", "label": "Балкон/Лоджия"}
            },
            "Дом": {
                "area_sqm": {"type": "number", "label": "Площадь дома (кв.м.)", "required": True},
                "plot_area_sot": {"type": "number", "label": "Площадь участка (сот.)"},
                "floors": {"type": "integer", "label": "Этажность"},
                "bedrooms": {"type": "integer", "label": "Кол-во спален"},
                "material": {"type": "string", "label": "Материал стен", "choices": ["Кирпич", "Бревно", "Брус", "Газоблок"]}
            },
            "Гараж": {
                "area_sqm": {"type": "number", "label": "Площадь (кв.м.)", "required": True},
                "has_pit": {"type": "boolean", "label": "Смотровая яма"},
                "material": {"type": "string", "label": "Материал стен", "choices": ["Кирпич", "Металл", "Бетон"]}
            },
            "Коммерческое помещение": {
                 "area_sqm": {"type": "number", "label": "Площадь (кв.м.)", "required": True},
                 "purpose": {"type": "string", "label": "Назначение", "choices": ["Офис", "Магазин", "Склад", "Производство", "Свободное"]},
                 "floor": {"type": "integer", "label": "Этаж"}
            }
        }
        property_types = []
        for name, schema in types_data.items():
            prop_type, created = PropertyType.objects.get_or_create(
                name=name,
                defaults={
                    'attribute_schema': schema,
                    'slug': slugify(name) # Генерируем slug здесь
                }
            )
            # Обновляем схему, если объект уже существовал, на всякий случай
            if not created and prop_type.attribute_schema != schema:
                 prop_type.attribute_schema = schema
                 prop_type.save()
            property_types.append(prop_type)
        return property_types

    def _generate_attributes(self, fake, schema):
        attributes = {}
        for key, field_schema in schema.items():
            field_type = field_schema.get("type")
            choices = field_schema.get("choices")

            if field_type == "number":
                # Простые границы для примера
                min_val, max_val = (10.0, 500.0) if 'area' in key else (1.0, 100.0)
                attributes[key] = round(random.uniform(min_val, max_val), 1)
            elif field_type == "integer":
                min_val, max_val = (1, 5) if 'room' in key or 'bedroom' in key else (1, 25)
                attributes[key] = random.randint(min_val, max_val)
            elif field_type == "boolean":
                attributes[key] = random.choice([True, False])
            elif field_type == "string":
                if choices:
                    attributes[key] = random.choice(choices)
                else:
                    attributes[key] = fake.word() # Или более специфичная генерация
            # Можно добавить другие типы по необходимости
        return attributes

    def _seed_generic_properties(self, fake, count, property_types, locations):
        self.stdout.write('Seeding Generic Properties...')
        if not property_types:
            self.stdout.write(self.style.WARNING('No property types found to create generic properties.'))
            return []
        if not locations:
             self.stdout.write(self.style.WARNING('No locations found.'))
             return []

        listing_statuses = [choice[0] for choice in GenericProperty.LISTING_STATUS_CHOICES]
        generic_properties = []

        for _ in range(count):
            prop_type = random.choice(property_types)
            loc = random.choice(locations)
            price = round(random.uniform(1_000_000, 100_000_000), -4) # Округляем до 10тыс
            title = f"{prop_type.name} в {loc.locality}"
            attributes = self._generate_attributes(fake, prop_type.attribute_schema)
            # Добавим площадь в заголовок, если она есть в атрибутах
            if 'area_sqm' in attributes:
                title += f" {attributes['area_sqm']:.1f} кв.м."

            prop = GenericProperty.objects.create(
                property_type=prop_type,
                title=title,
                description=fake.text(max_nb_chars=500),
                location=loc,
                price=decimal.Decimal(price),
                listing_status=random.choices(listing_statuses, weights=[7, 1, 1, 1], k=1)[0],
                attributes=attributes,
                view_count=random.randint(0, 5000)
                # parent можно добавить позже, если нужна иерархия
            )
            generic_properties.append(prop)
        return generic_properties

    # --- Обновленные методы сидинга --- #

    def _seed_land_plots(self, fake, count, locations):
        self.stdout.write('Seeding Land Plots...')
        if not locations:
             self.stdout.write(self.style.WARNING('No locations found.'))
             return []

        land_types = [choice[0] for choice in LandPlot.LAND_TYPE_CHOICES]
        plot_statuses = [choice[0] for choice in LandPlot.PLOT_STATUS_CHOICES]
        listing_statuses = [choice[0] for choice in LandPlot.LISTING_STATUS_CHOICES]
        categories = list(LandCategory.objects.all())
        use_types = list(LandUseType.objects.all())
        features = list(Feature.objects.filter(type__in=['communication', 'plot_feature']))
        land_plots = []

        for _ in range(count):
            area = round(random.uniform(5.0, 100.0), 2)
            price_per_are = round(random.uniform(50000, 1000000))
            price = round(price_per_are * area)
            loc = random.choice(locations)

            plot = LandPlot.objects.create(
                land_type=random.choice(land_types),
                title=f"Участок {area:.1f} сот. в {loc.locality}",
                description=fake.text(max_nb_chars=400),
                location=loc,
                land_category=random.choice(categories) if categories else None,
                area=decimal.Decimal(area),
                price=decimal.Decimal(price),
                price_per_are=decimal.Decimal(price_per_are),
                plot_status=random.choices(plot_statuses, weights=[7, 2, 1], k=1)[0],
                listing_status=random.choices(listing_statuses, weights=[9, 1], k=1)[0],
                view_count=random.randint(0, 10000)
            )
            num_use_types = random.randint(1, min(3, len(use_types)))
            if use_types and num_use_types > 0:
                 plot.land_use_types.set(random.sample(use_types, num_use_types))
            num_features = random.randint(1, min(6, len(features)))
            if features and num_features > 0:
                 plot.features.set(random.sample(features, num_features))
            land_plots.append(plot)
        return land_plots

    def _seed_news_categories(self):
        self.stdout.write('Seeding News Categories...')
        categories_names = ['Рынок недвижимости', 'Законодательство', 'Новости компании', 'Аналитика', 'Лайфстайл']
        categories = []
        for name in categories_names:
            category, created = NewsCategory.objects.get_or_create(name=name)
            categories.append(category)
        return categories

    def _seed_news(self, fake, count, categories):
        self.stdout.write('Seeding News Articles...')
        if not categories:
            self.stdout.write(self.style.WARNING('No news categories found to assign.'))
            # Можно либо прекратить выполнение, либо создавать новости без категорий, если модель позволяет (null=True)
            # return

        for _ in range(count):
            NewsArticle.objects.create(
                title=fake.sentence(nb_words=6),
                content='\n'.join(fake.paragraphs(nb=5)),
                category=random.choice(categories) if categories else None,
                view_count=random.randint(0, 1000)
                # Поле image остается пустым
                # Поля created_at и updated_at заполняются автоматически
            )

    def _seed_contact_submissions(self, fake, count, users):
        self.stdout.write('Seeding Contact Submissions...')
        statuses = [choice[0] for choice in ContactSubmission.STATUS_CHOICES]
        for _ in range(count):
            # Связываем с superuser или оставляем None
            user = users[0] if users and random.choice([True, False]) else None
            name = user.get_full_name() if user else fake.name()
            email = user.email if user else fake.email()

            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone_number=fake.phone_number(),
                subject=fake.sentence(nb_words=4),
                message=fake.text(max_nb_chars=300),
                user=user,
                status=random.choices(statuses, weights=[5, 3, 2], k=1)[0]
            )

    def _seed_quizzes(self, fake, count):
        self.stdout.write('Seeding Quizzes...')
        quizzes = []
        for _ in range(count):
            quiz = Quiz.objects.create(
                title=f"Квиз: {fake.catch_phrase()}",
                description=fake.sentence(),
                is_active=random.choices([True, False], weights=[9, 1], k=1)[0]
            )
            quizzes.append(quiz)
        return quizzes

    def _seed_questions(self, fake, count, quizzes):
        self.stdout.write('Seeding Questions...')
        if not quizzes:
            self.stdout.write(self.style.WARNING('No quizzes found to add questions to.'))
            return []
        questions = []
        # Убрал types т.к. не уверен что они есть в модели Question
        # question_types = [choice[0] for choice in Question.QUESTION_TYPE_CHOICES] # Если есть типы

        for _ in range(count):
            question = Question.objects.create(
                quiz=random.choice(quizzes),
                text=fake.sentence().replace('.', '?'),
                order=random.randint(1, 10),
                # question_type=random.choice(question_types) # Если есть поле типа вопроса
            )
            questions.append(question)
        return questions

    def _seed_answers(self, fake, count, questions):
        self.stdout.write('Seeding Answers...')
        if not questions:
            self.stdout.write(self.style.WARNING('No questions found to add answers to.'))
            return

        for _ in range(count):
            question = random.choice(questions)
            # Убираем логику is_correct, т.к. это опрос
            # existing_correct = Answer.objects.filter(question=question, is_correct=True).exists()
            # is_correct_choice = False if existing_correct else random.choices([True, False], weights=[1, 3], k=1)[0]

            Answer.objects.create(
                question=question,
                text=fake.word().capitalize()
                # Убираем поле is_correct
                # is_correct=is_correct_choice
            )

    def _seed_requests(self, fake, count, users, properties_for_requests):
        self.stdout.write('Seeding Requests (requests_app)...')
        if not users:
            self.stdout.write(self.style.WARNING('No users found to create requests for.'))
            # return # Можно раскомментировать, если пользователи обязательны
        if not properties_for_requests:
            self.stdout.write(self.style.WARNING('No properties (LandPlot or GenericProperty) found to create requests for.'))
            return

        request_types = [choice[0] for choice in getattr(Request, 'REQUEST_TYPE_CHOICES', [])]
        statuses = [choice[0] for choice in getattr(Request, 'STATUS_CHOICES', [])]

        for _ in range(count):
            property_choice = random.choice(properties_for_requests)
            # Связываем с superuser или оставляем None (имитируем анонимный запрос)
            user_choice = users[0] if users and random.choice([True, False]) else None

            client_name = user_choice.get_full_name() if user_choice else fake.name()
            client_phone = fake.phone_number()
            client_email = user_choice.email if user_choice else fake.email()
            request_message = fake.sentence()

            # Получаем ContentType для выбранного объекта (LandPlot или GenericProperty)
            content_type = ContentType.objects.get_for_model(property_choice)

            Request.objects.create(
                name=client_name,
                phone=client_phone,
                email=client_email,
                content_type=content_type, # Используем полученный content_type
                object_id=property_choice.pk,
                request_type=random.choice(request_types) if request_types else 'callback', # Указываем тип, например 'callback'
                user_message=request_message,
                status=random.choice(statuses) if statuses else 'new'
            ) 