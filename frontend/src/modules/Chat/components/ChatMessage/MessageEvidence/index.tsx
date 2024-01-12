import React from 'react';
import { CopyComponent } from '../ActionComponents';
import MessageActionList from '../MessageActionList';
import styles from './style.module.css';
import { EvidenceMap } from '../MessageEvidenceList';
import { micromark } from 'micromark';

type PropsType = {
  content: EvidenceMap;
  copyMessage: (message: string) => void;
};

const MessageEvidence = ({ content, copyMessage }: PropsType) => {
  const MessageActions = () => (
    <>
      <CopyComponent action={() => copyMessage(content.explanation)} />
    </>
  );

  return (
    <li className={styles.root}>
      <div className={styles.root__content}>
        <div className={styles.message}>
          <p dangerouslySetInnerHTML={{ __html: micromark(content.id) }} />
          <p>{content.explanation}</p>
          <p>Score: {content.score}</p>
          <p>Verdict: {content.verdict}</p>
          <p>
            <a href={content.leapUrl}>Leap</a>
          </p>
        </div>
        <ul className={styles.root__wrapper}>
          <MessageActionList ai={false}>
            <MessageActions />
          </MessageActionList>
        </ul>
      </div>
    </li>
  );
};

export default MessageEvidence;
