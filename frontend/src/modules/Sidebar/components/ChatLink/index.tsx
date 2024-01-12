import { useEffect, useRef, useState } from "react";
import { TopicType } from "~/types";
import { useChatStore } from "~/store";
import classNames from "classnames";
import ChatLinkView from "./ChatLinkView";
import ChatLinkEdit from "./ChatLinkEdit";
import ChatLinkDelete from "./ChatLinkDelete";
import styles from "./style.module.css";

type PropsType = {
  chatLink: TopicType;
};

enum Statuses {
  VIEW,
  EDIT,
  DELETE,
}

const ChatLink = ({ chatLink }: PropsType) => {
  const deleteTopic = useChatStore((state) => state.deleteTopic);
  const isActive = useChatStore((state) => state.isChatActive(chatLink.id));
  const changeCurrentChat = useChatStore((state) => state.changeCurrentChat);
  const updateTopicTitle = useChatStore((state) => state.updateTopicTitle);

  const [status, setStatus] = useState(Statuses.VIEW);

  const isView = status === Statuses.VIEW;
  const isEdit = status === Statuses.EDIT;
  const isDelete = status === Statuses.DELETE;

  const childRef = useRef(null);

  const editConfirmHandler = (id: string, newTitle: string) => {
    updateTopicTitle(id, newTitle);
    setStatus(Statuses.VIEW);
  };

  const deleteConfirmHandler = (id: string) => {
    deleteTopic(id);
    setStatus(Statuses.VIEW);
    changeCurrentChat("3");
  };

  useEffect(() => {
    setStatus(Statuses.VIEW);
  }, [isActive]);

  return (
    <a
      onClick={() => changeCurrentChat(chatLink.id)}
      className={classNames(styles.chat__link, isActive && styles.active)}
    >
      {isView && (
        <ChatLinkView
          chatLink={chatLink}
          isActive={isActive}
          onDelete={() => setStatus(Statuses.DELETE)}
          onEdit={() => setStatus(Statuses.EDIT)}
        />
      )}
      {isEdit && (
        <ChatLinkEdit
          chatLink={chatLink}
          isActive={isActive}
          inputRef={childRef}
          onConfirm={editConfirmHandler}
          onCancel={() => setStatus(Statuses.VIEW)}
        />
      )}

      {isDelete && (
        <ChatLinkDelete
          chatLink={chatLink}
          isActive={isActive}
          onConfirm={deleteConfirmHandler}
          onCancel={() => setStatus(Statuses.VIEW)}
        />
      )}
    </a>
  );
};

export default ChatLink;
