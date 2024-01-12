import { StateCreator } from 'zustand';
import { v4 as uuid } from 'uuid';
import api from '~/api';
import { useInputStore } from '~/modules/Chat';
import { useChatStore, useAssertionStore } from '~/store';
import { ACTIONS } from '~/modules/Chat/constants';
import { toast } from 'react-toastify';
import { createTokenId } from '~/api/ws/handlers/onmessage';
import { cacheService } from '~/api/cache';

const createDataForHumanInputMessage = (chatId: string, extra: string, newMessage: string) => {
  return {
    chat_id: chatId,
    chat_ts: new Date().toISOString(),
    ts: new Date().toISOString(),
    human_input: newMessage,
    extra,
  };
};

export const createDataCustomAssertionMessage = (
  chatId: string,
  extra: string,
  assertion: string
) => {
  return {
    chat_id: chatId,
    chat_ts: new Date().toISOString(),
    ts: new Date().toISOString(),
    assertion,
    extra,
  };
};

const createDataForResolveToken = (chat_id: string, statementId: string, token: string) => {
  return {
    ts: new Date().toISOString(),
    chat_ts: new Date().toISOString(),
    id: statementId,
    chat_id,
    task_token: token,
  };
};

export interface ISendMessageSlice {
  sendHumanMessage: (chatId: string, newMessage: string) => void;
  sendActionMessage: (chatId: string, message: string) => void;
  sendAssertionToken: (
    chatId: string,
    statementId: string,
    token: string
  ) => {} | { error: string };
  sendEvidenceToken: (chatId: string, assertionId: string) => void;
}

export const createSendMessageSlice: StateCreator<ISendMessageSlice> = () => ({
  sendEvidenceToken: async (chatId, assertionId) => {
    const { task_token: token } = await api.chat.getToken(createTokenId(assertionId));
    const data = createDataForResolveToken(chatId, assertionId, token);
    cacheService.deleteItem(chatId, createTokenId(assertionId));
    await api.chat.sendTokenForResolve(assertionId, data);

    api.chat.getEvidence(assertionId);
  },
  sendAssertionToken: async (chatId, statementId, token) => {
    const data = createDataForResolveToken(chatId, statementId, token);
    cacheService.deleteItem(chatId, createTokenId(statementId));
    api.chat.sendTokenForResolve(statementId, data);
    const assertionResponse = await api.chat.getAssertions(statementId);

    if ('error' in assertionResponse) {
      if (assertionResponse.error === 'No assertions were generated')
        return { error: 'No assertions were generated' };

      toast.error(`Something went wrong with generating assertions.`, {
        closeButton: false,
      });
      return { error: assertionResponse.error };
    }

    const { ids, assertions: assertionList } = assertionResponse;
    useAssertionStore.getState().setAssertions(assertionList, ids);
  },
  sendHumanMessage: async (chatId, newMessage) => {
    useInputStore.getState().setCanWrite(false);
    useInputStore.getState().change('');
    useChatStore.getState().addUserMessage(chatId, newMessage);

    const extra = uuid();
    const data = createDataForHumanInputMessage(chatId, extra, newMessage);

    api.chat.sendHumanInput(extra, data);

    const tempMsgId = uuid();
    useChatStore.getState().addBotMessage(chatId, tempMsgId, '');
    useAssertionStore.getState().setAssertions([], []);

    const {
      statement: message,
      id: statementId,
      error: statementError,
    } = await api.chat.getStatement(extra);

    useInputStore.getState().setCanWrite(true);
    useChatStore.getState().deleteMessage(chatId, tempMsgId);

    if (statementError) {
      return useChatStore.getState().addErrorMessage(chatId, statementId, statementError);
    }

    useChatStore.getState().addBotMessage(chatId, statementId, message);
  },
  sendActionMessage: async (chatId, message) => {
    useInputStore.getState().setCanWrite(false);
    useChatStore.getState().addUserMessage(chatId, message);
    // const assertions = useAssertionStore.getState().assertions;
    // const assertionIds = useAssertionStore.getState().assertionIds;
    const clearValue = message.replace(`${ACTIONS.EXPLORE} `, '');
    // const assertionIdx = assertions.findIndex((assertion) => clearValue === assertion);

    useInputStore.getState().change('');

    const assertionId = uuid();
    const data = createDataCustomAssertionMessage(chatId, assertionId, clearValue);
    api.chat.sendCustomAssertion(assertionId, data);

    const tempMsgId = uuid();
    useChatStore.getState().addBotMessage(chatId, tempMsgId, '');
    const {
      id: evidenceId,
      evidence,
      error: evidenceError,
    } = await api.chat.getEvidence(assertionId);

    useInputStore.getState().setCanWrite(true);
    useChatStore.getState().deleteMessage(chatId, tempMsgId);

    if (evidenceError) {
      return useChatStore.getState().addErrorMessage(
        chatId,
        evidenceId,
        `
        Something went wrong with generating assertions.
        Error: ${evidenceError}
      `
      );
    }
    useChatStore.getState().deleteMessage(chatId, tempMsgId);
    useChatStore
      .getState()
      .addEvidenceMessage(chatId, evidenceId, 'Assertion: ' + clearValue, evidence);
    useInputStore.getState().setCanWrite(true);
  },
});
