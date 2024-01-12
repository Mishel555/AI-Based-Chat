import { MessageAuthor } from '~/types';
import { Avatar, Message } from '~/ui';
import MessageForm from '../MessageForm';
import { micromark } from 'micromark';
import { useStreamMessageStore } from '~/store';
import classNames from 'classnames';
import styles from './style.module.css';
import { useInputStore } from '~/modules/Chat';

type PropsType = {
  message: string;
  isLast: boolean;
  editable?: boolean;
  type: MessageAuthor;
  onCancel: () => void;
  onSubmit: (newMessage: string) => void;
};

const avatarMap = {
  [MessageAuthor.BOT]: 'chatgpt1.png',
  [MessageAuthor.USER]: 'chatgpt.png',
  [MessageAuthor.EVIDENCE]: 'flagship.jpg',
  [MessageAuthor.ERROR]: 'chatgpt-error.png',
};

const DefaultMessage = ({ messageFull }: { messageFull: string }) => {
  const isCanWrite = useInputStore((state) => state.isCanWrite);
  const isActiveStream = useStreamMessageStore((state) => state.isActiveStream);
  const messageStream = useStreamMessageStore((state) => state.message);

  const message = isActiveStream ? messageStream : messageFull;

  return (
    <p
      dangerouslySetInnerHTML={{ __html: micromark(message) }}
      className={classNames(
        styles.root__message,
        styles.last_message,
        !isCanWrite && styles.message_loading
      )}
    />
  );
};

const MessageContent = ({ message, editable, onSubmit, onCancel, type, isLast }: PropsType) => {
  return (
    <div className={styles.root}>
      <Avatar src={`./${avatarMap[type]}`} />

      {type === MessageAuthor.ERROR && <Message message={message} />}

      {editable && <MessageForm defaultValue={message} onSubmit={onSubmit} onCancel={onCancel} />}

      {!editable &&
        type !== MessageAuthor.ERROR &&
        (!isLast ? (
          <p
            dangerouslySetInnerHTML={{ __html: micromark(message) }}
            className={styles.root__message}
          />
        ) : (
          <DefaultMessage messageFull={message} />
        ))}
    </div>
  );
};

export default MessageContent;
