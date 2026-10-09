// No answer came: a message the server refused, a turn whose stream broke, or an answer the model
// failed on five times (design items 193, 216 and 221). One card for all of them, with the words the
// server or the engine said under it. Without `onRetry` it keeps no button: a failed answer the chat
// has moved on from is still a record of what happened, and nothing more.
export default function FailureCard({ words, onRetry = null }) {
  return (
    <div className="failure">
      <div className="failure__body">
        {/* The design also said "The connection dropped." That is a guessed cause -- a bad key and a
            wrong model name raise this same card -- so the card states what happened and the
            server's own words sit underneath. */}
        <span className="failure__line">Couldn&apos;t get a response.</span>
        {/* The server's own words and nothing beside them. There used to be a way out offered here
            -- a screen for typing a missing key -- and with the key coming from the environment
            there is no longer anywhere for it to lead. */}
        <span className="failure__detail">{words}</span>
      </div>
      {onRetry ? (
        <button type="button" className="failure__retry" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}
