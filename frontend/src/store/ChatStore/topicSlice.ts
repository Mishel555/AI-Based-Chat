import { StateCreator } from 'zustand';
import { produce } from 'immer';
import { v4 as uuid } from 'uuid';
import {
  AllMessageTypes,
  BotMessage,
  ErrorMessage,
  EvidenceMessage,
  MessageAuthor,
  TopicType,
  UserMessage,
} from '~/types';
import { useChatStore } from '~/store';
import { cacheService } from '~/api/cache';
import { DBService } from '~/api/localDB';
import { Evidence } from '~/api/types';

export interface ITopicSlice {
  topics: TopicType[];
  lastMessage: () => AllMessageTypes | null;
  activeTopic: () => TopicType | null;
  addTopic: (topicId: string, topicTitle: string) => void;
  addBotMessage: (topicId: string, id: string, message: string) => void;
  addErrorMessage: (topicId: string, id: string, message: string) => void;
  addUserMessage: (topicId: string, message: string) => void;
  addEvidenceMessage: (topicId: string, id: string, message: string, evidence: Evidence) => void;
  addMessage: (topicId: string, messageObj: AllMessageTypes) => void;
  updateTopicTitle: (id: string, title: string) => void;
  updateTopicDate: (id: string, date: string) => void;
  updateMessage: (topicId: string, id: string, newMessage: string) => void;
  deleteFollowingMessages: (topicId: string, id: string, newMessage: string) => void;
  deleteTopic: (id: string) => void;
  deleteTopicById: (id: string) => void;
  deleteMessage: (topicId: string, id: string) => void;
  loadTopics: () => void;
  saveTopics: () => void;
}

const createBotMessage = (id: string, message: string): BotMessage => ({
  id,
  message: message,
  type: MessageAuthor.BOT,
});

const createErrorMessage = (id: string, message: string): ErrorMessage => ({
  id,
  message: message,
  type: MessageAuthor.ERROR,
});

const createUserMessage = (message: string): UserMessage => ({
  id: uuid(),
  message,
  type: MessageAuthor.USER,
});

export const createEvidenceMessage = (
  id: string,
  message: string,
  evidence: Evidence
): EvidenceMessage => ({ id, evidence, type: MessageAuthor.EVIDENCE, message });

const createTopic = (id: string, title: string, messages: TopicType['messages']): TopicType => {
  const date = new Date().toISOString();

  return {
    id,
    title,
    messages,
    createdDate: date,
    updatedDate: date,
  };
};

export const createTopicSlice: StateCreator<ITopicSlice> = (set, get) => ({
  topics: [],
  lastMessage: () => get().activeTopic()?.messages.at(-1) || null,
  activeTopic: () => get().topics.find((t) => t.id === useChatStore.getState().currentChat) || null,
  addTopic: (id, topicTitle) =>
    set(
      produce((state: ITopicSlice) => {
        const newTopic = createTopic(id, topicTitle.substring(0, 25), []);
        state.topics.unshift(newTopic);
      })
    ),
  addBotMessage: (topicId, id, message) => {
    get().addMessage(topicId, createBotMessage(id, message));
  },
  addErrorMessage: (topicId, id, message) => {
    get().addMessage(topicId, createErrorMessage(id + 'error', message));
  },
  addUserMessage: (topicId, message) => {
    const date = new Date().toISOString();

    get().addMessage(topicId, createUserMessage(message));
    get().updateTopicDate(topicId, date);
  },
  addEvidenceMessage: (topicId, id, message, evidence) => {
    get().addMessage(topicId, createEvidenceMessage(id, message, evidence));
  },
  addMessage: (topicId, messageObj) =>
    set(
      produce((state: ITopicSlice) => {
        const topic = state.topics.find((topic) => topic.id === topicId);
        if (topic) {
          topic.messages.push(messageObj);
        }
      })
    ),
  updateTopicTitle: (id, title) =>
    set(
      produce((state: ITopicSlice) => {
        const topic = state.topics.find((topic) => topic.id === id);
        if (topic) topic.title = title;
      })
    ),
  updateTopicDate: (id, date) =>
    set(
      produce((state: ITopicSlice) => {
        const topic = state.topics.find((topic) => topic.id === id);
        if (topic) topic.updatedDate = date;
      })
    ),
  updateMessage: (topicId, id, newMessage) => {
    useChatStore.getState().deleteFollowingMessages(topicId, id, newMessage);
    useChatStore.getState().sendHumanMessage(topicId, newMessage);
    const topic = get().activeTopic();

    if (topic) {
      cacheService.deleteAfterUpdate(
        topic.id,
        topic.messages.map((m) => m.id)
      );
    }
  },
  deleteFollowingMessages: (topicId, id, newMessage) =>
    set(
      produce((state: ITopicSlice) => {
        const topic = state.topics.find((topic) => topic.id === topicId);
        if (topic) {
          const messageIdx = topic.messages.findIndex((msg) => msg.id === id);
          if (messageIdx > -1) {
            topic.messages[messageIdx].message = newMessage;
            topic.messages.splice(messageIdx);
          }
        }
      })
    ),
  deleteTopic: (id: string) => {
    useChatStore.getState().deleteTopicById(id);
    cacheService.deleteData(id);
  },
  deleteTopicById: (id: string) =>
    set(
      produce((state: ITopicSlice) => {
        state.topics = state.topics.filter((topic) => topic.id !== id) || state.topics;
      })
    ),
  deleteMessage: (topicId, id) =>
    set(
      produce((state: ITopicSlice) => {
        const topic = state.topics.find((topic) => topic.id === topicId);
        if (topic) {
          topic.messages = topic.messages.filter((message) => message.id !== id);
        }
      })
    ),
  saveTopics: () => {
    const { topics } = get();

    if (topics) {
      DBService.saveTopics(topics);
    }
  },
  loadTopics: () =>
    set(
      produce((state: ITopicSlice) => {
        state.topics = DBService.loadTopics();
      })
    ),
});
