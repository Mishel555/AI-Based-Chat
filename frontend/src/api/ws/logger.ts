export interface onCloseLogger {
  cleanClose: () => void;
  failedReconnect: (count: number) => void;
  reconnectAttempt: () => void;
  connectionDied: () => void;
}

export interface onErrorLogger {
  error: (error: Event) => void;
}

export interface onOpenLogger {
  openConnection: () => void;
}

export interface onMessageLogger {
  sendMessage: (data: string) => void;
  receivedMessage: (message: string, data: string) => void;
}

export const logger: onOpenLogger & onCloseLogger & onErrorLogger & onMessageLogger = {
  openConnection() {
    console.log('[open] Connection opened');
  },
  receivedMessage(message, data) {
    console.log(message, data);
  },
  sendMessage(data: string) {
    console.log(`[sent-message] ${data}`);
  },
  cleanClose() {
    console.log(`[close] Connection closed cleanly`);
  },
  error(error: Event) {
    console.log(`[error]`, error);
  },
  failedReconnect(count: number) {
    console.log(`[reconnect] reconnection failed after ${count} attempts`);
  },
  reconnectAttempt() {
    console.log('[reconnect] attempt');
  },
  connectionDied() {
    console.log('[close] Connection died. Reconnecting...');
  },
};
