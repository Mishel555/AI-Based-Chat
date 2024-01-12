import { HiOutlineArrowDown } from 'react-icons/hi';
import classNames from 'classnames';
import styles from './style.module.css';
import { RefObject, useEffect, useState } from 'react';

type PropsType = {
  onClick: () => void;
  parentRef: RefObject<HTMLDivElement>;
};

const ChatScrollDown = (props: PropsType) => {
  const [showScroll, setShowScroll] = useState<boolean>(false);

  useEffect(() => {
    // @ts-ignore
    const handleScroll = (e) => {
      const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;

      let newState = scrollHeight > clientHeight && scrollHeight - clientHeight - scrollTop > 5;

      if (newState) {
        setShowScroll(true);
      } else {
        setShowScroll(false);
      }
    };

    const element = props.parentRef.current;
    if (element) {
      element.addEventListener('scroll', handleScroll);

      return () => {
        element.removeEventListener('scroll', handleScroll);
      };
    }
  }, [props.parentRef]);

  return (
    <button
      onClick={props.onClick}
      className={classNames(styles.root, showScroll && styles.visible)}
    >
      <HiOutlineArrowDown />
    </button>
  );
};

export default ChatScrollDown;
