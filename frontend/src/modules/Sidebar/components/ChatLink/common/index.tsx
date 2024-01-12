import styles from '../style.module.css';
import { BsCheck2 } from 'react-icons/bs';
import { RxCross2 } from 'react-icons/rx';

export type CommonPropsType = {
  onConfirm: Function;
  onCancel: Function;
  size?: number;
};

export const ConfirmChatOperations = ({ onConfirm, onCancel, size = 16 }: CommonPropsType) => (
  <div className={styles.operation_buttons}>
    <button onClick={(e) => onConfirm(e)}>
      <BsCheck2 size={size} />
    </button>
    <button onClick={(e) => onCancel(e)}>
      <RxCross2 size={size} />
    </button>
  </div>
);
