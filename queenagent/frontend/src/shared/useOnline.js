import { useEffect, useState } from "react";

// Read in one place. What the network is actually needed for is the engine: QueenAgent's own server
// is on this machine, so a message still reaches the disk while the connection is gone.
export function useOnline() {
  const [online, setOnline] = useState(() => navigator.onLine !== false);

  useEffect(() => {
    const went = () => setOnline(navigator.onLine !== false);
    window.addEventListener("online", went);
    window.addEventListener("offline", went);
    return () => {
      window.removeEventListener("online", went);
      window.removeEventListener("offline", went);
    };
  }, []);

  return online;
}
