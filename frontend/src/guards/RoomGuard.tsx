import { useParams } from 'react-router-dom';
import { useAuth } from '../shared/auth/AuthContext';
import { CandidateRoom } from '../pages/CandidateRoom/CandidateRoom';
import { InterviewerRoom } from '../pages/InterviewerRoom/InterviewerRoom';
import './room-guard.css'

export const RoomGuard = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const { isInterviewer } = useAuth();

  if (!roomId) {
    return (
      <div className='error'>
        <h2>Комната не найдена</h2>
        <p>Проверьте ссылку и попробуйте снова.</p>
      </div>
    );
  }

  return isInterviewer
    ? <InterviewerRoom roomId={roomId} />
    : <CandidateRoom roomId={roomId} />;
};
