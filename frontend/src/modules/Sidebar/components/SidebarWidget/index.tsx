import { Fragment } from 'react';
import { useAuthStore } from '~/store';
import NewChat from '../NewChat';
import ChatLinkList from '../ChatLinkList';
import AuthBadge from '../AuthBadge';
import styles from './style.module.css';

const SidebarWidget = () => {
  const user = useAuthStore(state => state.user);

  return (
    <div className={styles.root}>
      <nav className={styles.root__navigation}>
        {user && (
          <Fragment>
            <NewChat />
            <ChatLinkList />
          </Fragment>
        )}
        <AuthBadge />
      </nav>
    </div>
  );
};

export default SidebarWidget;
