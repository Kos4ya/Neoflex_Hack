import { CodeEditor } from "./CodeEditor/CodeEditor"
import { IRHeader } from "@/widgets/IRHeader/IRHeader"

type CandidateRoomProps = {
    roomId: string;
}

enum Role {
  Candidate = 'Кандидат',
  Interviewer = 'Интервьюер'
}

export const CandidateRoom = ({ roomId }: CandidateRoomProps) => {
    return (
        <div className="ir-root">
            <IRHeader role={Role.Candidate} name='Алексей К.' />
        </div>
    )
}