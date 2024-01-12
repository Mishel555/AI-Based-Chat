import styles from '~/modules/Chat/components/ChatMessage/ChatMessage.module.css';
import { BsBook } from 'react-icons/all';
import React from 'react';

export const BookUrl = (props: { url: string }) => {
  return (
    <a href={props.url} target="_blank" className={styles.url_book}>
      <BsBook size={14} />
    </a>
  );
};
