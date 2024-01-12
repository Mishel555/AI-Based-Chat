import { ChatWidget } from '~/modules/Chat';
import { SidebarWidget } from '~/modules/Sidebar';
import {
  useValidationSidebarStore,
  ValidationSidebarWidget,
} from '~/modules/ValidationSidebar/ValidationSidebar';
import styles from './style.module.css';

const ChatPage = () => {
  const visible = useValidationSidebarStore((state) => state.visible);

  return (
    <div className={styles.root}>
      <div className={styles.root__wrapper}>
        <SidebarWidget />
        <ChatWidget />
      </div>
      <ValidationSidebarWidget visible={visible} />
    </div>
  );
};

export default ChatPage;
