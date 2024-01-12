import { FormEvent, KeyboardEvent } from 'react';
import { IoSend } from 'react-icons/all';
import { ThreeDots } from 'react-loader-spinner';
import api from '~/api';
import { useChatStore } from '~/store';
import { ACTION_VALUES } from '../../../constants';
import { useInputStore } from '../../../store';
import InputMenu from '../InputMenu';
import FormTextarea from './FormTextarea';
import styles from './style.module.css';

const FormInput = () => {
  const sendHumanMessage = useChatStore((state) => state.sendHumanMessage);
  const sendActionMessage = useChatStore((state) => state.sendActionMessage);
  const isCanWrite = useInputStore((state) => state.isCanWrite);
  const setCanWrite = useInputStore((state) => state.setCanWrite);

  const addTopic = useChatStore((state) => state.addTopic);
  const currentChat = useChatStore((state) => state.currentChat);
  const setCurrentChat = useChatStore((state) => state.changeCurrentChat);

  const value = useInputStore((state) => state.value);
  const change = useInputStore((state) => state.change);

  const createNewChat = async () => {
    const { id: newTopicId } = await api.chat.createNewChat({
      ts: new Date().toISOString(),
    });

    addTopic(newTopicId, value);
    setCurrentChat(newTopicId);
    return newTopicId;
  };

  const sendMessage = async () => {
    if (value.length === 0) return;
    if (!isCanWrite) return;

    const isNewChatInput = currentChat === null;
    const isValidationActionInput = value.includes(ACTION_VALUES[0]);

    setCanWrite(false);
    const chatId = isNewChatInput ? await createNewChat() : currentChat;
    if (isValidationActionInput) sendActionMessage(chatId, value);
    else sendHumanMessage(chatId, value);
  };

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    sendMessage();
  };

  const onPressEnter = (e: KeyboardEvent) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <form onSubmit={onSubmit} className={styles.root}>
      <InputMenu />
      <FormTextarea
        value={value}
        onChange={(e) => change(e.target.value)}
        onPressEnter={onPressEnter}
        placeholder={'Send a message'}
      />
      {!isCanWrite ? (
        <ThreeDots width={20} height={24} color="#acacbe" />
      ) : (
        <button disabled={value.length === 0} className={styles.root__send}>
          <IoSend size={16} />
        </button>
      )}
    </form>
  );
};

export default FormInput;
