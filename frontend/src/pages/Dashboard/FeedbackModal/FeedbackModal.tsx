import { useState } from "react";
import { sendFeedback, type Room } from "@/shared/api/interviews";

interface FeedbackModalProps {
  room: Room;
  onClose: () => void;
  onSent: (roomId: string) => void;
}


const fmtFull = (iso: string) => new Date(iso).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });


export const FeedbackModal = ({ room, onClose, onSent }: FeedbackModalProps) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await sendFeedback(room.id, text.trim());
      onSent(room.id);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка отправки');
    } finally {
      setLoading(false);
    }
  };

  const resultLabel = room.result === 'passed' ? 'Пройдено' : 'Не пройдено';
  const resultClass = room.result === 'passed' ? 'dash-card__result-badge--high' : 'dash-card__result-badge--low';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal--wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <span className="modal__title">Отправить фидбек</span>
          <button className="modal__close" onClick={onClose}><img src='src/assets/Icons/close' /></button>
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
              <span className={`dash-card__result-badge ${resultClass}`}>{resultLabel}</span>
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
            <div className="modal__label">Фидбек</div>
            <textarea
              className="modal__textarea"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Опишите результаты собеседования, сильные и слабые стороны кандидата..."
              rows={6}
              autoFocus
            />
          </div>

          {error && <div className="modal__error">{error}</div>}
        </div>
        <div className="modal__footer">
          <button className="btn btn--ghost" onClick={onClose}>Отмена</button>
          <button className="btn btn--primary" onClick={handleSend} disabled={!text.trim() || loading}>
            {loading ? 'Отправка...' : <><img src='src/assets/Icons/send.svg' /> Отправить фидбек</>}
          </button>
        </div>
      </div>
    </div>
  );
};