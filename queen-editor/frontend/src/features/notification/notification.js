// The browser's own notification, for a tab left in the background (madde 498, 509). Whatever the
// browser cannot or will not do is let go in silence: nothing else on screen stands in for it.

const TITLE = "Queen Editor";
// One tag for every one of them: a notification shown again replaces the last instead of stacking,
// and `renotify` makes it ring all the same.
const TAG = "queen-editor-queue";

const supported = () => typeof Notification !== "undefined";

// Asked from a press: the browser asks the user only inside a click. Once answered, either way, the
// browser keeps the answer and this asks nothing more.
export function askPermission() {
  if (!supported() || Notification.permission !== "default") return;
  // Older browsers answer through a callback and return nothing; nobody waits for it here.
  Promise.resolve(Notification.requestPermission()).catch(() => {});
}

export function notify(body) {
  if (!supported() || Notification.permission !== "granted") return;
  try {
    const shown = new Notification(TITLE, { body, tag: TAG, renotify: true });
    shown.onclick = () => {
      window.focus();
      shown.close();
    };
  } catch {
    // Chrome on Android allows a notification only through a service worker.
  }
}
