import { create } from 'zustand';
import { createChatSlice, IChatSlice } from './chatSlice';
import { createTopicSlice, ITopicSlice } from './topicSlice';
import { createSendMessageSlice, ISendMessageSlice } from './sendMessageSlice';

const useChatStore = create<ITopicSlice & IChatSlice & ISendMessageSlice>((...a) => ({
  ...createChatSlice(...a),
  ...createTopicSlice(...a),
  ...createSendMessageSlice(...a),
}));

export default useChatStore;
