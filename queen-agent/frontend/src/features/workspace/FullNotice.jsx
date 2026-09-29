// A full chat takes no more messages, and says so in the box's place the moment its record does
// (Madde 352; design items 140 and 182). The two ways on are both ghost: nothing is destroyed,
// somebody is being asked.
export default function FullNotice({ gauge, onNewChat, onContinue }) {
  return (
    <div className="full">
      <div className="full__text">
        <p className="full__line">This chat is full.</p>
        <p className="full__detail">
          Continue here sends only the latest messages to the model; the older ones stay on screen.
        </p>
      </div>
      <div className="full__actions">
        <div className="composer__gauge">{gauge}</div>
        <button type="button" className="ghost full__new" onClick={onNewChat}>
          New chat
        </button>
        <button type="button" className="ghost full__continue" onClick={onContinue}>
          Continue here
        </button>
      </div>
    </div>
  );
}
