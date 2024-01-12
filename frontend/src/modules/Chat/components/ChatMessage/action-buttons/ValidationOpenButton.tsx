import React, { useEffect, useState } from 'react';
import { ResponseToken } from '~/api/types';
import chatStore from '~/store/ChatStore';
import api from '~/api';
import { createTokenId } from '~/api/ws/handlers/onmessage';
import classNames from 'classnames';
import styles from '~/modules/Chat/components/ChatMessage/ChatMessage.module.css';
import { FaLightbulb, FaSpinner, MdDisabledByDefault } from 'react-icons/all';

type PropsType = {
  statementId: string;
  chatId: string;
  action: () => void;
  iconProps?: {};
};

export const ValidationOpenButton = ({ action, statementId, chatId, iconProps }: PropsType) => {
  const [state, setState] = useState<'disabled' | 'loading' | 'ok'>('disabled');
  const [tokenResponse, setTokenResponse] = useState<ResponseToken | null>(null);

  let onClick = async () => {
    if (tokenResponse) {
      setState('loading');
      const response = await chatStore
        .getState()
        .sendAssertionToken(chatId, statementId, tokenResponse.task_token);
      if (response && 'error' in response) {
        setState('disabled');
      } else {
        setState('ok');
      }
      setTokenResponse(null);
    } else {
      action();
    }
  };

  useEffect(() => {
    const fetchAssertion = async () => {
      setState('loading');
      const response = await api.chat.getAssertions(statementId);

      // @ts-ignore
      const isDataInCache = response?.assertions?.length > 0;
      if (isDataInCache) {
        setState('ok');
      } else {
        const response = await api.chat.getToken(createTokenId(statementId));
        if (!response) {
          setState('disabled');
          return;
        } else {
          setTokenResponse(response);
          setState('ok');
        }
      }
    };

    if (statementId) fetchAssertion();
  }, [statementId]);

  return (
    <button
      disabled={state === 'disabled' || state === 'loading'}
      type="button"
      onClick={onClick}
      className={classNames(styles.root__button, state === 'loading' && styles.button_loading)}
    >
      {state !== 'disabled' && state !== 'loading' && <FaLightbulb {...iconProps} />}
      {state === 'loading' && <FaSpinner />}
      {state === 'disabled' && <MdDisabledByDefault />}
    </button>
  );
};
