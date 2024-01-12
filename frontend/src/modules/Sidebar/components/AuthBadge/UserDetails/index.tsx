import { useEffect, useRef, useState } from 'react';
import { SlLogout, BiDotsHorizontalRounded, FiSettings } from 'react-icons/all';
import { UserType } from '~/types';
import { useAuthStore } from '~/store';
import { Avatar } from '~/ui';
import { ContextActionType } from '../../../types';
import ContextMenu from '../ContextMenu';
import styles from './style.module.css';

type PropsType = {
  data: UserType;
}

const UserDetails = ({ data }: PropsType) => {
  const { avatar, email } = data;

  const logOut = useAuthStore(state => state.logout);

  const rootRef = useRef<HTMLDivElement | null>(null);

  const [open, setOpen] = useState<boolean>(false);

  const toggle = () => setOpen(prevState => !prevState);

  const contextActions: ContextActionType[] = [
    { label: 'Log out', icon: <SlLogout />, onClick: logOut },
    { label: 'Settings', icon: <FiSettings />, onClick: () => {} },
  ];

  useEffect(() => {
    const listener = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Element)) {
        setOpen(false);
      }
    };

    document.addEventListener('click', listener);

    return () => document.removeEventListener('click', listener);
  }, []);

  return (
    <div ref={rootRef} className={styles.root}>
      <ContextMenu actions={contextActions} visible={open} />
      <button onClick={toggle} className={styles.root__button}>
        <Avatar src={avatar} size={20} />
        <span className={styles.user_email}>{email}</span>
        <BiDotsHorizontalRounded className={styles.dots_icon} size={16} />
      </button>
    </div>
  );
};

export default UserDetails;
