import { useEffect, useState } from "react";

import { readChats } from "./useChatLists.js";

// /p/<id> has no screen of its own (the design's item 170): a project opens on its latest chat, or
// on its draft while it has none. Which chat is the latest is the server's order; this only takes
// the first. The address it stands on is written over, so the back button never lands here to be
// thrown forward again.
export default function OpenProject({ projectId, navigate }) {
  const [error, setError] = useState(null);

  useEffect(() => {
    // An answer about a project the user has already left moves nobody.
    let left = false;
    readChats(projectId).then(
      (chats) => {
        if (!left) navigate(`/p/${projectId}/c/${chats[0]?.id ?? "new"}`, { replace: true });
      },
      (failure) => {
        if (!left) setError(failure.message);
      },
    );
    return () => {
      left = true;
    };
  }, [projectId, navigate]);

  // Landing in the draft instead would say the project has no chats, which nobody said.
  return error ? (
    <div className="screen">
      <div className="screen__column">
        <p className="list-error">{error}</p>
      </div>
    </div>
  ) : null;
}
