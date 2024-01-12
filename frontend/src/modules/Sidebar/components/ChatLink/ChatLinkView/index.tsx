import { BsChatLeft, BsTrash } from 'react-icons/bs';
import { AiOutlineEdit } from 'react-icons/ai';
import { TopicType } from '~/types';
import styles from '../style.module.css';

type ViewPropsType = {
  onEdit: Function;
  onDelete: Function;
};

const ViewChatOperations = ({ onEdit, onDelete }: ViewPropsType) => (
  <div className={styles.operation_buttons}>
    <button onClick={() => onEdit()}>
      <AiOutlineEdit size={16} />
    </button>
    <button onClick={() => onDelete()}>
      <BsTrash />
    </button>
  </div>
);

type PropsType = {
  chatLink: TopicType;
  isActive: boolean;
  onDelete: Function;
  onEdit: Function;
};

const ChatLinkView = ({ chatLink, onDelete, onEdit, isActive }: PropsType) => {
  return (
    <>
      <BsChatLeft />

      <div className={styles.title}>
        {chatLink.title}
        <div className={styles.shadow}></div>
      </div>

      {isActive && <ViewChatOperations onDelete={() => onDelete()} onEdit={() => onEdit()} />}
    </>
  );
};

export default ChatLinkView;
