import { createPendingData, statuses } from '~/api/ws/WsService';
import {
  CommonResponse,
  RequestResponseAssertion,
  ResponseEvidence,
  ResponseStream,
  ResponseToken,
  ResponseType,
} from '~/api/types';
import { cacheService } from '~/api/cache';
import { logger } from '~/api/ws/logger';
import { useStreamMessageStore } from '~/store';

export const createTokenId = (id: string) => {
  const tokenPostfix = 'token';
  return `${id}-${tokenPostfix}`;
};

const processStreamResponse = (response: ResponseStream) => {
  const { message: messagePart, extra } = response;
  useStreamMessageStore.getState().startStream();
  useStreamMessageStore.getState().appendMessage(messagePart);

  const isStreamEnd = messagePart === '';
  const statement = useStreamMessageStore.getState().message;

  if (isStreamEnd && statement.length > 0) {
    useStreamMessageStore.getState().stopStream();
    useStreamMessageStore.getState().resetMessage();
    const { id: statementId } = response;

    statuses.get(extra)({ statement, id: statementId });

    createPendingData(createTokenId(statementId));
  }
};

// const processStatementResponse = (response: ResponseStatement) => {
//   const { statement, extra, id, error } = response;
//   statuses.get(extra)({ statement, id, error });
//
//   const promise = new Promise((resolve) => {
//     statuses.set(id, resolve);
//   });
//
//   chatData.set(id, promise);
// };

/*
  → send human input
  * create waiting statement (extra)
  ← statement
  * create waiting for assertion token (statementId)
  ← token for assertion
  * click assertion icon
  → send token for assertion
  * create waiting for assertion (statementId)
  ← assertion
  * create waiting for evidence token (assertionId)
  ← token for one evidence
  * click evidence icon
  → send token for evidence
  * create waiting for evidence token
  ← evidence
*/

const processTaskToken = (response: ResponseToken) => {
  const { id, chat_id } = response;
  statuses.get(createTokenId(id))(response);
  cacheService.setData(chat_id, createTokenId(id), response);
};

const processAssertionResponse = (response: RequestResponseAssertion) => {
  const { statement_id, chat_id } = response;
  statuses.get(statement_id)(response);

  const error = 'error' in response;
  if (!error) {
    cacheService.setData(chat_id, statement_id, response);

    response.ids.forEach((assertionId: string) => {
      createPendingData(createTokenId(assertionId));
    });
  }
};

const processEvidenceResponse = (response: ResponseEvidence) => {
  const { assertion_id, chat_id, extra } = response;
  const id = extra ? extra : assertion_id; // extra for custom assertion

  statuses.get(id)(response);
  cacheService.setData(chat_id, id, response);
};

export const onmessage = (data: string) => {
  const response = JSON.parse(data) as CommonResponse;
  const { type } = response;

  logger.receivedMessage(`[ws message] [type-${type}]`, data);

  if (type === ResponseType.TASK_TOKEN) processTaskToken(response);
  if (type === ResponseType.STREAM) processStreamResponse(response);
  // if (type === ResponseType.STATEMENT) processStatementResponse(response);
  if (type === ResponseType.ASSERTIONS) processAssertionResponse(response);
  if (type === ResponseType.EVIDENCE) processEvidenceResponse(response);
};
