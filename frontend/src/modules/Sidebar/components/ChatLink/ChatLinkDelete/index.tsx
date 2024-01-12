import { TopicType } from '~/types';
import { CommonPropsType, ConfirmChatOperations } from '../common';
import { BsTrash } from 'react-icons/bs';
import styles from '../style.module.css';

type PropsType = CommonPropsType & {
  chatLink: TopicType;
  isActive: boolean;
};

const ChatLinkDelete = ({ chatLink, isActive, onCancel, onConfirm }: PropsType) => {
  const handlerConfirm = (e: Event) => {
    e.stopPropagation();
    onConfirm(chatLink.id);
  };

  return (
    <>
      <BsTrash size={16} />

      <div className={styles.title}>
        Delete "{chatLink.title}"?
        <div className={styles.shadow}></div>
      </div>

      {isActive && (
        <ConfirmChatOperations onConfirm={handlerConfirm} onCancel={() => onCancel()} />
      )}
    </>
  );
};

export default ChatLinkDelete;
