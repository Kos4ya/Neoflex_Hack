import { useEffect, useRef, useState } from "react";
import {
  type NoteItem,
} from '@/shared/api/interviews';

import './note.css'

type NoteProps = {
  note: NoteItem;
  onDelete: (id: string) => void;
  onEdit: (id: string, text: string) => void;
}

export const Note = ({ note, onDelete, onEdit }: NoteProps) => {
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(note.text);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  const save = () => {
    if (editText.trim()) {
      onEdit(note.id, editText.trim());
    }
    setEditing(false);
  };

  return (
    <div className="ir-note">
      <span className="ir-note__timestamp">{note.timestamp}</span>
      {editing ? (
        <input
          ref={inputRef}
          className="ir-note__edit-input"
          value={editText}
          onChange={(e) => setEditText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') save();
            if (e.key === 'Escape') { setEditText(note.text); setEditing(false); }
          }}
          onBlur={save}
        />
      ) : (
        <span className="ir-note__text">{note.text}</span>
      )}
      <div className="ir-note__actions">
        <button className="ir-note__btn" onClick={() => { setEditText(note.text); setEditing(true); }}>
          <img src='src/assets/Icons/edit.svg' />
        </button>
        <button className="ir-note__btn ir-note__btn--delete" onClick={() => onDelete(note.id)}>
          <img src='src/assets/Icons/trash.svg' />
        </button>
      </div>
    </div>
  );
};