export interface SessionDTO {
  id: string;
  candidateFirstName: string;
  candidateLastName: string;
  vacancy: string;
  scheduledAt: string;
  roomLink: string | null;
  language: string | null;
  result: number | null;
  feedback: string | null;
}

interface InterviewDto {
  id: string | null;
  vacancy_id: string;
  candidate_id: string;
  interviewer_id: string;
  manager_id: string;
  status: string;
  language: string;
  scheduled_start_at: string;
  scheduled_end_at: string;
  actual_started_at: string;
  actual_ended_at: string;
  paused_at: string;
  total_paused_duration_seconds: number;
  created_at: string;
  updated_at: string;
}

export interface MetricDTO {


}
 
export interface CreateRoomPayload {
  interviewId: string;
  language: string;
}
 
export interface CreateRoomResponse {
  roomLink: string;
}