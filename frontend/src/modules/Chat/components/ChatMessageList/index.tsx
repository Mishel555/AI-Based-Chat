import { useEffect, useRef } from 'react';
import classNames from 'classnames';
import { AllMessageTypes } from '~/types';
import { useInputStore } from '~/modules/Chat';
import ChatScrollDown from '../ChatScrollDown';
import ChatMessage from '../ChatMessage/ChatMessage';
import styles from './style.module.css';

type PropsType = {
  topicId: string;
  data: AllMessageTypes[];
};

const ChatMessageList = ({ data, topicId }: PropsType) => {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const isCanWrite = useInputStore((state) => state.isCanWrite);

  const scrollDown = () => {
    if (rootRef.current) {
      rootRef.current.scrollTo({ behavior: 'smooth', top: rootRef.current.scrollHeight });
    }
  };

  useEffect(() => {
    scrollDown();
  }, [data]);

  useEffect(() => {
    if (rootRef.current) {
      rootRef.current.scrollTop = rootRef.current.scrollHeight;
    }
  }, []);

  return (
    <div ref={rootRef} className={classNames(styles.root, !isCanWrite && styles.message_loading)}>
      <ChatScrollDown parentRef={rootRef} onClick={scrollDown} />

      {data.map((message, index, array) => (
        <ChatMessage
          key={message.id}
          topicId={topicId}
          data={message}
          isLast={array.length - 1 === index}
        />
      ))}
    </div>
  );
};

export default ChatMessageList;
