import { useEffect } from 'react';
import { cacheService } from '~/api/cache';
import { useChatStore } from '~/store';
import ChatPage from './pages/ChatPage';

const App = () => {
  const topics = useChatStore((state) => state.topics);
  const loadTopics = useChatStore((state) => state.loadTopics);
  const saveTopics = useChatStore((state) => state.saveTopics);

  useEffect(() => {
    loadTopics();
  }, [loadTopics]);

  // implemented temporary DB...
  useEffect(() => {
    saveTopics();

    if (topics.length > 0) {
      cacheService.restoreFromCache(topics.map((chat) => chat.id));
    }
  }, [topics]);

  return <ChatPage />;
};

export default App;
