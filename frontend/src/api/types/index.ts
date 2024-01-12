import { IChatApi } from '~/api/apis/Chat';
import { AuthApi } from '~/api/apis/Auth';

export enum ResponseType {
  STATEMENT = 'statement',
  ASSERTIONS = 'assertions',
  EVIDENCE = 'evidence',
  STREAM = 'stream',
  TASK_TOKEN = 'task_token',
}

export enum StepType {
  STATEMENT = 'statement',
  ASSERTIONS = 'assertions',
}

export type CommonResponse =
  | ResponseStatement
  | RequestResponseAssertion
  | ResponseEvidence
  | ResponseStream
  | ResponseToken;

export interface ResponseStream {
  id: string;
  chat_id: string;
  message: string;
  type: ResponseType.STREAM;
  extra: string;
}
export interface ResponseStatement {
  ts: string;
  chat_id: string;
  chat_ts: string;
  id: string;
  human_input_id: string;
  statement: string;
  extra: string;
  type: ResponseType.STATEMENT;
  error?: string;
}

interface AssertionResponseError {
  error: string;
  ts: string;
  chat_id: string;
  chat_ts: string;
  extra: string;
  type: ResponseType.ASSERTIONS;
  statement_id: string;
}

export interface ResponseAssertion {
  ts: string;
  chat_id: string;
  chat_ts: string;
  ids: string[];
  statement_id: string;
  assertions: string[];
  type: ResponseType.ASSERTIONS;
}

// TODO add better errors to all responses
export type RequestResponseAssertion = AssertionResponseError | ResponseAssertion;

export interface ResponseEvidence {
  ts: string;
  chat_ts: string;
  chat_id: string;
  extra: string;
  type: ResponseType.EVIDENCE;
  id: string;
  assertion_id: string;
  evidence: Evidence;
  error?: string;
}

export type Evidence = EvidenceItem & EvidenceSummary;

interface EvidenceItem {
  [key: string]: {
    ID: string;
    Score: string;
    Verdict: string;
    Explanation: string;
    leap_url: string;
  };
}

interface EvidenceSummary {
  Summary: string;
  'Final Verdict': string;
}

export interface ResponseToken {
  id: string;
  chat_id: string;
  type: ResponseType.TASK_TOKEN;
  task_token: string;
  step_type: StepType.STATEMENT | StepType.ASSERTIONS;
  ts: string;
  chat_ts: string;
  extra?: string;
}

export interface RequestForResolveToken {
  ts: string;
  chat_ts: string;
  id: string;
  chat_id: string;
  task_token: string;
}

export interface IHumanInputRequestBody {
  chat_id: string;
  chat_ts: string;
  ts: string;
  human_input: string;
  extra: string;
}

export interface ICustomAssertionRequestBody {
  chat_id: string;
  chat_ts: string;
  ts: string;
  assertion: string;
  extra: string;
}

export interface ICreateChatParams {
  ts: string;
}

export interface ICreateChatResponse {
  id: string;
  ts: string;
}

export interface IApi {
  auth: AuthApi;
  chat: IChatApi;
}
