import { useAuthStore, useChatStore } from '~/store';
import ChatMessageList from '../ChatMessageList';
import ChatPlaceholder from '../ChatPlaceholder';
import ChatForm from '../ChatForm';

import styles from './style.module.css';

const ChatWidget = () => {
  const user = useAuthStore(state => state.user);
  const activeTopic = useChatStore((state) => state.activeTopic());

  return (
    <div className={styles.root}>
      {activeTopic && <ChatMessageList key={activeTopic.id} topicId={activeTopic.id} data={activeTopic.messages} />}
      {!activeTopic && <ChatPlaceholder />}
      {user && <ChatForm />}
    </div>
  );
};

export default ChatWidget;
