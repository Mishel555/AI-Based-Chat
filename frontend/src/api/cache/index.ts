import { CommonResponse, ResponseType } from '~/api/types';
import { chatData } from '~/api/ws/WsService';

type ApiResponses = CommonResponse;

function CacheService() {
  const restoreFromCache = (chatIds: string[]) => {
    chatIds.forEach((chatId) => {
      const dataString = localStorage.getItem(chatId);
      if (!dataString) {
        localStorage.removeItem(chatId);
        return;
      }
      const chatCachedData = JSON.parse(dataString) as Record<string, ApiResponses>;

      Object.keys(chatCachedData).forEach((id) => chatData.set(id, chatCachedData[id]));
    });
  };

  const updateData = (chatId: string, id: string, prevStateString: string, data: ApiResponses) => {
    const prevState = JSON.parse(prevStateString) as Record<string, ApiResponses>;
    prevState[id] = data;
    localStorage.setItem(chatId, JSON.stringify(prevState));
  };

  const setNewData = (chatId: string, id: string, data: ApiResponses) => {
    const dataForCache = { [id]: data };
    localStorage.setItem(chatId, JSON.stringify(dataForCache));
  };

  const setData = (chatId: string, id: string, data: ApiResponses) => {
    const prevState = localStorage.getItem(chatId);
    if (prevState !== null) updateData(chatId, id, prevState, data);
    else setNewData(chatId, id, data);
  };

  const deleteData = (chatId: string) => {
    localStorage.removeItem(chatId);
  };

  const deleteAfterUpdate = (chatId: string, allMessageId: string[]) => {
    const dataString = localStorage.getItem(chatId);
    if (dataString) {
      const chatCachedData = JSON.parse(dataString) as Record<string, ApiResponses>;
      const newChatData = Object.keys(chatCachedData).reduce((acc, key) => {
        if (allMessageId.includes(key)) {
          acc[key] = chatCachedData[key];
        }
        return acc;
      }, {} as Record<string, ApiResponses>);
      localStorage.setItem(chatId, JSON.stringify(newChatData));
    }
  };

  const deleteItem = (chatId: string, id: string) => {
    const dataString = localStorage.getItem(chatId);
    if (dataString) {
      const preState = JSON.parse(dataString);
      delete preState[id];
      localStorage.setItem(chatId, JSON.stringify(preState));
    }
  };

  const addAssertion = (
    chatId: string,
    id: string,
    newAssertion: { assertion: string; id: string }
  ) => {
    const dataString = localStorage.getItem(chatId);
    if (dataString) {
      const preState = JSON.parse(dataString) as Record<string, ApiResponses>;
      const response = preState[id];
      if (response.type === ResponseType.ASSERTIONS && !('error' in response)) {
        response.ids.push(newAssertion.id);
        response.assertions.push(newAssertion.assertion);
      }
      localStorage.setItem(chatId, JSON.stringify(preState));
    }
  };

  return { setData, deleteData, deleteAfterUpdate, deleteItem, restoreFromCache, addAssertion };
}

export const cacheService = CacheService();
