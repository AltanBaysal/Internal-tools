# Madde 387 — Reddedilen yeniden adlandırma yazılan adı kaybetmez · uygulama

Testler: `docs/superpowers/specs/2026-09-30-queenagent-m387-reddedilen-yeniden-adlandirma-testler-design.md`.

## Değişen tek yer: `ProjectRow.jsx`'in `RenameField`'ı

Bugün alan, adı `onDone`'la yukarı verip hemen kapanıyor. Değişiklikten sonra alan iki şey alır:

- `onSave(name)` — adı gönderir, bir söz döner; kabulde truthy, redde falsy çözülür.
- `onClose()` — alanı kapatır.

`finish(save)`:

1. `done` ref'i kuruluysa hiçbir şey yapmaz (bugünkü gibi: Enter'ın ardından gelen blur, ya da cevap
   beklenirken ikinci Enter, ikinci istek olmaz).
2. Vazgeçildiyse (Esc) ya da ad boşsa `onClose()` — sunucuya hiçbir şey sorulmaz, alan hemen kapanır.
3. Değilse `await onSave(ad)`: kabulde `onClose()`; redde `done` geri bırakılır ve alan açık kalır,
   yazılan ad içinde, odak nerede bıraktıysa orada. Enter ya da blur aynı adı tekrar gönderebilir.

`ProjectRow` alanı şöyle bağlar: `onSave={(name) => onRename?.(project.id, name)}`,
`onClose={() => setRenaming(false)}`.

## Değişmeyenler

- `useProjects`'in `editProject`'i zaten kabulde düzenlenen projeyi, redde `null`'ı dönüyor, ve
  `writeError`'ı kuruyor/temizliyor; `App` `onRenameProject`'te bu sözü olduğu gibi geri veriyor.
  Dokunulmaz.
- Hata `AllProjectsScreen`'in `.list-error` satırında, bugünkü yerinde. Satıra yeni bir hata satırı,
  yeni CSS yok.
- `dist` bu maddede kurulmaz; birleştiren kurar.

## Neden alan cevabı bekliyor

Alan önce kapanıp redde yeniden açılsaydı, satır bir an eski adı gösterir, odak alana geri çekilirdi
— kullanıcı başka yere basmışsa odağı elinden alırdı. Beklerken açık kalan alan, ad sorma ekranının
yaptığıyla aynı: ad, cevap gelene kadar da reddden sonra da yazıldığı yerde durur.
