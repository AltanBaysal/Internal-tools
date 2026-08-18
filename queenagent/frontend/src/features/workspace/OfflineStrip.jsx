// The sentence is what is actually true here: the server is on this machine, so the message is
// written; the network is what the sending needs, so that is what waits.
export default function OfflineStrip({ online }) {
  if (online) return null;
  return (
    <div className="offline" data-testid="offline">
      {/* A filled dot in the strip's own ink. The design says accent; the same design says the
          accent marks the primary action and nothing else, and being offline is a state. */}
      <span className="offline__dot" />
      You&apos;re offline — messages are saved and will send when you reconnect.
    </div>
  );
}
