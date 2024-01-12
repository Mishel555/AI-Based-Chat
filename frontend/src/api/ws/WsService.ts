import { logger } from './logger';
import { onmessage } from './handlers/onmessage';
import { onopen } from './handlers/onopen';
import { onerror } from './handlers/onerror';
import { onclose } from './handlers/onclose';
import api from '~/api';
import { toast } from 'react-toastify';
import { useAuthStore } from '~/store';

export const chatData = new Map();
export const statuses = new Map();

export const createPendingData = (id: string) => {
  const promise = new Promise((resolve) => {
    statuses.set(id, resolve);
  });
  chatData.set(id, promise);
};

export const getChatData = () => chatData;

const registerHandlers = (ws: WebSocket) => {
  ws.onopen = onopen(logger);
  ws.onerror = onerror(logger);
  ws.onclose = onclose(logger);
  ws.onmessage = ({ data }) => {
    onmessage(data);
  };
};

function WsService(url: string) {
  let ws: WebSocket;
  let urlForReconnect: string;
  let wsSession: string;

  async function connect(session: string) {
    const response = await api.auth.getUser();

    if ('error' in response) {
      toast.error(`Session expired.`, {
        closeButton: false,
      });
      useAuthStore.getState().logout();
      return;
    }
    wsSession = session;
    const urlWithSession = `${url}?session=${session}`;
    ws = new WebSocket(urlWithSession);
    urlForReconnect = urlWithSession;
    registerHandlers(ws);

    return response;
  }

  function reconnect() {
    ws = new WebSocket(urlForReconnect);
    registerHandlers(ws);
  }

  function sendMessage(action: string, body: string) {
    const preparedDataObj = { action, session: wsSession, body };

    ws.send(JSON.stringify(preparedDataObj));
    logger.sendMessage(preparedDataObj.body);
  }

  return {
    sendMessage,
    connect,
    reconnect,
  };
}

export const wsService = WsService(import.meta.env.VITE_WS_URL);
