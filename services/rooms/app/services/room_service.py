from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from typing import List, Optional
import secrets
import string
from datetime import datetime, timezone

from app.models.rooms import Room, Metric, RoomMetric, Feedback, Note, Code
from app.schemas.rooms import (
    RoomCreate, RoomUpdate,
    MetricCreate, MetricUpdate,
    RoomMetricCreate, RoomMetricUpdate,
    FeedbackCreate, FeedbackUpdate,
    NoteCreate, NoteUpdate,
    CodeCreate, CodeUpdate
)


def generate_room_link() -> str:
    """Генерация уникальной ссылки для комнаты"""
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"{token}"


class RoomService:
    """Сервис для работы с комнатами и связанными сущностями"""

    def __init__(self, db: AsyncSession):
        self.db = db


    async def list_rooms(
            self,
            skip: int = 0,
            limit: int = 100,
            candidate_id: Optional[UUID] = None,
            interviewer_id: Optional[UUID] = None,
            vacancy_id: Optional[UUID] = None
    ) -> List[Room]:
        """Список комнат с фильтрацией"""
        query = select(Room)

        if candidate_id:
            query = query.where(Room.candidate_id == candidate_id)
        if interviewer_id:
            query = query.where(Room.interviewer_id == interviewer_id)
        if vacancy_id:
            query = query.where(Room.vacancy_id == vacancy_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_room(self, room_id: UUID) -> Optional[Room]:
        """Получение комнаты по ID"""
        result = await self.db.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_room_by_link(self, link: str) -> Optional[Room]:
        """Получение комнаты по ссылке"""
        result = await self.db.execute(
            select(Room).where(Room.link == link)
        )
        return result.scalar_one_or_none()

    async def create_room(self, room_data: RoomCreate) -> Room:
        """Создание комнаты с автоматической генерацией ссылки"""
        link = generate_room_link()

        # Проверка уникальности
        while await self.get_room_by_link(link):
            link = generate_room_link()

        room = Room(
            candidate_id=room_data.candidate_id,
            interviewer_id=room_data.interviewer_id,
            vacancy_id=room_data.vacancy_id,
            link=link
        )
        self.db.add(room)
        await self.db.flush()
        return room

    async def update_room(
            self,
            room_id: UUID,
            room_data: RoomUpdate
    ) -> Optional[Room]:
        """Обновление комнаты"""
        room = await self.get_room(room_id)
        if not room:
            return None

        update_data = room_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(room, key, value)

        await self.db.flush()
        return room

    async def delete_room(self, room_id: UUID) -> bool:
        """Удаление комнаты"""
        room = await self.get_room(room_id)
        if not room:
            return False

        await self.db.delete(room)
        await self.db.flush()
        return True

    async def get_room_with_details(self, room_id: UUID) -> Optional[dict]:
        """Получение комнаты со всеми связанными данными"""
        room = await self.get_room(room_id)
        if not room:
            return None

        # Получение метрик
        metrics_result = await self.db.execute(
            select(RoomMetric, Metric)
            .join(Metric, RoomMetric.metric_id == Metric.id)
            .where(RoomMetric.room_id == room_id)
        )
        metrics = []
        for rm, metric in metrics_result.all():
            metrics.append({
                "id": rm.id,
                "metric_id": rm.metric_id,
                "room_id": rm.room_id,
                "result": rm.result,
                "created_at": rm.created_at,
                "updated_at": rm.updated_at,
                "metric": metric
            })

        feedbacks_result = await self.db.execute(
            select(Feedback).where(Feedback.room_id == room_id)
        )
        feedbacks = feedbacks_result.scalars().all()

        notes_result = await self.db.execute(
            select(Note).where(Note.room_id == room_id)
        )
        notes = notes_result.scalars().all()

        codes_result = await self.db.execute(
            select(Code).where(Code.room_id == room_id)
        )
        codes = codes_result.scalars().all()

        return {
            "id": room.id,
            "candidate_id": room.candidate_id,
            "interviewer_id": room.interviewer_id,
            "vacancy_id": room.vacancy_id,
            "link": room.link,
            "created_at": room.created_at,
            "updated_at": room.updated_at,
            "metrics": metrics,
            "feedbacks": feedbacks,
            "notes": notes,
            "codes": codes
        }

    async def start_room(self, room_id: UUID) -> Optional[Room]:
        """
        Начать интервью в комнате.
        Устанавливает статус 'active' и время начала.
        """
        room = await self.get_room(room_id)
        if not room:
            return None

        # Нельзя начать уже начатую или завершённую комнату
        if room.status in ["active", "completed"]:
            return None

        from datetime import datetime
        room.status = "active"
        room.started_at = datetime.now()

        await self.db.flush()
        return room


    async def complete_room(self, room_id: UUID) -> Optional[Room]:
        """
        Завершить интервью в комнате.
        Устанавливает статус 'completed' и время окончания.
        """
        room = await self.get_room(room_id)
        if not room:
            return None

        # Можно завершить только активную комнату
        if room.status != "active":
            return None

        room.status = "completed"
        room.finished_at = datetime.now()

        await self.db.flush()
        return room


    async def cancel_room(self, room_id: UUID) -> Optional[Room]:
        """
        Отменить интервью в комнате.
        Устанавливает статус 'cancelled'.
        """
        room = await self.get_room(room_id)
        if not room:
            return None

        # Нельзя отменить уже завершённую комнату
        if room.status == "completed":
            return None

        room.status = "cancelled"

        await self.db.flush()
        return room

    async def get_room_time_offset(self, room_id: UUID) -> Optional[int]:
        """
        Получить количество секунд, прошедших с начала интервью в комнате
        """
        room = await self.get_room(room_id)
        if not room:
            return None

        if not room.started_at:
            return 0  # интервью ещё не началось

        now = datetime.now(timezone.utc)
        offset = int((now - room.started_at).total_seconds())
        return offset


    async def get_active_rooms(
            self,
            skip: int = 0,
            limit: int = 100,
            interviewer_id: Optional[UUID] = None
    ) -> List[Room]:
        """Получить активные комнаты (в процессе интервью)"""
        query = select(Room).where(Room.status == "active")

        if interviewer_id:
            query = query.where(Room.interviewer_id == interviewer_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()


    async def get_room_duration(self, room_id: UUID) -> Optional[dict]:
        """
        Получить длительность интервью в комнате.
        Возвращает длительность в минутах и секундах.
        """
        room = await self.get_room(room_id)
        if not room:
            return None

        if not room.started_at:
            return {"error": "interview_not_started"}

        end_time = room.finished_at or datetime.now()
        duration = end_time - room.started_at

        return {
            "room_id": room_id,
            "started_at": room.started_at,
            "finished_at": room.finished_at,
            "duration_seconds": int(duration.total_seconds()),
            "duration_minutes": round(duration.total_seconds() / 60, 2),
            "status": room.status
        }


    async def get_rooms_by_status(
            self,
            status: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Room]:
        """Получить комнаты по статусу"""
        query = select(Room).where(Room.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()


    async def list_metrics(
            self,
            skip: int = 0,
            limit: int = 100,
            visible_only: bool = False,
            name: Optional[str] = None
    ) -> List[Metric]:
        """Список метрик с фильтрацией"""
        query = select(Metric)

        if visible_only:
            query = query.where(Metric.visible == True)
        if name:
            query = query.where(Metric.name.ilike(f"%{name}%"))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_metric(self, metric_id: UUID) -> Optional[Metric]:
        """Получение метрики по ID"""
        result = await self.db.execute(
            select(Metric).where(Metric.id == metric_id)
        )
        return result.scalar_one_or_none()

    async def create_metric(self, metric_data: MetricCreate) -> Metric:
        """Создание метрики"""
        metric = Metric(
            name=metric_data.name,
            scale_from=metric_data.scale_from,
            scale_to=metric_data.scale_to,
            visible=metric_data.visible
        )
        self.db.add(metric)
        await self.db.flush()
        return metric

    async def update_metric(
            self,
            metric_id: UUID,
            metric_data: MetricUpdate
    ) -> Optional[Metric]:
        """Обновление метрики"""
        metric = await self.get_metric(metric_id)
        if not metric:
            return None

        update_data = metric_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(metric, key, value)

        await self.db.flush()
        return metric

    async def delete_metric(self, metric_id: UUID) -> bool:
        """Удаление метрики"""
        metric = await self.get_metric(metric_id)
        if not metric:
            return False

        await self.db.delete(metric)
        await self.db.flush()
        return True


    async def get_room_metrics(self, room_id: UUID) -> List[RoomMetric]:
        """Получение всех метрик комнаты с результатами"""
        result = await self.db.execute(
            select(RoomMetric).where(RoomMetric.room_id == room_id)
        )
        return result.scalars().all()

    async def assign_metric_to_room(
            self,
            room_id: UUID,
            metric_id: UUID,
            result: Optional[float] = None
    ) -> Optional[RoomMetric]:
        """Назначение метрики комнате"""
        room = await self.get_room(room_id)
        metric = await self.get_metric(metric_id)

        if not room or not metric:
            return None

        existing = await self.db.execute(
            select(RoomMetric).where(
                RoomMetric.room_id == room_id,
                RoomMetric.metric_id == metric_id
            )
        )
        if existing.scalar_one_or_none():
            return None

        room_metric = RoomMetric(
            room_id=room_id,
            metric_id=metric_id,
            result=result
        )
        self.db.add(room_metric)
        await self.db.flush()
        return room_metric

    async def update_room_metric_result(
            self,
            room_id: UUID,
            metric_id: UUID,
            result: float
    ) -> Optional[RoomMetric]:
        """Обновление результата метрики в комнате"""
        result_query = await self.db.execute(
            select(RoomMetric).where(
                RoomMetric.room_id == room_id,
                RoomMetric.metric_id == metric_id
            )
        )
        room_metric = result_query.scalar_one_or_none()
        if not room_metric:
            return None

        room_metric.result = result
        await self.db.flush()
        return room_metric

    async def remove_metric_from_room(
            self,
            room_id: UUID,
            metric_id: UUID
    ) -> bool:
        """Удаление метрики из комнаты"""
        result = await self.db.execute(
            select(RoomMetric).where(
                RoomMetric.room_id == room_id,
                RoomMetric.metric_id == metric_id
            )
        )
        room_metric = result.scalar_one_or_none()
        if not room_metric:
            return False

        await self.db.delete(room_metric)
        await self.db.flush()
        return True

    async def bulk_assign_metrics_to_room(
            self,
            room_id: UUID,
            metric_ids: List[UUID]
    ) -> dict:
        """Массовое назначение метрик комнате"""
        room = await self.get_room(room_id)
        if not room:
            return {"error": "room_not_found"}

        assigned = []
        failed = []

        for metric_id in metric_ids:
            result = await self.assign_metric_to_room(room_id, metric_id)
            if result:
                assigned.append(metric_id)
            else:
                failed.append(metric_id)

        return {
            "assigned": assigned,
            "failed": failed,
            "total": len(metric_ids)
        }


    async def get_room_feedbacks(self, room_id: UUID) -> List[Feedback]:
        """Получение всех фидбеков комнаты"""
        result = await self.db.execute(
            select(Feedback).where(Feedback.room_id == room_id)
        )
        return result.scalars().all()

    async def create_feedback(
            self,
            room_id: UUID,
            feedback_data: FeedbackCreate
    ) -> Optional[Feedback]:
        """Создание фидбека для комнаты"""
        room = await self.get_room(room_id)
        if not room:
            return None

        feedback = Feedback(
            room_id=room_id,
            text_body=feedback_data.text_body
        )
        self.db.add(feedback)
        await self.db.flush()
        return feedback

    async def update_feedback(
            self,
            feedback_id: UUID,
            feedback_data: FeedbackUpdate
    ) -> Optional[Feedback]:
        """Обновление фидбека"""
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            return None

        update_data = feedback_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(feedback, key, value)

        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def delete_feedback(self, feedback_id: UUID) -> bool:
        """Удаление фидбека"""
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            return False

        await self.db.delete(feedback)
        await self.db.flush()
        return True


    async def get_room_notes(self, room_id: UUID) -> List[Note]:
        """Получение всех заметок комнаты"""
        result = await self.db.execute(
            select(Note).where(Note.room_id == room_id)
        )
        return result.scalars().all()

    async def create_note(
            self,
            room_id: UUID,
            note_data: NoteCreate
    ) -> Optional[Note]:
        """Создание заметки для комнаты"""
        room = await self.get_room(room_id)
        if not room:
            return None

        time_offset = await self.get_room_time_offset(room_id)

        note = Note(
            room_id=room_id,
            note_body=note_data.note_body,
            time_offset=time_offset,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def update_note(
            self,
            note_id: UUID,
            note_data: NoteUpdate
    ) -> Optional[Note]:
        """Обновление заметки"""
        result = await self.db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()
        if not note:
            return None

        update_data = note_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)

        await self.db.flush()
        return note

    async def delete_note(self, note_id: UUID) -> bool:
        """Удаление заметки"""
        result = await self.db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()
        if not note:
            return False

        await self.db.delete(note)
        await self.db.commit()
        return True


    async def get_room_codes(self, room_id: UUID) -> List[Code]:
        """Получение всего кода комнаты"""
        result = await self.db.execute(
            select(Code).where(Code.room_id == room_id)
        )
        return result.scalars().all()

    async def create_code(
            self,
            room_id: UUID,
            code_data: CodeCreate
    ) -> Optional[Code]:
        """Создание/сохранение кода для комнаты"""
        room = await self.get_room(room_id)
        if not room:
            return None

        code = Code(
            room_id=room_id,
            code_body=code_data.code_body
        )
        self.db.add(code)
        await self.db.commit()
        await self.db.refresh(code)
        return code

    async def update_code(
            self,
            code_id: UUID,
            code_data: CodeUpdate
    ) -> Optional[Code]:
        """Обновление кода"""
        result = await self.db.execute(
            select(Code).where(Code.id == code_id)
        )
        code = result.scalar_one_or_none()
        if not code:
            return None

        update_data = code_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(code, key, value)

        await self.db.flush()
        return code

    async def delete_code(self, code_id: UUID) -> bool:
        """Удаление кода"""
        result = await self.db.execute(
            select(Code).where(Code.id == code_id)
        )
        code = result.scalar_one_or_none()
        if not code:
            return False

        await self.db.delete(code)
        await self.db.flush()
        return True