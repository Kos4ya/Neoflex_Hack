import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { CompletionModal } from './CompletionModal/CompletionModal';
import { Note } from './Note/Note';
import { useTimer } from '@/shared/hooks/useTimer';
import type {  NoteItem, MetricItem } from '../../shared/api/interviews';
import './InterviewerRoom.css';
import { IRHeader } from '@/widgets/IRHeader/IRHeader';

enum Role {
  Candidate = 'Кандидат',
  Interviewer = 'Интервьюер'
}

// TODO: Бд запрос
const INITIAL_METRICS: MetricItem[] = [
  { id: 'problem-solving', name: 'Решение задач', value: 0 },
  { id: 'code-quality', name: 'Качество кода', value: 0 },
  { id: 'communication', name: 'Коммуникация', value: 0 },
  { id: 'system-design', name: 'Системное мышление', value: 0 },
  { id: 'debugging', name: 'Отладка', value: 0 },
];

// TODO: Вебсокет
const CANDIDATE_CODE = '';

type InterviewerRoomProps = {
  roomId: string;
}

export const InterviewerRoom = ({ roomId } : InterviewerRoomProps) => {
  const navigate = useNavigate();
  const timer = useTimer(roomId);

  const [notes, setNotes] = useState<NoteItem[]>([]);
  const [noteInput, setNoteInput] = useState('');
  const notesEndRef = useRef<HTMLDivElement>(null);

  const [metrics, setMetrics] = useState<MetricItem[]>(INITIAL_METRICS);

  const [showCompletion, setShowCompletion] = useState(false);

  const addNote = useCallback(() => {
    const text = noteInput.trim();

    if (!text) return;

    const note: NoteItem = {
      id: `note_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      text,
      timestamp: timer.formatted,
      createdAt: Date.now(),
    };

    setNotes(prev => [...prev, note]);
    setNoteInput('');
    setTimeout(() => notesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
    
  }, [noteInput, timer.formatted]);

  const deleteNote = (id: string) => setNotes(prev => prev.filter(n => n.id !== id));
  const editNote = (id: string, text: string) => setNotes(prev => prev.map(n => n.id === id ? { ...n, text } : n));
  const setMetric = (id: string, value: number) => setMetrics(prev => prev.map(m => m.id === id ? { ...m, value } : m));

  return (
    <div className="ir-root">
      <IRHeader role={Role.Interviewer} name='Алексей К.' />

      <div className="ir-main">
        <div className="ir-main__editor">
          <div className="ir-monaco-wrap">
            <Editor
              height="100%"
              defaultLanguage="typescript"
              defaultValue={CANDIDATE_CODE}
              theme="vs-dark"
              options={{
                readOnly: true,
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 16 },
                lineNumbersMinChars: 3,
                automaticLayout: true,
                domReadOnly: true,
                renderLineHighlight: 'none',
                cursorStyle: 'line-thin',
              }}
            />
          </div>
        </div>

        <div className="ir-main__panel">
          <div className="ir-panel">
            <div className="ir-timer">
              <div className="ir-timer__icon">
                  <img src='src/assets/Icons/clock.svg'/>
                </div>
              <div className="ir-timer__info">
                <span className="ir-timer__time">{timer.mm}:{timer.ss}</span>
                <span className="ir-timer__label">Время интервью</span>
              </div>
            </div>

            <div className="ir-panel__body">
              <div className="ir-panel__section">
                <div className="ir-panel__section-header">
                  <span className="ir-panel__section-title">
                    <img src='srs/assets/Icons/notes.svg'/> 
                    Заметки
                    {notes.length > 0 && (
                      <span className="ir-panel__section-count">{notes.length}</span>
                    )}
                  </span>
                </div>
                <div className="ir-notes">
                  <div className="ir-notes__input-wrap">
                    <input
                      className="ir-notes__input"
                      value={noteInput}
                      onChange={e => setNoteInput(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') addNote(); }}
                      placeholder="Напишите заметку и нажмите Enter..."
                    />
                  </div>
                  <div className="ir-notes__list">
                    {notes.length === 0 ? (
                      <div className="ir-notes__empty">Пока нет заметок</div>
                    ) : (
                      <>
                        {notes.map(n => (
                          <Note key={n.id} note={n} onDelete={deleteNote} onEdit={editNote} />
                        ))}
                        <div ref={notesEndRef} />
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="ir-panel__section">
                <div className="ir-panel__section-header">
                  <span className="ir-panel__section-title">
                    <img src='src/assets/Icons/metrics.svg' />
                     Оценка
                  </span>
                </div>
                <div className="ir-metrics">
                  {metrics.map(m => (
                    <div key={m.id} className="ir-metric">
                      <div className="ir-metric__header">
                        <span className="ir-metric__name">{m.name}</span>
                        <span className="ir-metric__value">{m.value > 0 ? `${m.value}/5` : '—'}</span>
                      </div>
                      <div className="ir-metric__segments">
                        {[1, 2, 3, 4, 5].map(lvl => (
                          <div
                            key={lvl}
                            className={`ir-metric__seg ${lvl <= m.value ? 'ir-metric__seg--on' : 'ir-metric__seg--off'}`}
                            data-level={lvl}
                            onClick={() => setMetric(m.id, lvl)}
                          />
                        ))}
                      </div>
                      <div className="ir-metric__labels">
                        <span>Слабо</span>
                        <span>Отлично</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="ir-finish-bar">
              <button className="ir-finish-btn" onClick={() => setShowCompletion(true)}>
                <img src='src/assets/Icons/stop.svg'/>
                Завершить собеседование
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="ir-status">
        <div className="ir-status__left">
          <span className="ir-status__dot" />
          <span>Подключено</span>
          <span className="ir-status__sep">•</span>
          <span>Комната: #{roomId}</span>
        </div>
        <div className="ir-status__right">
          <span>WebSocket</span>
          <span className="ir-status__sep">•</span>
          <span>Latency: 18ms</span>
        </div>
      </div>

      {showCompletion && (
        <CompletionModal
          metrics={metrics}
          notes={notes}
          roomId={roomId}
          onClose={() => setShowCompletion(false)}
          onCompleted={() => navigate('/')}/>
      )}
    </div>
  );
};

