import { TopicType } from '~/types';

const LOCAL_STORAGE_KEY = 'EXPLORATION_COPILOT_TOPICS';

const saveTopics = (data: TopicType[]): void => {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
};

const loadTopics = (): TopicType[] => {
  const savedMessages = localStorage.getItem(LOCAL_STORAGE_KEY);

  if (savedMessages) {
    return JSON.parse(savedMessages);
  }

  return [];
};

const updateTopicDate = (topicId: string) => {
  const topics = loadTopics();
  const currentTopicIndex = topics.findIndex(topic => topic.id === topicId);

  if (currentTopicIndex > -1) {
    topics[currentTopicIndex].updatedDate = new Date().toISOString();
  }

  saveTopics(topics);
};

export const DBService = {
  saveTopics,
  loadTopics,
  updateTopicDate,
};
