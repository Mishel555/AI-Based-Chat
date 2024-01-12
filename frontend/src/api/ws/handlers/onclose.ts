import { MAX_ATTEMPTS_TO_RECONNECT } from '../constants';
import { onCloseLogger } from '../logger';
import { toast } from 'react-toastify';
import { wsService } from '~/api/ws/WsService';

const reconnectBeforeClose = (maxReconnectCount: number, delay: number) => {
  let counter = maxReconnectCount;

  return function (logger: onCloseLogger) {
    if (counter === 0) {
      logger.failedReconnect(MAX_ATTEMPTS_TO_RECONNECT);

      toast.error(`Ws connection failed after ${MAX_ATTEMPTS_TO_RECONNECT} attempts`, {
        closeButton: false,
      });
    } else {
      setTimeout(function () {
        wsService.reconnect();
        counter--;
        logger.reconnectAttempt();
      }, delay);

      logger.connectionDied();
    }
  };
};

const reconnect = reconnectBeforeClose(MAX_ATTEMPTS_TO_RECONNECT, 3000);

export const onclose = (logger: onCloseLogger) => () => {
  reconnect(logger);
};
