import { useNavigate } from "react-router-dom";
import type { Room } from "@/shared/api/interviews";
import './interview-card.css' 
import { useState } from "react";

type TabId = 'upcoming' | 'pending' | 'completed';

type RoomCardProps = {
  room: Room;
  index: number;
  tabId: TabId;
  onAction: (room: Room) => void;
}

const fmtDate = (iso: string) => new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
const fmtTime = (iso: string) => new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
const initials = (n: string, s: string) => `${n[0] ?? '?'}${s[0] ?? ''}`.toUpperCase();

export const RoomCard  = ({ room, index, tabId, onAction } : RoomCardProps) => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(`${window.location.origin}/interview/${room.id}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const badge = room.result
    ? room.result === 'passed'
      ? { cls: 'dash-card__result-badge--high', text: 'Пройдено' }
      : { cls: 'dash-card__result-badge--low', text: 'Не пройдено' }
    : null;

  return (
    <div className="dash-card" style={{ animationDelay: `${index * 50}ms` }}>
      <div className="dash-card__avatar">
        {initials(room.candidateName, room.candidateSurname)}
      </div>
      <div className="dash-card__info">
        <div className="dash-card__name">{room.candidateName} {room.candidateSurname}</div>
        <div className="dash-card__vacancy">ID: {room.vacancyId.slice(0, 8)}…</div>
      </div>
      <div className="dash-card__meta">
        {room.language && <span className="dash-card__lang-badge">{room.language}</span>}
        {badge && <span className={`dash-card__result-badge ${badge.cls}`}>{badge.text}</span>}
        <div className="dash-card__time">
          <span className="dash-card__date">{fmtDate(room.createdAt)}</span>
          <span className="dash-card__hour">{fmtTime(room.createdAt)}</span>
        </div>
        <div className="dash-card__actions">
          <button className="btn btn--ghost btn--sm" onClick={handleCopy} title="Скопировать ссылку">
            <img src='src/images/Icons/copy.svg' /> {copied ? 'Скопировано' : 'Ссылка'}
          </button>
          {tabId === 'upcoming' && (
            <button className="btn btn--green btn--sm" onClick={() => navigate(`/interview/${room.id}`)}>
              <img src='src/images/Icons/enter.svg' /> Войти
            </button>
          )}
          {tabId === 'pending' && (
            <button className="btn btn--primary btn--sm" onClick={() => onAction(room)}>
              <img src='src/images/Icons/msg.svg' /> Фидбек
            </button>
          )}
          {tabId === 'completed' && (
            <button className="btn btn--ghost btn--sm" onClick={() => onAction(room)}>
              <img src='src/images/Icons/eye.svg' /> Результаты
            </button>
          )}
        </div>
      </div>
    </div>
  );
};