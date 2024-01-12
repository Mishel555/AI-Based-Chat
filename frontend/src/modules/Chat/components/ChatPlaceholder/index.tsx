import styles from './style.module.css';
import { useInputStore } from '~/modules/Chat';
import { RotatingLines } from 'react-loader-spinner';

const ChatPlaceholder = () => {
  const isCanWrite = useInputStore((state) => state.isCanWrite);

  return (
    <div className={styles.root}>
      {isCanWrite ? (
        <h1>Chat FSP</h1>
      ) : (
        <RotatingLines strokeColor="#acacbe" strokeWidth="2" width="20" />
      )}
    </div>
  );
};

export default ChatPlaceholder;
