# QueenAgent: design needs for the v10 round

QueenAgent is a small AI workspace in the browser. Work is organised into projects, each project holds chats and files, and the assistant's answers in a chat can create files in the project. The interface is in English on purpose. This document lists the needs the owner wants the next design round to answer. It states problems and the owner's fixed decisions, not solutions. Anything not stated here as the owner's decision is the designer's call. Where something is open, ask the owner rather than assume: they want to talk the open points through with you. The known ones are listed at the end.

The first need changes how an answer arrives, so the chat screen has to be designed around it. The second and third are for your information: they are built without waiting for the design, and they are here so the next round's drawings match the app. The fourth is built only once your green has come.

---

## 1. The answer's retries, on screen

**Today**
- When the user sends a message, their bubble appears at once. Under it, the answer's place shows three small grey dots that blink in turn.
- Under the dots, a line in small type gives the time the message was sent. Once the turn has started, the line reads `14:32 · round 2/32 · 3.4k tokens ·`, then a small turning spinner and a word that changes every three seconds ("Pondering…", "Brewing…" and so on). A turn can run up to 32 rounds.
- While the assistant works with tools, a box above the dots shows the step in progress, for example `⏺ read_file(aylin.json) ⌄`. Pressed, it lists the steps so far. When the turn is over, it reads `⏺ 3 steps`.
- When the assistant starts writing a file, a dashed card reading "creating file…" appears under the dots.
- As soon as the first words of the answer arrive, the dots give way to the answer, which is written out live as it comes in.
- When the answer ends, the line under it becomes the time and what the answer cost: `14:32 · 3.1k cached · 312 missed`. The cached count is dark green, the missed count red.
- While an answer runs, the send button (`↑` on a filled rust-red square) shows `⏹` instead. Its tooltip reads "Stop".
- Pressing Stop ends the turn. Whatever text had arrived stays, with a thin grey line down its left edge and the word "Stopped" under it in small grey type. An answer stopped before its first word shows only its steps, "Stopped" and the time.
- When the model refuses, its refusal shows as the answer, like any other answer.
- When an answer never comes, or the message could not be sent, a card appears under the conversation, tinted a pale rust. It reads "Couldn't get a response.", with the error's own words under it in small monospaced type, and a "Try again" button on the right. Nothing is asked again unless the user presses it.

**Need.** The owner's words: "Look at the answer, and if it is a refusal, send it again." "When an error comes, let it try again too." "Raise the count to 5 instead of 3, and let it show in QueenAgent."

**Fixed by the owner**
- When the model fails or refuses, QueenAgent asks it again by itself, up to five tries in all. An error and a refusal count toward the same five.
- A refusal no longer shows as the answer.
- The retries show in the chat. Every retry is shown, whichever round of the turn it happens in.
- The answer is no longer written out live. The dots stay until the whole answer has come, and then the whole answer appears at once.
- With no retry, the screen looks as it does today, apart from the answer no longer being written out live.
- Stop ends the turn at once, and QueenAgent does not try again after it. Whatever of the answer had come is dropped: the user never saw it. The turn is marked as stopped. This replaces today's rule that a stopped answer keeps its half text. The owner's words: "Drop it."
- After five failed tries, the chat shows a message as the AI's answer, and the turn ends:
  - **If the model kept refusing:** a general message. The owner's words, in Turkish, are "Model hata döndü, farklı şekilde dene", which means "The model returned an error, try a different way." The English wording is not fixed yet.
  - **If the failure was technical** (no internet, a server error): the error's own text.

  The owner's words: "If the model refuses, let it return something like 'the model returned an error, try a different way'. If there really is an error, a technical one, no internet or an internal error, those can be passed on as they are."
- What follows from this, not a decision of its own: the "Couldn't get a response." card no longer appears when the model fails, because a model failure now ends as an answer. The card stays for failures that are not the model's, for example when QueenAgent's own server cannot be reached or the message cannot be sent.

**Left to the designer**
- How the retries show: where, in what words, and how they look.
- How the wait changes once retries begin, and how it gives way to the answer.
- How a stopped turn looks, now that it never has any answer text.
- How the failed answer looks, and whether it looks different from an ordinary answer.

**States that must be designed**
- **Waiting, no retry yet:** the dots and the line under them, as today.
- **Retrying once:** the first try failed, and the second is on its way.
- **Retrying several times:** for example the fourth or the fifth try.
- **Retrying in a later round:** steps already in the box above, and a retry in the round after them.
- **The answer arriving whole after retries:** the moment the retries give way to the complete answer.
- **Stopped:** pressed while waiting, or while retrying. No answer text, and the turn marked as stopped.
- **Failed after five refusals:** the general message as the answer, and the turn over.
- **Failed after five technical errors:** the error's own text as the answer, and the turn over. That text can be short and technical.

---

## 2. Undo after Archive goes

**Today**
- The app opens on "All projects", with two tabs: "Projects" and "Archived", each with its count beside it.
- On the Projects tab, a row's `⋯` menu holds "Rename", "Pin" (or "Unpin"), "Archive", and, under a line, "Delete" in red.
- Choosing "Archive" turns the row into a quiet line: "**<name>** archived · Undo", with "Undo" in rust red and ready for the keyboard. The two tab counts change at once. Archiving also unpins the project, so the line stands among the "Recent" projects, where the project's last use puts it.
- The line stays until the next thing is done: opening any row's `⋯`, switching tabs, or leaving the screen. "Undo" brings the project back.
- This line came from your own earlier round: item 135, "an archive is undone, never confirmed".
- On the Archived tab, a row's `⋯` menu holds "Rename", "Unarchive" and "Delete".

**Need.** The owner's words: "Remove the undo feature from archive."

**Fixed by the owner**
- The Undo line goes, everywhere.
- An archived project leaves the Projects tab at once and appears on the Archived tab.
- Nothing asks first. No confirmation takes the Undo line's place.
- The way back is the Archived tab's `⋯` → "Unarchive", as today.
- This is built without waiting for the design. It is here for your information, because it takes away part of item 135.

**Left to the designer.** Nothing is waiting on the design. The next round's drawings should show Archive without the Undo line.

**States that must be designed**
- **Just after Archive:** the row gone from the Projects tab, the Projects count one lower, the Archived count one higher, and no Undo line.
- **The last project archived:** the Projects tab reads "Every project is archived." at once.

---

## 3. Archived projects open

**Today**
- On the Projects tab, pressing a row opens the project. A project opens on its latest chat, or on an empty new chat if it has none. The top bar then shows the project's name in the middle and "Exit project" on the right, and the sidebar lists the project's chats.
- On the Archived tab, rows show the same three columns as on the Projects tab: the name, "N chats · N files", and how long ago the project was used. They tint on hover, but pressing a row does nothing. Only its `⋯` menu works.
- This came from your own earlier round: items 190 and 191.
- "Exit project" goes back to All projects, which always opens on the Projects tab.

**Need.** The owner's words: "Archived projects don't open. Make them open."

**Fixed by the owner**
- Pressing an archived project's row opens the project, the way any other project opens.
- Opening does not unarchive. The project stays on the Archived tab, and "Unarchive" is the way out of the archive. The owner's words: "Let it stay."
- An archived project can be chatted in. The owner's words: "Yes, it can be chatted in. The only difference between archived and unarchived projects is that they sit in different lists. There will be no other difference. Keep the differences simple."
- So nothing inside an archived project shows that it is archived. Its screens are the same as any project's.
- This is built without waiting for the design. It is here for your information, because it changes items 190 and 191.

**Left to the designer.** Nothing is waiting on the design. The next round's drawings should show archived rows as rows that open.

**States that must be designed**
- **An archived row:** something that opens when pressed, like a row on the Projects tab.
- **An archived project open:** the same screens as any other project.

---

## 4. Copy turns fully green

**Today**
- Copy buttons stand in three places:
  - **The sidebar inside a project,** when its chats could not be read: "Couldn't load chats.", with "Try again" and "Copy". Copy copies the error's words.
  - **The header of an open file,** beside "Refresh". Copy copies the whole file.
  - **All projects, and the screen for naming a new project,** when the project list could not be read: "Couldn't load projects.", with "Try again" and "Copy". Copy copies the error's words.
- Each is a small outlined button: an off-white face (#fffdfa), a thin beige border (#e2dcd2), and the word "Copy" in grey-brown (#6b6259).
- Pressed, the word becomes "Copied" for 2.5 seconds, then "Copy" again. Only the word changes colour: it turns the app's accent, a rust red (#b5623c). The face and the border stay as they were. The accent marks the main action across the app, such as the send button and "+ New chat", and on Copy the success reads like an error.
- If the copy fails, the word becomes "Could not copy" for 2.5 seconds, in the app's red for failures and deleting (#b23a2e).
- The new word takes the old word's place, so nothing around the button moves. In the file header, the button is wide enough for "Could not copy".
- In the file header, the button is dimmed while the file is still loading and there is nothing to copy. It cannot be pressed then.
- The app's colour set has no green of its own. Two small notes use a muted sage green: "✓ saved to project" on a file card (#6f8a5f), and the cached count under an answer (#536747).

**Need.** The owner's words: "Press Copy and 'Copied' comes up red. Make the button fully green. I want to see the green."

**Fixed by the owner**
- When a copy succeeds, the whole button turns green, not just its word.
- Every Copy button: the sidebar's, the open file's header's, and the failed project list's.
- After 2.5 seconds, the button goes back to how it looks today.
- "Could not copy" stays as it is today: red words on the button.
- The green comes from the designer. The owner's words: "We'll have the designer do it."

**Left to the designer**
- The green: its shade, and how the button's word, border and hover read on it.
- Whether the word "Copied" stays on the green button.

**States that must be designed**
- **Idle:** "Copy", as today.
- **Copied:** the whole button green, for 2.5 seconds.
- **Could not copy:** red words, as today.
- **Dimmed:** nothing to copy yet, in the open file's header while the file loads. It cannot be pressed, so it never turns green.
- **In each of its three places:** beside "Try again" in the sidebar and on the failed project list, and beside "Refresh" in the file header.

---

## What must keep working

- With no retry, the wait looks as it does today: the steps box, the dots, and the line with the time and the round under them.
- A refusal never shows as an answer, and a stopped turn never shows half an answer.
- The "Couldn't get a response." card, with its "Try again", stays for failures that are not the model's: QueenAgent's own server cannot be reached, or the message cannot be sent.
- On the Archived tab, `⋯` → "Unarchive" brings a project back, as today.
- Opening an archived project leaves it on the Archived tab.
- "Could not copy" stays red words on the button, as today.
- Every Copy button goes back to its usual look 2.5 seconds after a press.

---

## Open points to ask the owner

- **Retries (1):**
  - whether the screen counts the tries, for example "2 of 5"
  - whether each retry says why it happened: an error, or the model refusing
  - whether anything stays on the finished answer to show that it needed more than one try
- **The failed answer (1):**
  - its exact English wording for a refusal
  - whether it offers a way to ask again, as today's failure card does with "Try again"
- **A stopped turn (1):** whether it still shows the steps it got through before the Stop.
