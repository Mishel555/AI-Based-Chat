import classNames from 'classnames';
import { useChatStore } from '~/store';
import { useValidationSidebarStore } from '../../store';
import ValidationSidebarHeader from '../ValidationSidebarHeader';
import ValidationSidebarInput from '../ValidationSidebarInput';
import ValidationSidebarAssertionList from '../ValidationSidebarAssertionList';
import styles from './style.module.css';

type PropsType = {
  visible: boolean;
};

const ValidationSidebarWidget = ({ visible }: PropsType) => {
  const closeSidebar = useValidationSidebarStore((state) => state.close);
  const selectedStatementId = useValidationSidebarStore((state) => state.selectedStatementId);

  const selectedStatement = useChatStore((state) => {
    const currentTopic = state.topics.find(
      (topic) => topic.messages.findIndex((message) => message.id === selectedStatementId) > -1
    );

    return currentTopic?.messages.find((message) => message.id === selectedStatementId);
  });

  const opened = visible && !!selectedStatement;

  return (
    <div className={classNames(styles.root, opened && styles.root__opened)}>
      <ValidationSidebarHeader message={selectedStatement?.message} onClose={closeSidebar} />
      <ValidationSidebarAssertionList statementId={selectedStatement?.id} />
      {selectedStatement?.id && <ValidationSidebarInput statementId={selectedStatement.id} />}
    </div>
  );
};

export default ValidationSidebarWidget;
