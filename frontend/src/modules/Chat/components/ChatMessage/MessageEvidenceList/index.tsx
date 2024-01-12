import { EvidenceMessage } from '~/types';
import styles from './style.module.css';
import MessageEvidence from '~/modules/Chat/components/ChatMessage/MessageEvidence';

interface OldEvidenceMessage {
  evidence: string;
}

export interface EvidenceMap {
  id: string;
  score: string;
  verdict: string;
  explanation: string;
  leapUrl: string;
}

type PropsType = {
  data: EvidenceMessage | OldEvidenceMessage;
  copyMessage: (message: string) => void;
};

const MessageEvidenceList = ({ data, copyMessage }: PropsType) => {
  console.log(data);
  if (typeof data.evidence === 'string') {
    return <ol className={styles.errorEvidenceMessage}>Not supported Evidence format</ol>;
  }

  const { evidence } = data as EvidenceMessage;
  const summary = evidence.Summary;
  const finalVerdict = evidence['Final Verdict'];

  const evidenceList = Object.keys(evidence).reduce((acc: EvidenceMap[], key) => {
    if (key !== 'Summary' && key !== 'Final Verdict') {
      const evidenceItem = evidence[key];
      acc.push({
        id: evidenceItem.ID,
        score: evidenceItem.Score,
        verdict: evidenceItem.Verdict,
        explanation: evidenceItem.Explanation,
        leapUrl: evidenceItem.leap_url,
      });
    }
    return acc;
  }, []);

  return (
    <>
      <ol className={styles.messageEvidenceList}>
        {evidenceList.map((evidence) => (
          <MessageEvidence key={evidence.id} copyMessage={copyMessage} content={evidence} />
        ))}
      </ol>

      <div className={styles.summary}>
        <p>Summary: {summary}</p>
        <p>Final Verdict: {finalVerdict}</p>
      </div>
    </>
  );
};

export default MessageEvidenceList;
