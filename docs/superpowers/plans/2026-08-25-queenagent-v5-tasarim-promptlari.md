# QueenAgent v5 — claude.ai/design promptları

**Tarih:** 2026-08-25 · **Kaynak:** [v5 yol haritası](2026-08-25-queenagent-v5-roadmap.md)

Beş iş, beş prompt. **Teker teker atılır**: biri gidip tasarım düzelene kadar öteki beklenir —
üçü aynı alana (cevabın kendi bölgesi ve composer) bakıyor ve aynı anda giderlerse birbirinin
yerini alırlar.

**Sıra önemli:** 1 → 2 → 3 yakın zamanda lazım (yol haritasının Blok 1'i, tek başıma koşulacak
kısım). 4 ve 5 Blok 2'de, sonra.

**Promptlar İngilizce** çünkü içlerindeki her etiket ürüne İngilizce giriyor; çeviri katmanı
eklemek etiketleri bozar. Başlıklar ve notlar Türkçe.

Her promptun sonunda tasarımcıya bırakılan sorular var — bilerek. O kararlar tasarımın kendi işi;
yol haritasının spec'leri onları ratifiye eder, önden dayatmaz.

**Her prompt iki şeyi daha istiyor:** `QueenAgent Handoff`'un güncellenmesini — davranış sözleşmesi
o ve çelişkide o kazanıyor, yani yalnız prototipte yaşayan bir eleman gecikmeli bir çelişki — ve
handoff'un başında bir **değişiklik günlüğü** tutulmasını. Günlük ayrı dosyaya değil handoff'un
içine yazılıyor: aynı bilgi iki yerde tutulunca birinde bayatlıyor.

---

## 1 — Tool call satırı *(Madde 66, yakında lazım)*

> QueenAgent is a small AI workspace. A project holds chats and files; a chat's answer can create
> files. You already have its design — I want to add one element to the chat screen.
>
> **What happens today.** While an answer is being produced, the model can call tools: list the
> project's files, read one, edit one, or build the prompt list from a structure file. A single
> answer can chain up to sixteen of these. None of it is drawn. The user sees three blinking dots
> and nothing else, and when a file is being written a dashed "creating file…" card appears and is
> then replaced by a solid file card. Everything else is invisible — during the wait and forever
> after, because these steps are never written to the chat record either.
>
> **What I need.** A new element in the message column that shows each tool call as it happens, and
> keeps showing it after the answer is finished. Someone reading the chat a week later should be
> able to see that the answer read `bar-scene.md` before it wrote anything.
>
> **Stay inside the existing language.** Canvas `#F7F5F1`, sidebar `#EFEBE4`, surface `#FFFDFA`,
> ink `#22201D`, muted `#8B8378`, hairline `#E2DCD2`. One accent only, `#B5623C`, and it marks the
> primary action — a tool call is not a primary action, so it should not take the accent. Newsreader
> for headings, DM Sans for body, DM Mono for labels, numbers and time. Radii: 8px controls, 12px
> cards, 20px pills. Motion is opacity only, 180–220ms; nothing that has settled on the screen may
> be pushed sideways when a new line arrives. The existing mono label above a message is 10.5px,
> uppercase, 0.06em letter-spacing, muted — the family this element probably belongs to.
>
> **Do not** use red (reserved for destructive actions), do not invent a second accent, and do not
> add a spinner: the three dots are the only waiting animation this product has.
>
> **Decide and show me:** whether the line names only the tool or also what it was given (a file
> name); whether the calls stay as a list or collapse into one summary line once the answer lands;
> and whether they sit inside the answer's own block or above it. Show the states: one call running,
> several finished, and a call that failed.
>
> **Also update the handoff, and log the change.** `QueenAgent Handoff` is the behaviour contract in
> this project and it wins over the prototype wherever the two disagree — so something that exists
> only in the prototype is a contradiction with a delay on it. Write what this change means for
> behaviour into the handoff: the states involved, the keyboard behaviour if any, and what is shown
> when there is nothing to show. Then add a line to a **change log** at the top of the handoff,
> newest first: the date, what changed, and what it replaced. Keep that log inside the handoff rather
> than in a file of its own — the same fact kept in two places goes stale in one. The log is how I
> see what moved without re-reading the whole design.

---

## 2 — Durdurma *(Madde 67, yakında lazım)*

> QueenAgent — the chat screen again, this time the composer.
>
> **What happens today.** The composer's bottom row is, in order: a **Skills** picker, a **model**
> picker, and the **Send** button. Send is filled with the accent `#B5623C` and goes flat grey
> `#E5DFD5` with `cursor: not-allowed` when the draft is empty. Once an answer starts streaming,
> nothing about this row changes — and there is no way to stop the answer. Leaving the chat does not
> stop it either; coming back asks for it again from the start.
>
> **What I need.** A way to stop an answer that is already running. It has to be reachable the whole
> time the answer is streaming, and it has to be obvious that it stops rather than sends.
>
> **Stay inside the existing language.** Same palette and type as the rest: canvas `#F7F5F1`,
> surface `#FFFDFA`, ink `#22201D`, muted `#8B8378`, accent `#B5623C` (hover `#9E5232`), hairline
> `#E2DCD2`. Radii 8px for controls, 20px for pills. Focus ring is 2px `#B5623C` with 2px offset,
> everywhere, no exceptions. Motion is opacity only, 180–220ms.
>
> **The hard rule:** nothing that has settled may move. If the button's label changes mid-answer,
> its box must not resize and the row must not reflow — the user's pointer is already there.
>
> **Do not** use red. Stopping your own answer is not destructive; red belongs to deleting things.
>
> **Decide and show me:** whether **Send** itself becomes **Stop** while the answer runs, or whether
> Stop is a separate control that appears beside it; and what the answer looks like the instant after
> it is stopped — does the half-written text stay on screen with a mark saying it was stopped, or
> does it go. Show all three states: idle, streaming, just-stopped.
>
> **Also update the handoff, and log the change.** `QueenAgent Handoff` is the behaviour contract in
> this project and it wins over the prototype wherever the two disagree — so something that exists
> only in the prototype is a contradiction with a delay on it. Write what this change means for
> behaviour into the handoff: the states involved, the keyboard behaviour if any, and what is shown
> when there is nothing to show. Then add a line to a **change log** at the top of the handoff,
> newest first: the date, what changed, and what it replaced. Keep that log inside the handoff rather
> than in a file of its own — the same fact kept in two places goes stale in one. The log is how I
> see what moved without re-reading the whole design.

---

## 3 — Token sayacı *(Madde 68, yakında lazım)*

> QueenAgent — the chat screen.
>
> **What happens today.** Nothing tells the user what an answer cost. The engine reports, for every
> answer, how many tokens went out, how many came back, and how much of the outgoing side was served
> from cache rather than paid for again. None of it is shown. In long chats the context reaches
> 300–500k tokens, so the difference between cached and freshly paid is the whole story — and it is
> invisible.
>
> **What I need.** A place that says what an answer cost: the total, the part that came from cache,
> and the part that was paid again.
>
> **Stay inside the existing language.** DM Mono is the family for numbers in this product —
> the mono label above a message is 10.5px, uppercase, 0.06em, colour `#8B8378`. Palette: canvas
> `#F7F5F1`, surface `#FFFDFA`, ink `#22201D`, muted `#8B8378`, hairline `#E2DCD2`. The accent
> `#B5623C` marks the primary action and a number is not one. Radii 8px / 12px / 20px. Motion is
> opacity only, 180–220ms.
>
> **The weight problem is the real problem.** This number is diagnostic, not the point of the screen.
> Someone reading a conversation must be able to ignore it completely; someone hunting cost must be
> able to find it without opening anything. Solve that tension.
>
> **Do not** turn it into a chart, a badge with a colour scale, or anything that competes with the
> answer text.
>
> **Decide and show me:** whether it sits under every answer, in the chat's own total, or both; and
> whether the cached/fresh split is always visible or only on hover or expand. Show a cheap answer
> and an expensive one side by side.
>
> **Also update the handoff, and log the change.** `QueenAgent Handoff` is the behaviour contract in
> this project and it wins over the prototype wherever the two disagree — so something that exists
> only in the prototype is a contradiction with a delay on it. Write what this change means for
> behaviour into the handoff: the states involved, the keyboard behaviour if any, and what is shown
> when there is nothing to show. Then add a line to a **change log** at the top of the handoff,
> newest first: the date, what changed, and what it replaced. Keep that log inside the handoff rather
> than in a file of its own — the same fact kept in two places goes stale in one. The log is how I
> see what moved without re-reading the whole design.

---

## 4 — Model seçici kalkıyor *(Madde 72, Blok 2 — sonra)*

> QueenAgent — the composer, a removal this time.
>
> **What happens today.** The composer's bottom row is **Skills · model · Send**. The model picker
> opens a menu of six models, each row a name and a line saying what it costs per million tokens.
>
> **What changes.** The product moves to a single model. There will be nothing to choose, so the
> model picker leaves the row entirely.
>
> **What I need.** The composer's bottom row redrawn with two things instead of three: **Skills** and
> **Send**. The question is what the row does with the space — Skills stays left and Send stays
> right with a wider gap, or the whole row rebalances, or something else earns the place.
>
> **Stay inside the existing language.** Palette: canvas `#F7F5F1`, surface `#FFFDFA`, ink
> `#22201D`, muted `#8B8378`, hairline `#E2DCD2`, accent `#B5623C` on Send only. Radii 8px controls,
> 20px pills. Focus ring 2px `#B5623C`, 2px offset.
>
> **Also decide:** whether the model's name should appear anywhere at all once it can no longer be
> chosen — a chat record still knows which model answered it, and a user might want to know. If the
> answer is no, say so; a screen that says nothing is a legitimate answer.
>
> **Show me** the composer on both the chat screen and the empty draft screen, since both carry it.
>
> **Also update the handoff, and log the change.** `QueenAgent Handoff` is the behaviour contract in
> this project and it wins over the prototype wherever the two disagree — and a removal is the case
> where this matters most: a control deleted from the prototype but still described in the handoff
> reads as a bug for as long as nobody notices. Take the model picker out of the handoff too. Then
> add a line to a **change log** at the top of the handoff, newest first: the date, what changed, and
> what it replaced. Keep that log inside the handoff rather than in a file of its own — the same fact
> kept in two places goes stale in one. The log is how I see what moved without re-reading the whole
> design.

---

## 5 — Skill menüsü *(Madde 74, en son)*

> QueenAgent — the Skills picker.
>
> **What happens today.** The picker holds six entries, each a name and a second line saying what it
> does and whether a file comes out of it: create a scenario, create a character prompt, split into
> frames, generate prompts, generate prompts+ (builds from a structure file so a character never
> drifts), verify prompts. The user picks one and it stays picked until they change it.
>
> **What changes.** These six are really one chain — scenario, frames, characters, prompts, check —
> and the user is carrying the chain by hand. Some of the six are going away entirely; the rest
> collapse into a single flow.
>
> **What I need.** What the picker becomes when there is one flow instead of six choices. That may
> mean a much shorter menu, a different control, or no control at all — if the flow is one thing,
> there may be nothing left to pick, and the screen should say where in the chain the user is
> instead.
>
> **Stay inside the existing language.** Palette: canvas `#F7F5F1`, surface `#FFFDFA`, sidebar
> `#EFEBE4`, ink `#22201D`, muted `#8B8378`, hairline `#E2DCD2`, one accent `#B5623C`. DM Sans for
> body, DM Mono for labels. Radii 8px / 12px / 20px. Motion opacity only, 180–220ms.
>
> **Decide and show me:** whether a picker survives; and if the flow has steps, whether the user sees
> which step they are on and whether they can go back to an earlier one. Show the empty state — a
> chat where the flow has not started — and a chat in the middle of it.
>
> **Also update the handoff, and log the change.** `QueenAgent Handoff` is the behaviour contract in
> this project and it wins over the prototype wherever the two disagree — so something that exists
> only in the prototype is a contradiction with a delay on it. Write what this change means for
> behaviour into the handoff: the states involved, the keyboard behaviour if any, and what is shown
> when there is nothing to show. Then add a line to a **change log** at the top of the handoff,
> newest first: the date, what changed, and what it replaced. Keep that log inside the handoff rather
> than in a file of its own — the same fact kept in two places goes stale in one. The log is how I
> see what moved without re-reading the whole design.

---

## Not

5. promptun içeriği **74. maddenin spec'inde** hangi skillerin düşeceği kararlaşınca kesinleşir.
Bugünkü hâli soruyu doğru soruyor ama cevabın yarısını taşımıyor; en sona bırakılmasının sebebi bu.

Tasarım güncellendikçe çıkan farklar ilgili maddenin spec'ine girer — tasarım görsel şartnamedir,
kaynak kod değildir.
