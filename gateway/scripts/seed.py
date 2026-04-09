import asyncio
import httpx
from typing import Dict, Any, List
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8080/api/v1"


class DataSeeder:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.created_users = []
        self.created_vacancies = []
        self.created_candidates = []
        self.created_sessions = []

    async def close(self):
        await self.client.aclose()

    async def register_user(self, email: str, password: str, full_name: str, role: str) -> Dict:
        """Регистрация пользователя"""
        response = await self.client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Зарегистрирован {role}: {full_name} ({email})")
            return data
        elif response.status_code == 409:
            print(f"⚠ Пользователь уже существует: {email}")
            # Пытаемся получить токен через логин
            return await self.login(email, password)
        else:
            print(f"✗ Ошибка регистрации {email}: {response.text}")
            return None

    async def login(self, email: str, password: str) -> str:
        """Логин и получение токена"""
        response = await self.client.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Вход выполнен: {email}")
            return data
        else:
            print(f"✗ Ошибка входа {email}: {response.text}")
            return None

    async def create_vacancy(self, token: str, title: str, description: str, department: str,
                             required_skills: list) -> Dict:
        """Создание вакансии (требует manager прав)"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{BASE_URL}/vacancies/vacancies",
            headers=headers,
            json={
                "name": title,
                "description": description,
                "department": department,
                "required_skills": required_skills,
                "experience_level": "middle",
                "location": "Remote",
                "status": "open"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Создана вакансия: {title}")
            return data
        else:
            print(f"✗ Ошибка создания вакансии {title}: {response.text}")
            return None

    async def create_candidate(self, token: str, name: str, surname: str, email: str, phone: str, skills: list) -> Dict:
        """Создание кандидата"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{BASE_URL}/vacancies/candidates",
            headers=headers,
            json={
                "name": name,
                "surname": surname,
                "email": email,
                "phone": phone,
                "skills": skills,
                "experience_years": 3,
                "status": "active"
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Создан кандидат: {name} {surname} ({email})")
            return data
        else:
            print(f"✗ Ошибка создания кандидата {email}: {response.text}")
            return None

    async def assign_candidate_to_vacancy(self, token: str, vacancy_id: str, candidate_id: str) -> bool:
        """Назначение кандидата на вакансию"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{BASE_URL}/vacancies/vacancies/{vacancy_id}/candidates/{candidate_id}",
            headers=headers
        )
        if response.status_code == 201:
            print(f"✓ Кандидат {candidate_id} назначен на вакансию {vacancy_id}")
            return True
        elif response.status_code == 400:
            print(f"⚠ Кандидат уже назначен на эту вакансию")
            return True
        else:
            print(f"✗ Ошибка назначения: {response.text}")
            return False

    async def change_candidate_status(self, token: str, vacancy_id: str, candidate_id: str, status: str) -> bool:
        """Смена статуса кандидата на вакансии"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.patch(
            f"{BASE_URL}/vacancies/vacancies/{vacancy_id}/candidates/{candidate_id}/status?status={status}",
            headers=headers
        )
        if response.status_code == 200:
            print(f"✓ Статус кандидата изменен на {status}")
            return True
        else:
            print(f"✗ Ошибка смены статуса: {response.text}")
            return False

    async def create_session(self, token: str, vacancy_id: str, candidate_id: str, interviewer_id: str,
                             language: str = "python") -> Dict:
        """Создание сессии интервью"""
        headers = {"Authorization": f"Bearer {token}"}
        scheduled_start = (datetime.now() + timedelta(days=2)).isoformat() + "Z"
        scheduled_end = (datetime.now() + timedelta(days=2, hours=1)).isoformat() + "Z"

        response = await self.client.post(
            f"{BASE_URL}/sessions/",
            headers=headers,
            json={
                "vacancy_id": vacancy_id,
                "candidate_id": candidate_id,
                "interviewer_id": interviewer_id,
                "language": language,
                "scheduled_start_at": scheduled_start,
                "scheduled_end_at": scheduled_end
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Создана сессия: {data.get('id')}")
            return data
        else:
            print(f"✗ Ошибка создания сессии: {response.text}")
            return None

    async def get_vacancies(self, token: str) -> List[Dict]:
        """Получение списка вакансий"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get(
            f"{BASE_URL}/vacancies/vacancies",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_candidates(self, token: str) -> List[Dict]:
        """Получение списка кандидатов"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get(
            f"{BASE_URL}/vacancies/candidates",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_users(self, token: str) -> List[Dict]:
        """Получение списка пользователей"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get(
            f"{BASE_URL}/users/",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            return data
        return []

    async def seed_all(self):
        """Заполнение всеми тестовыми данными"""
        print("\n" + "=" * 60)
        print("🌱 Начало заполнения БД тестовыми данными")
        print("=" * 60 + "\n")

        # 1. Создаем пользователей
        print("📝 Шаг 1: Создание пользователей")
        print("-" * 40)

        # Админ
        admin_data = await self.register_user(
            email="admin@example.com",
            password="admin123",
            full_name="Администратор Системы",
            role="admin"
        )

        # Менеджер
        manager_data = await self.register_user(
            email="manager@example.com",
            password="manager123",
            full_name="Алексей Менеджеров",
            role="manager"
        )
        if manager_data:
            self.access_token = manager_data.get("access_token")

        # Интервьюеры
        interviewer1_data = await self.register_user(
            email="ivan.ivanov@example.com",
            password="interviewer123",
            full_name="Иван Иванов",
            role="interviewer"
        )

        interviewer2_data = await self.register_user(
            email="petr.petrov@example.com",
            password="interviewer123",
            full_name="Петр Петров",
            role="interviewer"
        )

        interviewer3_data = await self.register_user(
            email="elena.smirnova@example.com",
            password="interviewer123",
            full_name="Елена Смирнова",
            role="interviewer"
        )

        # 2. Получаем токен менеджера для создания вакансий
        if not self.access_token:
            manager_login = await self.login("manager@example.com", "manager123")
            if manager_login:
                self.access_token = manager_login.get("access_token")

        if not self.access_token:
            print("✗ Не удалось получить токен менеджера")
            return

        # 3. Создаем вакансии
        print("\n📝 Шаг 2: Создание вакансий")
        print("-" * 40)

        vacancies_data = [
            {
                "title": "Senior Python Developer",
                "description": "Разработка высоконагруженных сервисов на Python/FastAPI. Требуется опыт работы с асинхронностью, PostgreSQL, Redis, Docker, Kubernetes.",
                "department": "Backend",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"]
            },
            {
                "title": "Kotlin Backend Developer",
                "description": "Разработка микросервисов на Kotlin с использованием Spring Boot. Опыт работы с Kafka, MongoDB, Docker.",
                "department": "Backend",
                "required_skills": ["Kotlin", "Spring Boot", "PostgreSQL", "Kafka", "Docker"]
            },
            {
                "title": "React Frontend Developer",
                "description": "Разработка UI компонентов на React. Знание TypeScript, Redux, Material UI, опыт работы с REST API.",
                "department": "Frontend",
                "required_skills": ["React", "TypeScript", "Redux", "CSS", "Jest"]
            },
            {
                "title": "DevOps Engineer",
                "description": "Настройка CI/CD, управление инфраструктурой в AWS, мониторинг и логирование.",
                "department": "DevOps",
                "required_skills": ["AWS", "Terraform", "Kubernetes", "GitLab CI", "Prometheus"]
            },
            {
                "title": "Mobile Developer (iOS)",
                "description": "Разработка мобильного приложения на Swift. Опыт работы с SwiftUI, Combine, CoreData.",
                "department": "Mobile",
                "required_skills": ["Swift", "SwiftUI", "iOS", "CoreData", "REST API"]
            }
        ]

        for v_data in vacancies_data:
            vacancy = await self.create_vacancy(
                token=self.access_token,
                title=v_data["title"],
                description=v_data["description"],
                department=v_data["department"],
                required_skills=v_data["required_skills"]
            )
            if vacancy:
                self.created_vacancies.append(vacancy)

        # 4. Создаем кандидатов
        print("\n📝 Шаг 3: Создание кандидатов")
        print("-" * 40)

        candidates_data = [
            {"name": "Дмитрий", "surname": "Кузнецов", "email": "dmitry@example.com", "phone": "+7-999-123-45-01",
             "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]},
            {"name": "Анна", "surname": "Соколова", "email": "anna@example.com", "phone": "+7-999-123-45-02",
             "skills": ["Kotlin", "Spring Boot", "Kafka", "MongoDB"]},
            {"name": "Максим", "surname": "Лебедев", "email": "maxim@example.com", "phone": "+7-999-123-45-03",
             "skills": ["React", "TypeScript", "Redux", "Next.js"]},
            {"name": "Екатерина", "surname": "Морозова", "email": "ekaterina@example.com", "phone": "+7-999-123-45-04",
             "skills": ["Python", "Django", "PostgreSQL", "AWS"]},
            {"name": "Андрей", "surname": "Новиков", "email": "andrey@example.com", "phone": "+7-999-123-45-05",
             "skills": ["Go", "Kubernetes", "Docker", "Terraform"]},
            {"name": "Мария", "surname": "Волкова", "email": "maria@example.com", "phone": "+7-999-123-45-06",
             "skills": ["Swift", "SwiftUI", "iOS", "Firebase"]},
            {"name": "Сергей", "surname": "Павлов", "email": "sergey@example.com", "phone": "+7-999-123-45-07",
             "skills": ["Java", "Spring", "Hibernate", "Maven"]},
            {"name": "Ольга", "surname": "Степанова", "email": "olga@example.com", "phone": "+7-999-123-45-08",
             "skills": ["JavaScript", "Vue.js", "Node.js", "MongoDB"]},
        ]

        for c_data in candidates_data:
            candidate = await self.create_candidate(
                token=self.access_token,
                name=c_data["name"],
                surname=c_data["surname"],
                email=c_data["email"],
                phone=c_data["phone"],
                skills=c_data["skills"]
            )
            if candidate:
                self.created_candidates.append(candidate)

        # 5. Назначаем кандидатов на вакансии
        print("\n📝 Шаг 4: Назначение кандидатов на вакансии")
        print("-" * 40)

        # Получаем актуальные списки
        vacancies = await self.get_vacancies(self.access_token)
        candidates = await self.get_candidates(self.access_token)

        if vacancies and candidates:
            # Python Developer вакансия (первые 2 кандидата)
            if len(vacancies) > 0 and len(candidates) > 0:
                await self.assign_candidate_to_vacancy(
                    self.access_token,
                    vacancies[0]["id"],
                    candidates[0]["id"]
                )
                await self.change_candidate_status(
                    self.access_token,
                    vacancies[0]["id"],
                    candidates[0]["id"],
                    "reviewed"
                )

            if len(vacancies) > 0 and len(candidates) > 1:
                await self.assign_candidate_to_vacancy(
                    self.access_token,
                    vacancies[0]["id"],
                    candidates[1]["id"]
                )
                await self.change_candidate_status(
                    self.access_token,
                    vacancies[0]["id"],
                    candidates[1]["id"],
                    "invited"
                )

            # Kotlin вакансия
            if len(vacancies) > 1 and len(candidates) > 2:
                await self.assign_candidate_to_vacancy(
                    self.access_token,
                    vacancies[1]["id"],
                    candidates[2]["id"]
                )
                await self.change_candidate_status(
                    self.access_token,
                    vacancies[1]["id"],
                    candidates[2]["id"],
                    "pending"
                )

            # React вакансия
            if len(vacancies) > 2 and len(candidates) > 3:
                await self.assign_candidate_to_vacancy(
                    self.access_token,
                    vacancies[2]["id"],
                    candidates[3]["id"]
                )
                await self.change_candidate_status(
                    self.access_token,
                    vacancies[2]["id"],
                    candidates[3]["id"],
                    "invited"
                )

            if len(vacancies) > 2 and len(candidates) > 4:
                await self.assign_candidate_to_vacancy(
                    self.access_token,
                    vacancies[2]["id"],
                    candidates[4]["id"]
                )

        # 6. Создаем сессии интервью (если есть эндпоинт)
        print("\n📝 Шаг 5: Создание сессий интервью")
        print("-" * 40)

        users = await self.get_users(self.access_token)
        interviewers = [u for u in users if u.get("role") == "interviewer"]

        if vacancies and candidates and interviewers:
            if len(vacancies) > 0 and len(candidates) > 0 and len(interviewers) > 0:
                await self.create_session(
                    token=self.access_token,
                    vacancy_id=vacancies[0]["id"],
                    candidate_id=candidates[0]["id"],
                    interviewer_id=interviewers[0]["id"],
                    language="python"
                )

        # 7. Итог
        print("\n" + "=" * 60)
        print("✅ Заполнение завершено!")
        print("=" * 60)

        print("\n📊 Сводка созданных данных:")
        print(f"  - Пользователей: {len(await self.get_users(self.access_token))}")
        print(f"  - Вакансий: {len(self.created_vacancies)}")
        print(f"  - Кандидатов: {len(self.created_candidates)}")

        print("\n👤 Тестовые учетные записи:")
        print("  - admin@example.com / admin123 (admin)")
        print("  - manager@example.com / manager123 (manager)")
        print("  - ivan.ivanov@example.com / interviewer123 (interviewer)")
        print("  - petr.petrov@example.com / interviewer123 (interviewer)")
        print("  - elena.smirnova@example.com / interviewer123 (interviewer)")

        print("\n💼 Вакансии:")
        for v in self.created_vacancies:
            print(f"  - {v.get('title')}")

        print("\n👥 Кандидаты:")
        for c in self.created_candidates:
            print(f"  - {c.get('name')} {c.get('surname')} ({c.get('email')})")

        print("\n🔗 Полезные ссылки:")
        print(f"  - Swagger Gateway: http://localhost:8080/docs")
        print(f"  - Swagger Users: http://localhost:8001/docs")
        print(f"  - Swagger Sessions: http://localhost:8002/docs")
        print(f"  - Swagger Vacancies: http://localhost:8003/docs")

        return True

    async def seed_minimal(self):
        """Минимальное заполнение (только пользователи)"""
        print("\n" + "=" * 50)
        print("🌱 Минимальное заполнение БД")
        print("=" * 50 + "\n")

        # Создаем админа
        await self.register_user(
            email="admin@example.com",
            password="admin123",
            full_name="Администратор",
            role="admin"
        )

        # Создаем менеджера
        await self.register_user(
            email="manager@example.com",
            password="manager123",
            full_name="Менеджер",
            role="manager"
        )

        # Создаем интервьюеров
        await self.register_user(
            email="interviewer@example.com",
            password="interviewer123",
            full_name="Интервьюер",
            role="interviewer"
        )

        print("\n✅ Минимальное заполнение завершено!")
        print("\n📊 Тестовые учетные записи:")
        print("  - admin@example.com / admin123 (admin)")
        print("  - manager@example.com / manager123 (manager)")
        print("  - interviewer@example.com / interviewer123 (interviewer)")


async def main():
    seeder = DataSeeder()
    try:
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--minimal":
            await seeder.seed_minimal()
        else:
            await seeder.seed_all()
    finally:
        await seeder.close()


if __name__ == "__main__":
    asyncio.run(main())
