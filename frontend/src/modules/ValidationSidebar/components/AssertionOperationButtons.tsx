import { MouseEvent, useEffect, useState } from 'react';
import { HiOutlineBookOpen } from 'react-icons/hi';
import { TbArrowAutofitLeft } from 'react-icons/tb';
import { AiOutlineEdit } from 'react-icons/ai';
import styles from './ValidationAssertion/style.module.css';

enum CheckStatuses {
  INITIAL,
  IN_PROGRESS,
  SUCCESS,
  FAILED,
}

const colorsMap = {
  [CheckStatuses.INITIAL]: '',
  [CheckStatuses.IN_PROGRESS]: 'in_progress_check',
  [CheckStatuses.SUCCESS]: 'success_check',
  [CheckStatuses.FAILED]: 'failed_check',
};

type AssertionOperationPropsType = {
  opened: boolean;
  onSend: () => void;
  onCheck: () => void;
  onEdit: () => void;
};

const AssertionOperationButtons = ({
  opened,
  onSend,
  onCheck,
  onEdit,
}: AssertionOperationPropsType) => {
  const [checkStatus, setCheckStatus] = useState(CheckStatuses.INITIAL);

  const checkIconColor = colorsMap[checkStatus];

  const onSendClick = (e: MouseEvent) => {
    e.stopPropagation();

    onSend();
  };

  useEffect(() => {
    setCheckStatus(() => (opened ? CheckStatuses.IN_PROGRESS : CheckStatuses.INITIAL));
  }, [opened]);

  return (
    <div className={styles.assertion_buttons}>
      {checkStatus !== CheckStatuses.INITIAL ? (
        <button onClick={onSendClick}>
          <TbArrowAutofitLeft size={24} />
        </button>
      ) : (
        <button onClick={onEdit} className={`${styles.check_button}`}>
          <AiOutlineEdit size={24} className={styles[checkIconColor]} />
        </button>
      )}

      <button onClick={onCheck} className={`${styles.check_button}`}>
        <HiOutlineBookOpen size={24} className={styles[checkIconColor]} />
      </button>
    </div>
  );
};

export default AssertionOperationButtons;
