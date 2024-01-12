import { RotatingLines } from 'react-loader-spinner';
import styles from './style.module.css';

const ChatLinkLoader = () => (
  <div className={styles.root}>
    <RotatingLines strokeColor="#acacbe" strokeWidth="2" width="20" />
  </div>
);

export default ChatLinkLoader;
