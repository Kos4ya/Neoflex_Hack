import { fetchRoomFeedbacks, type FeedbackDTO, type Room } from "@/shared/api/interviews";
import { useEffect, useState } from "react";

interface ResultsModalProps {
  room: Room;
  onClose: () => void;
}


const fmtFull = (iso: string) => new Date(iso).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });


export const ResultsModal = ({ room, onClose }: ResultsModalProps) => {
  const [feedbacks, setFeedbacks] = useState<FeedbackDTO[]>(room.feedbacks);
  const [loadingFb, setLoadingFb] = useState(room.feedbacks.length === 0);

  useEffect(() => {
    if (room.feedbacks.length === 0) {
      fetchRoomFeedbacks(room.id)
        .then(setFeedbacks)
        .catch(() => {})
        .finally(() => setLoadingFb(false));
    }
  }, [room.id, room.feedbacks.length]);

  const resultLabel = room.result === 'passed' ? 'Пройдено' : 'Не пройдено';
  const resultClass = room.result === 'passed' ? 'dash-card__result-badge--high' : 'dash-card__result-badge--low';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal--wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <span className="modal__title">Результаты собеседования</span>
          <button className="modal__close" onClick={onClose}><img src='src/assets/Icons/close.svg' /></button>
        </div>
        <div className="modal__body">
          <div className="modal__info-row">
            <div>
              <div className="modal__label">Кандидат</div>
              <span style={{ fontSize: 14, fontWeight: 600 }}>
                {room.candidateName} {room.candidateSurname}
              </span>
            </div>
            <div>
              <div className="modal__label">Результат</div>
              <span className={`dash-card__result-badge ${resultClass}`} style={{ fontSize: 13 }}>
                {resultLabel}
              </span>
            </div>
            <div>
              <div className="modal__label">Язык</div>
              <span className="dash-card__lang-badge">{room.language}</span>
            </div>
            <div>
              <div className="modal__label">Дата</div>
              <span style={{ fontSize: 13 }}>{fmtFull(room.createdAt)}</span>
            </div>
          </div>

          <div>
            <div className="modal__label">Фидбеки ({feedbacks.length})</div>
            {loadingFb ? (
              <div className="modal__loading">Загрузка...</div>
            ) : feedbacks.length === 0 ? (
              <div className="modal__empty-text">Нет фидбеков</div>
            ) : (
              <div className="modal__feedback-list">
                {feedbacks.map((fb) => (
                  <div key={fb.id} className="modal__feedback-item">
                    <div className="modal__feedback-meta">
                      {fmtFull(fb.created_at)}
                    </div>
                    <div className="modal__feedback-text">{fb.text_body}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="modal__footer">
          <button className="btn btn--ghost" onClick={onClose}>Закрыть</button>
        </div>
      </div>
    </div>
  );
};