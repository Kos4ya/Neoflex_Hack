import { useState, useEffect, useMemo} from 'react';
import { useNavigate } from 'react-router-dom';
import { CreateRoomModal } from './CreateRoomModal/CreateRoomModal';
import { RoomCard } from './RoomCard/RoomCard';
import { FeedbackModal } from './FeedbackModal/FeedbackModal';
import { ResultsModal } from './ResultsModal/ResultsModal';
import { fetchDashboardData, type Room } from '@/shared/api/interviews';
import './dashboard.css';


type TabId = 'upcoming' | 'pending' | 'completed';

interface Tab {
  id: TabId;
  label: string;
  filter: (r: Room) => boolean;
}

const TABS: Tab[] = [
  {
    id: 'upcoming',
    label: 'Не проведённые',
    filter: (r) => r.result === null,
  },
  {
    id: 'pending',
    label: 'Без фидбека',
    filter: (r) => r.result !== null && !r.hasFeedback,
  },
  {
    id: 'completed',
    label: 'Завершённые',
    filter: (r) => r.result !== null && r.hasFeedback,
  },
];

// ── Languages for Monaco ───────────────────────────────────
type ModalState =
  | { type: 'create'; room: Room }
  | { type: 'feedback'; room: Room }
  | { type: 'results'; room: Room }
  | null;

 export const Dashboard = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>('upcoming');
  const [modal, setModal] = useState<ModalState>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData()
      .then(setRooms)
      .catch((err) => {
        console.error('Failed to load dashboard:', err);
        setError('Не удалось загрузить данные');
      })
      .finally(() => setLoading(false));
  }, []);

  const counts = useMemo(() => {
    const map: Record<TabId, number> = { upcoming: 0, pending: 0, completed: 0 };
    TABS.forEach((tab) => {
      map[tab.id] = rooms.filter(tab.filter).length;
    });
    return map;
  }, [rooms]);

    const filtered = useMemo(() => {
    const tab = TABS.find((t) => t.id === activeTab)!;
    return rooms.filter(tab.filter);
  }, [rooms, activeTab]);


  const handleCardAction = (room: Room) => {
    if (activeTab === 'pending')   setModal({ type: 'feedback', room });
    if (activeTab === 'completed') setModal({ type: 'results', room });
  };

  const handleFeedbackSent = (roomId: string) => {
    setRooms((prev) => prev.map((r) => r.id === roomId ? { ...r, hasFeedback: true } : r));
  };

  const handleRoomCreated = (_oldId: string, newRoom: Room) => {
    setRooms((prev) => [...prev, newRoom]);
  };

  const handleLogout = () => {
    //logout();
    navigate('/login');
  };


    const dashContent = [
  {
    id: 1,
    icon: 'calendar.svg',
    label: 'Предстоящие',
    value: counts.upcoming,
    style: '--done'
  },
  {
    id: 2,
    icon: 'clock.svg',
    label: 'Ждут фидбек',
    value: counts.pending,
    style: '--pending'
  },
  {
    id: 3,
    icon: 'check.svg',
    label: 'Завершены',
    value: counts.completed,
    style: '--done' 
  },
]

  return (
    <div className="dash">
      <header className="dash-header">
        <div className="dash-header__left">
          <div className="dash-header__logo">
            <img src='src/assets/Icons/code.svg'/>
            <span className="dash-header__logo-text">CodeInterview</span>
          </div>
          <span className="dash-header__sep" />
          <span className="dash-header__title">Панель интервьюера</span>
        </div>
        <div className="dash-header__right">
          <span className="dash-header__user-name">Интервьюер</span>
          <div className="dash-header__avatar">И</div>
        </div>
      </header>

      <div className="dash-content">
        <div className="dash-stats">
          {dashContent.map(item => (
            <div key={item.id} className="dash-stat">
              <div 
                className={`dash-stat__icon dash-stat__icon${item.style}`}>
              <img src={`/icons/${item.icon}`}/>
            </div>
            <div className="dash-stat__info">
              <span className="dash-stat__value">{item.value}</span>
              <span className="dash-stat__label">{item.label}</span>
            </div>
            </div>
          ))

          }
        </div>


        <div className="dash-tabs">
          {TABS.map((item) => (
            <button key={item.id} className={`dash-tab${activeTab === item.id ? ' dash-tab--active' : ''}`} onClick={() => setActiveTab(item.id)}>
              {item.label}<span className="dash-tab__count">{counts[item.id]}</span>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="dash-skeleton">{[1,2,3].map(item => <div key={item} className="dash-skeleton__card"/>)}</div>
        ) : error ? (
          <div className="dash-cards--empty">
            <img src='/icons/empty.svg' /><span>{error}</span>
            <button className="btn btn--primary btn--sm" onClick={() => window.location.reload()} style={{ marginTop: 12 }}>Попробовать снова</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="dash-cards--empty"><img src='/icons/empty.svg'/><span>Нет комнат в этой категории</span></div>
        ) : (
          <div className="dash-cards">
            {filtered.map((room, i) => (
              <RoomCard key={room.id} room={room} index={i} tabId={activeTab} onAction={handleCardAction} />
            ))}
          </div>
        )}
      </div>

      {modal?.type === 'create' && (
        <CreateRoomModal room={modal.room} onClose={() => setModal(null)} onCreated={handleRoomCreated} />
      )}
      {modal?.type === 'feedback' && (
        <FeedbackModal room={modal.room} onClose={() => setModal(null)} onSent={handleFeedbackSent} />
      )}
      {modal?.type === 'results' && (
        <ResultsModal room={modal.room} onClose={() => setModal(null)} />
      )}
    </div>
  );
};

