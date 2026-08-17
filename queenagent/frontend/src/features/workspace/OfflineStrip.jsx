// The sentence is what is actually true here: the server is on this machine, so the message is
// written; the network is what the engine needs, so the answer is what waits.
export default function OfflineStrip({ online }) {
  if (online) return null;
  return (
    <div className="offline" data-testid="offline">
      You&apos;re offline. Messages are saved; QueenAgent will answer when the connection is back.
    </div>
  );
}
