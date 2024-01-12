import { TopicType } from '~/types';
import ChatLink from '../ChatLink';
import styles from './style.module.css';

type PropsType = {
  name: string;
  chatLinksList: TopicType[]
}

const ChatPeriod = ({ name, chatLinksList }: PropsType) => (
  <div className={styles.root}>
    <div className={styles.period}>{name}</div>
    <ol>
      {chatLinksList.map(chatLink => (
        <li key={chatLink.id}>
          <ChatLink chatLink={chatLink} />
        </li>
      ))}
    </ol>
  </div>
);


export default ChatPeriod;
