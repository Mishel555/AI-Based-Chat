import { chatData, createPendingData, statuses, wsService } from '../ws/WsService';
import {
  ICreateChatParams,
  ICreateChatResponse,
  ICustomAssertionRequestBody,
  IHumanInputRequestBody,
  RequestForResolveToken,
  RequestResponseAssertion,
  ResponseEvidence,
  ResponseStatement,
  ResponseToken,
} from '../types';
import client from '../client';

export interface IChatApi {
  createNewChat: (data: ICreateChatParams) => Promise<ICreateChatResponse>;
  sendHumanInput: (id: string, data: IHumanInputRequestBody) => void;
  sendTokenForResolve: (id: string, data: RequestForResolveToken) => void;
  getToken: (id: string) => Promise<ResponseToken>;
  sendCustomAssertion: (
    id: string,
    data: ICustomAssertionRequestBody,
    statementId?: string
  ) => void;
  getStatement: (id: string) => Promise<ResponseStatement>;
  getAssertions: (id: string) => Promise<RequestResponseAssertion>;
  getEvidence: (id: string) => Promise<ResponseEvidence>;
}

export default (): IChatApi => ({
  async createNewChat(data) {
    const { data: response } = await client.post('validator/chat_session', JSON.stringify(data));

    return response as { id: string; ts: string };
  },
  sendHumanInput(id, data) {
    const promise = new Promise((resolve) => {
      statuses.set(id, resolve);
    });
    chatData.set(id, promise);

    wsService.sendMessage('human_input', JSON.stringify(data));
  },
  sendTokenForResolve(id, data) {
    createPendingData(id);
    wsService.sendMessage('task_token', JSON.stringify(data));
  },
  sendCustomAssertion(id, data, statementId) {
    createPendingData(id);
    wsService.sendMessage('custom_assertion', JSON.stringify({ ...data, statementId }));
  },
  async getToken(id: string) {
    return chatData.get(id);
  },
  async getStatement(id) {
    return chatData.get(id);
  },
  async getAssertions(id) {
    return chatData.get(id);
  },
  async getEvidence(id) {
    return chatData.get(id);
  },
});
