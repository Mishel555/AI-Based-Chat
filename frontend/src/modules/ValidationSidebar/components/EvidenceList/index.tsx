import { useEffect, useState } from 'react';
import api from '~/api';
import { EvidenceMessage } from '~/types';
import { copyTextToClipboard } from '~/utils/copyTextToClipboard';
import { Message } from '~/ui';
import { useChatStore } from '~/store';
import { getChatData } from '~/api/ws/WsService';
import { MessageEvidenceList } from '~/modules/Chat';
import { createEvidenceMessage } from '~/store/ChatStore/topicSlice';
import { createDataCustomAssertionMessage } from '~/store/ChatStore/sendMessageSlice';
import styles from './style.module.css';

interface PropsType {
  assertionId: string;
  statementId: string;
  assertionValue: string;
}

const EvidenceList = ({ assertionId, assertionValue, statementId }: PropsType) => {
  const chatId = useChatStore((state) => state.currentChat);
  const [evidenceError, setEvidenceError] = useState<string | null>(null);
  const [evidenceMessage, setEvidenceMessage] = useState<EvidenceMessage | null>(null);

  const fetchEvidence = async (assertId: string) => {
    const { id, evidence, error: evidenceError } = await api.chat.getEvidence(assertId);

    if (evidenceError) {
      return setEvidenceError(evidenceError);
    }

    const msg = createEvidenceMessage(id, 'Assertion: ' + assertionValue, evidence);
    setEvidenceMessage(msg);
  };

  const fetchEvidenceFromCustomAssertion = async (assertId: string) => {
    if (!chatId) return;
    const data = createDataCustomAssertionMessage(chatId, assertId, assertionValue);
    api.chat.sendCustomAssertion(assertId, data, statementId);
    await fetchEvidence(assertId);
  };

  const copyMessage = async (message: string) => {
    try {
      await copyTextToClipboard(message);
    } catch (e) {
      console.log(e);
    }
  };

  useEffect(() => {
    const isAssertionCustom = !getChatData().has(assertionId);
    if (isAssertionCustom) fetchEvidenceFromCustomAssertion(assertionId);
    else fetchEvidence(assertionId);
  }, []);

  return (
    <div className={styles.validation_sidebar_evidence}>
      {!evidenceError && !evidenceMessage && <ol>Loading...</ol>}
      {!!evidenceError && (
        <Message message={`Something went wrong with loading evidences. Error: ${evidenceError}`} />
      )}
      {evidenceMessage && <MessageEvidenceList data={evidenceMessage} copyMessage={copyMessage} />}
    </div>
  );
};

export default EvidenceList;
