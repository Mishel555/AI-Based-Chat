import { AiOutlineCloseCircle } from 'react-icons/ai';
import { HiOutlineLightBulb } from 'react-icons/hi';
import styles from './style.module.css';

type PropsType = {
  message?: string;
  onClose: () => void;
};

const ValidationSidebarHeader = ({ message, onClose }: PropsType) => (
  <div className={styles.root}>
    <div className={styles.root__wrapper}>
      <HiOutlineLightBulb size={24} />
      <span className={styles.root__title}>Exploration Copilot</span>
      <button onClick={onClose} className={styles.close_button}>
        <AiOutlineCloseCircle size={20} />
      </button>
    </div>
    <p className={styles.root__preview}>Message: {message}</p>
  </div>
);

export default ValidationSidebarHeader;
