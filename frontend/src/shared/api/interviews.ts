import { apiFetch, decodeJwt, getAccessToken } from './apiClient';

// ══════════════════════════════════════════════════════════
//  Backend DTOs
// ══════════════════════════════════════════════════════════

export interface RoomDTO {
  id: string;
  candidate_id: string;
  interviewer_id: string;
  vacancy_id: string;
  language: string;
  link: string;               // ignored — используем id для навигации
  result: 'passed' | 'failed' | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateDTO {
  id: string;
  name: string;
  surname: string;
  created_at: string;
  updated_at: string;
}

export interface FeedbackDTO {
  id: string;
  room_id: string;
  text_body: string;
  created_at: string;
  updated_at: string;
}

export interface CreateRoomRequest {
  candidate_id: string;
  interviewer_id: string;
  vacancy_id: string;
  language: string;
}

export interface CreateRoomResponse {
  room_id: string;
  link: string;
}

// ══════════════════════════════════════════════════════════
//  Frontend model
// ══════════════════════════════════════════════════════════

export interface Room {
  id: string;                   // = room UUID, используется для /interview/:roomId
  candidateId: string;
  candidateName: string;
  candidateSurname: string;
  interviewerId: string;
  vacancyId: string;
  language: string;
  result: 'passed' | 'failed' | null;
  hasFeedback: boolean;
  feedbacks: FeedbackDTO[];     // для просмотра в модалке результатов
  createdAt: string;
}

// ══════════════════════════════════════════════════════════
//  Candidate cache
// ══════════════════════════════════════════════════════════

const candidateCache = new Map<string, CandidateDTO>();

async function fetchCandidate(candidateId: string): Promise<CandidateDTO> {
  if (candidateCache.has(candidateId)) {
    return candidateCache.get(candidateId)!;
  }
  const data = await apiFetch<CandidateDTO>(`/vacancy/candidates/${candidateId}`);
  candidateCache.set(candidateId, data);
  return data;
}

// ══════════════════════════════════════════════════════════
//  API — Rooms
// ══════════════════════════════════════════════════════════

/** GET /room/rooms */
async function fetchRooms(): Promise<RoomDTO[]> {
  return apiFetch<RoomDTO[]>('/room/rooms');
}

/** GET /room/{roomId}/feedbacks */
export async function fetchRoomFeedbacks(roomId: string): Promise<FeedbackDTO[]> {
  return apiFetch<FeedbackDTO[]>(`/room/${roomId}/feedbacks`);
}

/**
 * POST /room/rooms
 * Создать комнату. interviewer_id берётся из JWT.
 */
export async function createRoom(
  payload: Omit<CreateRoomRequest, 'interviewer_id'>,
): Promise<CreateRoomResponse> {
  // Достаём interviewer_id из текущего токена
  const token = getAccessToken();
  const jwt = token ? decodeJwt(token) : null;
  const interviewerId = (jwt?.sub ?? jwt?.user_id ?? jwt?.id ?? '') as string;

  return apiFetch<CreateRoomResponse>('/room/rooms', {
    method: 'POST',
    body: JSON.stringify({
      candidate_id: payload.candidate_id,
      interviewer_id: interviewerId,
      vacancy_id: payload.vacancy_id,
      language: payload.language,
    }),
  });
}

/**
 * POST /room/{roomId}/feedbacks
 * Отправить фидбек для комнаты.
 */
export async function sendFeedback(roomId: string, textBody: string): Promise<FeedbackDTO> {
  return apiFetch<FeedbackDTO>(`/room/${roomId}/feedbacks`, {
    method: 'POST',
    body: JSON.stringify({ text_body: textBody }),
  });
}

// ══════════════════════════════════════════════════════════
//  Dashboard data loader
// ══════════════════════════════════════════════════════════

export async function fetchDashboardData(): Promise<Room[]> {
  const rooms = await fetchRooms();

  // Параллельно: кандидаты + фидбеки
  const uniqueCandidateIds = [...new Set(rooms.map((r) => r.candidate_id))];

  const [candidates, feedbackResults] = await Promise.all([
    // Кандидаты
    Promise.all(
      uniqueCandidateIds.map((id) => fetchCandidate(id).catch(() => null)),
    ),
    // Фидбеки для комнат с результатом
    Promise.all(
      rooms.map((r) =>
        r.result !== null
          ? fetchRoomFeedbacks(r.id)
              .then((fb) => ({ roomId: r.id, feedbacks: fb }))
              .catch(() => ({ roomId: r.id, feedbacks: [] as FeedbackDTO[] }))
          : Promise.resolve({ roomId: r.id, feedbacks: [] as FeedbackDTO[] }),
      ),
    ),
  ]);

  const candidateMap = new Map<string, CandidateDTO>();
  candidates.forEach((c) => { if (c) candidateMap.set(c.id, c); });

  const feedbackMap = new Map<string, FeedbackDTO[]>();
  feedbackResults.forEach((f) => feedbackMap.set(f.roomId, f.feedbacks));

  return rooms.map((r): Room => {
    const candidate = candidateMap.get(r.candidate_id);
    const feedbacks = feedbackMap.get(r.id) ?? [];
    return {
      id: r.id,
      candidateId: r.candidate_id,
      candidateName: candidate?.name ?? 'Неизвестный',
      candidateSurname: candidate?.surname ?? '',
      interviewerId: r.interviewer_id,
      vacancyId: r.vacancy_id,
      language: r.language,
      result: r.result,
      hasFeedback: feedbacks.length > 0,
      feedbacks,
      createdAt: r.created_at,
    };
  });
}

// ══════════════════════════════════════════════════════════
//  Completion types (used by InterviewerRoom)
// ══════════════════════════════════════════════════════════

export interface NoteItem {
  id: string;
  text: string;
  timestamp: string;
  createdAt: number;
}

export interface MetricItem {
  id: string;
  name: string;
  value: number;
}

export interface CompleteInterviewPayload {
  roomId: string;
  passed: boolean;
  metrics: MetricItem[];
  notes: NoteItem[];
  feedback: string;
}

export async function completeInterview(payload: CompleteInterviewPayload): Promise<void> {
  await apiFetch(`/room/rooms/${payload.roomId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      result: payload.passed ? 'passed' : 'failed',
    }),
  });

  if (payload.feedback.trim()) {
    await sendFeedback(payload.roomId, payload.feedback);
  }
}
