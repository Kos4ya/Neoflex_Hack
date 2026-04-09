import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRoom, type Room } from '@/shared/api/interviews';
import './create-room-modal.css';

type CreateRoomModalProps =  {
  room: Room;
  onClose: () => void;
  onCreated: (roomId: string, newRoom: Room) => void;
}

const LANGUAGES = [
  'TypeScript',
  'JavaScript',
  'Python',
  'Go',
  'Java',
  'C++',
  'C#',
  'Rust',
  'Kotlin',
];

export const CreateRoomModal = ({ room, onClose, onCreated }: CreateRoomModalProps) => {
  const navigate = useNavigate();
  const [lang, setLang] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [createdRoomId, setCreatedRoomId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!lang) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createRoom({
        candidate_id: room.candidateId,
        vacancy_id: room.vacancyId,
        language: lang.toLowerCase(),
      });
      setCreatedRoomId(res.room_id);
      onCreated(room.id, { ...room, id: res.room_id, language: lang.toLowerCase() });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания комнаты');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    const url = `${window.location.origin}/interview/${createdRoomId}`;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <span className="modal__title">Создать комнату</span>
          <button className="modal__close" onClick={onClose}>
            <img src='src/assets/Icons/close.svg' />
            </button>
        </div>
        <div className="modal__body">
          <div>
            <div className="modal__label">Кандидат</div>
            <span style={{ fontSize: 14, fontWeight: 600 }}>
              {room.candidateName} {room.candidateSurname}
            </span>
          </div>

          <div>
            <div className="modal__label">Язык программирования</div>
            <div className="lang-grid">
              {LANGUAGES.map((l) => (
                <button
                  key={l}
                  className={`lang-option${lang === l ? ' lang-option--selected' : ''}`}
                  onClick={() => setLang(l)}
                  disabled={!!createdRoomId}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="modal__error">{error}</div>}

          {createdRoomId && (
            <div>
              <div className="modal__label">Ссылка на комнату</div>
              <div className="room-link-box">
                <span className="room-link-box__url">
                  {window.location.origin}/interview/{createdRoomId}
                </span>
                <button
                  className={`room-link-box__copy${copied ? ' room-link-box__copy--copied' : ''}`}
                  onClick={handleCopy}
                >
                  {copied ? '✓ Скопировано' : 'Копировать'}
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="modal__footer">
          {!createdRoomId ? (
            <button className="btn btn--primary" onClick={handleCreate} disabled={!lang || loading}>
              {loading ? 'Создание...' : <><img src='src/assets/Icons/plus.svg' /> Создать комнату</>}
            </button>
          ) : (
            <button className="btn btn--green" onClick={() => navigate(`/interview/${createdRoomId}`)}>
              <img src='src/assets/Icons/enter.svg' /> Войти в комнату
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
