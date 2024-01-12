import { useState } from 'react';
import classNames from 'classnames';
import { AllMessageTypes, MessageAuthor } from '~/types';
import { useChatStore } from '~/store';
import { copyTextToClipboard } from '~/utils/copyTextToClipboard';
import { useValidationSidebarStore } from '~/modules/ValidationSidebar/ValidationSidebar';
import MessageActionList from './MessageActionList';
import MessageContent from './MessageContent';
import MessageEvidenceList from './MessageEvidenceList';
import {
  CopyComponent,
  EditComponent,
  EyeComponent,
  RegenerateComponent,
  ValidationOpenButton,
} from './ActionComponents';
import styles from './ChatMessage.module.css';

type PropsType = {
  topicId: string;
  data: AllMessageTypes;
  isLast: boolean;
};

const ChatMessage = ({ data, topicId: chatId, isLast }: PropsType) => {
  const open = useValidationSidebarStore((state) => state.open);
  const setStatementId = useValidationSidebarStore((state) => state.setStatementId);
  const deleteMessage = useChatStore((state) => state.deleteMessage);
  const updateMessage = useChatStore((state) => state.updateMessage);

  const { message, type, id } = data;
  const user = type === MessageAuthor.USER;
  const ai = type === MessageAuthor.BOT;
  const evidence = type === MessageAuthor.EVIDENCE;

  const [isEditable, setIsEditable] = useState<boolean>(false);

  const saveMessage = (newMessage: string) => {
    if (newMessage) {
      updateMessage(chatId, id, newMessage);
    } else {
      deleteMessage(chatId, id);
    }

    setIsEditable(false);
  };

  const copyMessage = async (message: string) => {
    try {
      await copyTextToClipboard(message);
    } catch (e) {
      console.log(e);
    }
  };

  const handleOpen = () => {
    setStatementId(id);
    open();
  };

  const editMessage = () => setIsEditable(true);
  const cancelEdit = () => setIsEditable(false);

  const UserActions = () => (
    <>
      <EditComponent action={editMessage} />
    </>
  );

  const BotActions = () => (
    <>
      <CopyComponent action={() => copyMessage(data.message)} />
      <ValidationOpenButton chatId={chatId} statementId={id} action={handleOpen} />
    </>
  );

  const ErrorActions = () => (
    <>
      <CopyComponent action={() => copyMessage(data.message)} />
      <RegenerateComponent action={() => console.log('regenerate')} />
    </>
  );

  const EvidenceActions = () => (
    <>
      <CopyComponent action={() => copyMessage(data.message)} />
      <EyeComponent action={() => console.log('hello book')} />
    </>
  );

  const actionComponents: Record<MessageAuthor, () => JSX.Element> = {
    [MessageAuthor.USER]: UserActions,
    [MessageAuthor.BOT]: BotActions,
    [MessageAuthor.ERROR]: ErrorActions,
    [MessageAuthor.EVIDENCE]: EvidenceActions,
  };

  const MessageActions = actionComponents[data.type];

  return (
    <div
      className={classNames(
        styles.root,
        user && styles.hide_controls,
        ai && styles.ai_background,
        evidence && styles.evidence_background
      )}
    >
      <div className={styles.root__wrapper}>
        <div className={styles.root__content}>
          <MessageContent
            type={type}
            message={message}
            editable={isEditable}
            isLast={isLast}
            onCancel={cancelEdit}
            onSubmit={saveMessage}
          />
          <MessageActionList ai={ai}>
            <MessageActions />
          </MessageActionList>
        </div>
        {type === MessageAuthor.EVIDENCE && (
          <MessageEvidenceList data={data} copyMessage={copyMessage} />
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
