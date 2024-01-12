import styles from './style.module.css';
import { BsPlusLg } from 'react-icons/all';
import { useChatStore } from '~/store';

const NewChat = () => {
  const setCurrentChat = useChatStore((state) => state.changeCurrentChat);

  const clicked = () => {
    setCurrentChat(null);
  };

  return (
    <a onClick={clicked} className={styles.root}>
      <BsPlusLg />
      <span>New chat</span>
    </a>
  );
};

export default NewChat;
