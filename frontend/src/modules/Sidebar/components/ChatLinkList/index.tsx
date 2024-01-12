import { useEffect, useState } from 'react';
import { TopicType } from '~/types';
import { useChatStore } from '~/store';
import ChatPeriod from '../ChatPeriod';
import ChatLinkLoader from '../ChatLinkLoader';
import styles from './style.module.css';

enum Periods {
  TODAY = 'Today',
  YESTERDAY = 'Yesterday',
  PREV_7_DAYS = 'Previous 7 Days',
}

export type ChatPeriodType = {
  name: Periods;
  chatLinkList: TopicType[];
};

const getYesterdayDate = (): Date => {
  const date = new Date();
  date.setDate(date.getDate() - 1);

  return date;
};

const separateToPeriods = (chatLinkList: TopicType[]): ChatPeriodType[] => {
  const periodsMap: Map<Periods, TopicType[]> = new Map([
    [Periods.TODAY, []],
    [Periods.YESTERDAY, []],
    [Periods.PREV_7_DAYS, []],
  ]);

  const today = new Date().toDateString();
  const yesterday = getYesterdayDate().toDateString();

  chatLinkList.forEach((chatLink) => {
    const dateToCheck = new Date(chatLink.updatedDate ?? chatLink.createdDate).toDateString();

    let chatLinkPeriod = Periods.PREV_7_DAYS;
    if (dateToCheck === today) chatLinkPeriod = Periods.TODAY;
    if (dateToCheck === yesterday) chatLinkPeriod = Periods.YESTERDAY;

    const perValue = periodsMap.get(chatLinkPeriod) || [];
    periodsMap.set(chatLinkPeriod, [...perValue, chatLink]);
  });

  return Array.from(periodsMap.entries())
    .map(([period, chatLinkList]) => {
      return {
        name: period,
        chatLinkList,
      };
    })
    .filter((chatPeriod) => chatPeriod.chatLinkList.length > 0);
};

const ChatLinkList = () => {
  const topics = useChatStore((state) => state.topics);
  const periods: ChatPeriodType[] = topics ? separateToPeriods(topics) : [];

  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  // implemented temporary loader...
  useEffect(() => {
    const timeout = setTimeout(() => setIsLoaded(true), 100);

    return () => {
      clearTimeout(timeout);
    };
  }, []);

  return (
    <div className={styles.root}>
      {!isLoaded && <ChatLinkLoader />}
      {isLoaded &&
        periods.map((period) => (
          <ChatPeriod key={period.name} name={period.name} chatLinksList={period.chatLinkList} />
        ))}
    </div>
  );
};

export default ChatLinkList;
