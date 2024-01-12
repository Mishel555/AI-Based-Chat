import { Tooltip } from 'react-tooltip';
import { useInputStore } from '../../../store';
import { ACTION_VALUES, ACTIONS } from '../../../constants';
import AssertionList from '../AssertionsList';
import styles from './style.module.css';
import { ValidationOpenButton } from '~/modules/Chat/components/ChatMessage/ActionComponents';
import { useChatStore } from '~/store';
import { Fragment } from 'react';

const InputMenu = () => {
  const chatId = useChatStore((state) => state.currentChat);
  const lastMessage = useChatStore((state) => state.lastMessage());
  const { value, change } = useInputStore();

  return (
    <Fragment>
      {chatId && lastMessage?.id && (
        <div id="tooltipId" className={styles.root}>
          <ValidationOpenButton
            iconProps={{
              id: 'tooltipId',
              color: ACTION_VALUES.includes(value) ? '#FFFD6A' : '',
              className: styles.root__button,
              size: '16',
            }}
            statementId={lastMessage.id}
            chatId={chatId}
            action={() => change(ACTIONS.EXPLORE)}
          />
          <Tooltip anchorSelect="#tooltipId" clickable isOpen={value === ACTIONS.EXPLORE}>
            <AssertionList statementId={lastMessage.id} />
          </Tooltip>
        </div>
      )}
    </Fragment>
  );
};

export default InputMenu;
