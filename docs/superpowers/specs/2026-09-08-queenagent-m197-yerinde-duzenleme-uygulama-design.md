# Madde 197 · uygulama turu — düzenleme mesajın kendi yerinde

**Kaynağı:** [test turu](2026-09-08-queenagent-m197-yerinde-duzenleme-testler-design.md), ve onun
kaynağı [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 197.

Kırmızı: ön yüzde 11.

---

## `ChatScreen.jsx`

`editing` artık `{index, text}` — `token` gitti, çünkü onu isteyen `Composer`'dı.

Bir kullanıcı mesajı iki hâlden birinde çiziliyor:

- **kapalı:** bubble, ve altında kalem *(`.msg__edit`)*;
- **açık:** `textarea` *(`.msg__editing-input`)*, altında ✓ ve ✕ *(`Confirm edit`, `Cancel edit`)*.

İkisi bir arada olmuyor: açıkken bubble da kalem de yok. Sarmalayıcı kalktığı için ikisi de `.msg`'in
doğrudan çocuğu, ve hizalamayı yine sütun yapıyor.

Taslak metni bileşenin kendi `useState`'inde duruyor — `Composer`'daki gibi, ve aynı sebeple:
kutunun anlık hâli ekranın bir durumu, sohbetin değil.

✓ `onSend(text, index)` çağırıp alanı kapatıyor; ✕ ile Escape yalnız kapatıyor. Boş bir metinle ✓
hiçbir şey yapmıyor — `Composer`'ın kuralı.

## `Composer.jsx`

`filled` ve onu okuyan effect kalkıyor; `useEffect` importu da onunla. Kutu yine yalnız kendi
taslağını biliyor.

## `workspace.css`

`.msg__said` siliniyor. `.msg__edit` kalıyor *(sessiz, hover ve odakta açılıyor)*, ama artık satır
içinde değil sütunda duruyor. Yeni: `.msg__editing` *(`max-width: 78%`, bubble'ın ölçüsü)*,
`.msg__editing-input`, ve `.msg__editing-actions` *(sağa yaslı bir satır)*.

## Yeşilin nasıl görüleceği

Dört sabit satır. Ön yüzde 645, ve arka uç ile `queen-editor` yerinde: **926 · 739 · 591**. `dist`
bu commit'in içinde.
