import { Evidence } from '~/api/types';

export enum MessageAuthor {
  BOT = 'BOT',
  USER = 'USER',
  EVIDENCE = 'EVIDENCE',
  ERROR = 'ERROR',
}

export type UserType = {
  id: string;
  email: string;
  avatar: string;
};

export type TopicType = {
  id: string;
  title: string;
  createdDate: string;
  updatedDate: string;
  messages: Array<AllMessageTypes>;
};

export type AllMessageTypes = BotMessage | UserMessage | EvidenceMessage | ErrorMessage;

export interface BotMessage {
  id: string;
  message: string;
  type: MessageAuthor.BOT;
}

export interface ErrorMessage {
  id: string;
  message: string;
  type: MessageAuthor.ERROR;
}

export interface UserMessage {
  id: string;
  message: string;
  type: MessageAuthor.USER;
}

export interface EvidenceMessage {
  id: string;
  message: string;
  evidence: Evidence;
  type: MessageAuthor.EVIDENCE;
}
