import { useState } from "react";
import {
  completeInterview,
  type NoteItem,
  type MetricItem,
} from '@/shared/api/interviews';

import './compltetion-modal.css'

interface CompletionModalProps {
  metrics: MetricItem[];
  notes: NoteItem[];
  roomId: string;
  onClose: () => void;
  onCompleted: () => void;
}

const timerKey = (roomId: string) => `ir_timer_start_${roomId}`;

const clearPersistedTimer = (roomId: string) => {
  localStorage.removeItem(timerKey(roomId));
}

export const CompletionModal = ({ metrics, notes, roomId, onClose, onCompleted }: CompletionModalProps) => {
  const [passed, setPassed] = useState<boolean | null>(null);
  const [feedback, setFeedback] = useState('');
  const [selectedMetrics, setSelectedMetrics] = useState<Set<string>>(() => new Set(metrics.filter(m => m.value > 0).map(m => m.id)));
  const [selectedNotes, setSelectedNotes] = useState<Set<string>>(() => new Set(notes.map(n => n.id)));
  const [submitting, setSubmitting] = useState(false);

  const toggleMetric = (id: string) => {
    setSelectedMetrics(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleNote = (id: string) => {
    setSelectedNotes(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleAutofill = () => {
    const parts: string[] = [];

    const selected = metrics.filter(m => selectedMetrics.has(m.id) && m.value > 0);
    if (selected.length > 0) {
      parts.push('Оценки:');
      selected.forEach(m => parts.push(`  ${m.name}: ${m.value}/5`));
    }

    const selNotes = notes.filter(n => selectedNotes.has(n.id));
    if (selNotes.length > 0) {
      parts.push('');
      parts.push('Заметки:');
      selNotes.forEach(n => parts.push(`  [${n.timestamp}] ${n.text}`));
    }

    setFeedback(parts.join('\n'));
  };

  const canSubmit = passed !== null;

  const handleSubmit = async () => {
    if (passed === null) return;
    setSubmitting(true);
    try {
      await completeInterview({
        roomId,
        passed,
        metrics: metrics.filter(m => selectedMetrics.has(m.id)),
        notes: notes.filter(n => selectedNotes.has(n.id)),
        feedback,
      });
      clearPersistedTimer(roomId);
      onCompleted();
    } catch (err) {
      console.error('Failed to complete interview:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="cm-overlay" onClick={onClose}>
      <div className="cm-modal" onClick={e => e.stopPropagation()}>
        <div className="cm-header">
          <span className="cm-header__title">Завершение собеседования</span>
          <button className="cm-close" onClick={onClose}>
                <img src='src/assets/Icons/close.svg'/>
            </button>
        </div>

        <div className="cm-body">
          <div>
            <div className="cm-section-label">Результат</div>
            <div className="cm-verdict">
              <button
                className={`cm-verdict__btn cm-verdict__btn--pass${passed === true ? ' cm-verdict__btn--selected' : ''}`}
                onClick={() => setPassed(true)}>
                <img src='src/assets/Icons/pass.svg'/>
                Пройдено
              </button>
              <button
                className={`cm-verdict__btn cm-verdict__btn--fail${passed === false ? ' cm-verdict__btn--selected' : ''}`}
                onClick={() => setPassed(false)}>
                <img src='src/assets/Icons/fail.svg'/>
                 Не пройдено
              </button>
            </div>
          </div>

          <div>
            <div className="cm-section-label">
              Метрики 
              ({metrics.filter(m => selectedMetrics.has(m.id) && m.value > 0).length}/{metrics.length})
            </div>
            <div className="cm-metrics-summary">
              {metrics.map(m => (
                <div key={m.id} className="cm-metric-row" onClick={() => toggleMetric(m.id)}>
                  <div className={`cm-metric-row__check${selectedMetrics.has(m.id) ? ' cm-metric-row__check--on' : ''}`}>
                    {selectedMetrics.has(m.id) &&
                     <img src='src/assets/Icons/check.svg'/>
                    }
                  </div>
                  <span className="cm-metric-row__name">{m.name}</span>
                  {m.value > 0
                    ? <span className="cm-metric-row__val">{m.value}/5</span>
                    : <span className="cm-metric-row__unset">—</span>
                  }
                </div>
              ))}
            </div>
          </div>

          {notes.length > 0 && (
            <div>
              <div className="cm-section-label">
                Заметки
                ({notes.filter(n => selectedNotes.has(n.id)).length}/{notes.length})
              </div>
              <div className="cm-notes-summary">
                {notes.map(n => (
                  <div key={n.id} className="cm-note-row" onClick={() => toggleNote(n.id)}>
                    <div className={`cm-note-row__check${selectedNotes.has(n.id) ? ' cm-note-row__check--on' : ''}`}>
                      {selectedNotes.has(n.id) &&
                       <img src='src/assets/Icons/check.svg'/>
                    }
                    </div>
                    <span className="cm-note-row__ts">{n.timestamp}</span>
                    <span className="cm-note-row__text">{n.text}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="cm-feedback-area">
            <div className="cm-section-label">Фидбек (необязательно)</div>
            <textarea
              className="cm-feedback-textarea"
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="Напишите фидбек вручную или используйте автосбор..."/>
            <button className="cm-autofill-btn" onClick={handleAutofill}>
              <img src='src/assets/Icons/sparkle.svg'/>
            </button>
          </div>
        </div>

        <div className="cm-footer">
          <button className="cm-footer__cancel" onClick={onClose}>Отмена</button>
          <button
            className="cm-footer__submit"
            disabled={!canSubmit || submitting}
            onClick={handleSubmit}>
                <img src="src/assets/Icons/stop.svg"/>
                {submitting ? 'Отправка...' : 'Завершить'}
          </button>
        </div>
      </div>
    </div>
  );
};