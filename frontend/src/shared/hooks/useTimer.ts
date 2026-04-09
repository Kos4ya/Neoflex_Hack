import { useEffect, useRef, useState } from "react";

const timerKey = (roomId: string) => `ir_timer_start_${roomId}`;

const getPersistedStart = (roomId: string): number => {
  const raw = localStorage.getItem(timerKey(roomId));
  const now = Date.now();

  if (raw) return parseInt(raw, 10);
  localStorage.setItem(timerKey(roomId), String(now));

  return now;
}

export const useTimer = (roomId: string) => {
  const startRef = useRef(getPersistedStart(roomId));
  const [elapsed, setElapsed] = useState(0);

  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  const formatted = `${mm}:${ss}`;

  useEffect(() => {
    startRef.current = getPersistedStart(roomId);
    setElapsed(Math.floor((Date.now() - startRef.current) / 1000));

    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
    }, 1000);

    return () => clearInterval(id);
  }, [roomId]);

  return { elapsed, mm, ss, formatted };
}