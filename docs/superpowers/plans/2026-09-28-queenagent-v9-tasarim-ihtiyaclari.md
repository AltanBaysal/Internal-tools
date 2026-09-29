# QueenAgent: design needs for the next round

QueenAgent is a small AI workspace in the browser. Work is organised into projects, each project holds chats and files, and the assistant's answers in a chat can create files in the project. The interface is in English on purpose. This document lists the needs the owner wants the next design round to answer. It states problems and the owner's fixed decisions, not solutions. Anything not stated here as the owner's decision is the designer's call. Where something is open, ask the owner rather than assume: they want to talk the open points through with you. The known ones are listed at the end.

---

## 1. Projects need fixing

**Today**
- The app opens straight into the first project in the list. With no projects, it shows a separate "No projects yet" screen.
- The sidebar lists projects under "Projects". Each row has a dot, the name, the number of files (hidden at zero) and a `⋯` menu. New projects are named "New project 1", "New project 2" and so on.
- While a project is selected, the sidebar also shows "+ New chat" at the top and "Recent chats" (up to eight) below the projects.
- The project screen shows:
  - the name as a large title, with "Rename" and "Delete" beside it
  - a box for starting a new chat
  - two columns: "Chats" (each with its title, how long ago it was used, and `×` to delete) and "Files QueenAgent created"
- A chat's header reads "← project name / chat title". The project's files are listed on the right under "Project files".

**Need.** The owner's words: "QueenAgent's design will be updated, and above all the projects side will be fixed."

**Fixed by the owner.** Nothing beyond the need itself.

**Left to the designer.** Everything. The owner has not said what is wrong with projects today or what "fixed" looks like, and wants to talk it through with you.

---

## 2. Project management

**Today**
- A project has only two actions: rename and delete.
- Both actions are in two places:
  - the `⋯` menu on the project's sidebar row ("Rename", "Delete project")
  - the buttons beside the title on the project screen ("Rename", "Delete")
- Rename opens the browser's own prompt box, "Project name", filled with the current name. An empty answer cancels.
- Delete asks first. The box reads `Delete "<name>"?` and "The N chats and N files in this project are deleted with it. This can't be undone.", with a "Delete project" button.

**Need.** Project management is to be improved.

**Fixed by the owner.** Nothing beyond the need itself.

**Left to the designer.** What better project management looks like. The owner has named no new action, and wants to talk it through with you.

---

## 3. Starting a new project and a new chat

**Today.** There are three separate places, as the owner counts them:
- **The `+` beside "Projects" in the sidebar.** It creates a project at once without asking for a name, so it gets "New project N". The project is added at the end of the list, and the screen stays where it was.
- **"+ New chat" at the top of the sidebar**, shown only while a project is selected. It opens an empty chat titled "New chat". The chat only really exists once its first message is sent, and it takes its title from that message.
- **The "No projects yet" screen**, shown only when there are no projects. It reads "Chats live inside a project, and the files they create stay there. Create a project to start." Its "+ New project" button creates a project and opens it.

The project screen also has a box, "Start a new chat in this project...", which starts a chat when its first message is sent.

**Need.** Starting a new project or a new chat is confusing, because several separate places do it today: the three the owner counts, and probably the project screen's box as well.

**Fixed by the owner.** Nothing beyond the need itself.

**Left to the designer.** Where and how a new project and a new chat are started.

---

## 4. The notes under a message

**Today**
- **Under a message the user wrote, two lines stack:**
  - First, a line with the version strip `‹ 1/2 ›` and the edit pencil `✎`. The strip appears only when the message has been edited and has more than one version. The pencil is faint until the message is hovered.
  - Below it, on its own line, the time (e.g. `14:32`).
- **Under an answer**, there is no pencil. One line gives the time and the token count (e.g. `14:32 · 3.4k tokens`).
- **While an answer is still running**, that line's place shows `round 2/16 · 3.4k tokens ·`, a spinner and a changing word. When the answer ends, the time and the count take its place.

**Need.** Under the user's message, the pencil and the time stack one above the other instead of sitting side by side.

**Fixed by the owner.** Nothing beyond the need itself.

**Left to the designer.** How the notes under a message are laid out.

---

## 5. A full chat: "continue here"

**Today**
- **The gauge.** In an open chat, the typing box has a small circle at its left end that fills as the chat grows. Hovering it says "N% of the context ceiling". The circle appears after the first answer.
- **The limit.** A chat is full at 50,000 tokens. Today that count covers everything sent with the last request: the conversation plus the instructions and files that go with it.
- **What a full chat does.** It takes no more messages. When the user sends one:
  - their message is taken back and the sentence returns to the typing box
  - a single line of red text appears under the conversation: "this chat has reached its context ceiling -- start a new chat to keep going"
- The line has no button. The way on is "+ New chat" in the sidebar. The full chat stays readable.

**Need.** Instead of only starting a new chat, the user can keep going in the same one: like compacting in Claude Code, but simpler. The oldest messages are trimmed from the top, down to 10k of context.

**Fixed by the owner**
- The limit stays at 50,000 tokens.
- The limit and the circle count only the chat's messages. The instructions and the files opened along the way stop counting.
- "Continue here" appears only when the chat is full. It sits next to starting a new chat, beside today's new-chat notice.
- Choosing it trims the oldest messages from the start until the chat is down to 10,000 tokens. Only the last 10,000 go to the model. There is no summary.
- The trimmed messages stay on screen. They only stop going to the model.
- After trimming, the chat takes messages again.

**Left to the designer**
- How the option looks and where it sits.
- How a full chat is announced. Today it is announced only after a message is refused.
- Whether and how the screen shows which messages no longer go to the model.

**States that must be designed**
- **Not full:** the chat as it grows, with the circle filling.
- **Full:** the notice with both choices, start a new chat and continue here.
- **Trimmed:** every message is still on screen, the oldest ones no longer go to the model, and the chat takes messages again.
- **Before and after trimming:** what the user sees just before choosing "continue here" and just after, including what changes and what stays the same.

---

## 6. The version next to the name

**Today.** At the top of the sidebar is "QueenAgent", with the version ("V8") under it in small, faint, letter-spaced type. When the sidebar is folded, both are hidden.

**Need.** Under the name, faint and small, the version reads like a footnote and goes unread.

**Fixed by the owner.** The version sits next to the name, the same size as the name, in bold. Putting it under the name is rejected.

**Left to the designer.** Everything else about it.

---

## 7. The model picker goes

**Today**
- In the typing box, on both the project screen and the chat screen, a button reads "Queen Flash ⌄".
- It opens a menu headed "MODELS" with two rows and their prices:
  - "Queen Flash": $0.22 / $0.66 per 1M
  - "Queen Pro": $0.66 / $1.98 per 1M

**Need.** Only one model is left, so there is nothing to pick. Queen Pro's underlying model was shut down by its provider on 14 September; choosing Queen Pro today gets Queen Flash's answers while the screen still says Pro.

**Fixed by the owner**
- Queen Pro goes, and only Queen Flash remains.
- The picker is removed.
- The model's name appears only as text: "Queen Flash".

**Left to the designer.** Where the name sits and how it looks.

---

## 8. "Improve" in the skill picker

**Today**
- In the typing box, on both screens, there is a "Skills ⌄" button. When a skill is chosen, the button shows that skill's name, tinted.
- It opens a menu headed "SKILLS" with two rows, each a name and a one-line description:
  - "Start a scenario": "Answer a few questions and get the characters, the places and the prompts."
  - "Edit prompts": "Fix what is wrong in prompts you already have, and build them again."
- The chosen row carries a ✓, and choosing it again clears it. Having no skill chosen is an ordinary state.

**Need.** A new skill, "Improve", which the user chooses when they want it. It runs four checks on a scenario's frames and their prompts:
- each frame shows a single moment
- a prompt names only what can be seen from the camera's angle
- the weak photo model can actually draw the prompt
- the scenario gets its list of negative prompts

Start a scenario ends with the same checks.

**Fixed by the owner**
- It is a new row in the skill picker, named "Improve".
- At the end of each check, the answer shows what it changed and waits for the user's yes.
- A long scenario's checks can spread over several turns, and the user says "continue".
- The checks themselves happen inside the conversation; only the new row in the picker is part of this design round.

**Left to the designer.** Where the row sits among the others and how it looks.

**States that must be designed**
- The picker open, with three rows.
- Improve chosen: its row checked and its name on the button.

---

## 9. Cached and missed tokens under an answer

**Today**
- Under an answer, one line gives the time and one token count (e.g. `14:32 · 3.4k tokens`).
- Every request re-sends the whole conversation. The service reports, for each one, how many of the
  tokens sent it already had in its cache and how many it did not. The cached ones cost about fifty
  times less than the missed ones, so one number says little about what an answer really cost.
- Today's count adds cached and missed together as if they cost the same.
- This one is not scheduled for a build yet. It is here so the design round covers it together with
  the notes under a message (4).

**Need.** The owner's words: "show two under every chat, one green and one red: green cached, red
missed cached."

**Fixed by the owner**
- Two numbers under an answer instead of one: the cached tokens and the missed ones.
- The cached number is green, the missed number is red.

**Left to the designer**
- How the two numbers sit next to the time, and how they are told apart beyond their colour.
- Whether the tokens the model wrote back are shown as well, and how. Today they are inside the one
  count; neither green nor red covers them.

**States that must be designed**
- **An answer that came mostly from the cache:** a large green number, a small red one.
- **An answer that came mostly from outside it:** the other way round.
- **An old answer with no count at all:** today it shows the time alone.

---

## What must keep working

- Trimmed messages stay on screen and readable. They only stop going to the model, and no summary replaces them.
- Starting a new chat stays available when a chat is full. "Continue here" is added beside it, not in its place.
- The limit stays at 50,000 tokens, and the circle stays, now counting only the chat's messages.
- Start a scenario and Edit prompts stay in the skill picker. Improve is added to them.

---

## Open points to ask the owner

- **Projects (1):** what is wrong with them today, and what "fixed" means.
- **Project management (2):** which actions are missing or weak.
- **Continue here (5):**
  - what the circle reads right after trimming
  - whether "continue here" is offered again when a trimmed chat fills up
  - whether choosing it asks first, and whether it can be undone
- **Improve (8):** its one-line description in the picker; the two existing rows have one.
- **Cached and missed tokens (9):** whether the line shown while an answer is still running
  (`round 2/16 · 3.4k tokens ·`) splits into green and red too, or keeps one number until the answer
  ends.
