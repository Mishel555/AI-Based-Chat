import classNames from 'classnames';
import styles from '../ChatMessage/ChatMessage.module.css';
import { ReactNode } from 'react';

type PropsType = {
  children: ReactNode;
  ai: boolean;
};

const MessageActionList = ({ children, ai }: PropsType) => (
  <div className={classNames(styles.msg_actions, !ai && styles.user_msg_actions)}>{children}</div>
);

export default MessageActionList;
