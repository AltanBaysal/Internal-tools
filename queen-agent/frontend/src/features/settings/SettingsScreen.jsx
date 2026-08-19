import { useEffect, useState } from "react";

// The app's own screen rather than a project's: one field today, and the place the model default
// will go when it stops being a server setting. The design draws no settings screen, so this is
// built out of the app's own parts -- the screen column, the mono label, the primary button.
export default function SettingsScreen({ apiKey = "", onSave }) {
  const [draft, setDraft] = useState(apiKey);
  const [saved, setSaved] = useState(false);
  const [failed, setFailed] = useState(null);

  // The screen is drawn before the answer arrives, so the box follows the stored key until the
  // moment someone types in it.
  useEffect(() => {
    setDraft(apiKey);
  }, [apiKey]);

  const save = async () => {
    setFailed(null);
    try {
      await onSave?.(draft);
      setSaved(true);
    } catch (failure) {
      setFailed(failure.message);
    }
  };

  return (
    <div className="screen">
      <div className="screen__column">
        <div className="screen__title-row">
          <h1 className="screen__title">Settings</h1>
        </div>

        <label className="field">
          <span className="field__label">XAI API KEY</span>
          {/* Plain text, the user's decision: their own machine, their own key, and a masked one
              they could not read back would answer less than the key itself. */}
          <input
            type="text"
            className="field__input"
            value={draft}
            spellCheck={false}
            autoComplete="off"
            onChange={(event) => {
              setDraft(event.target.value);
              // Saved is a moment, not a state: the box no longer holds what was saved.
              setSaved(false);
            }}
          />
        </label>

        <div className="field__foot">
          <button type="button" className="composer__send" onClick={save}>
            Save
          </button>
          {saved ? <span className="field__saved">Saved.</span> : null}
        </div>

        {failed ? <p className="list-error">{failed}</p> : null}
      </div>
    </div>
  );
}
