# Madde 79 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-26-queenagent-m79-gonder-durdurmaya-doner-testler-design.md](../specs/2026-08-26-queenagent-m79-gonder-durdurmaya-doner-testler-design.md)
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Yeni ad yok

`Composer` iki prop kazanıyor — `running` ve `onStop` — ve React tanımadığı prop'u sessizce yok
sayar. Toplama hatası riski yok.

## Dosyalar

`frontend/src/features/workspace/Composer.test.jsx` ·
`frontend/src/features/workspace/ChatScreen.test.jsx`

Arka uca dokunulmuyor. `App.test.jsx`'e de dokunulmuyor: durdurmayı `App` üzerinden soran testler
düğmeyi adıyla arıyor, sahibini değil.

## Testler

### `Composer.test.jsx` — dört test

Bir cevap akarken düğme `Stop` diyor. Akarken taslak boş olsa da basılabiliyor ve basınca `onStop`
çağrılıyor. **Akarken basmak `onSubmit` çağırmıyor** — iki iş tek düğmede, ve yanlış olanı
çalışırsa kullanıcı yazmadığı bir şeyi göndermiş olur. Akmıyorken hiçbir şey değişmiyor: düğme
eylem adını söylüyor ve boş taslakta kapalı *(bekçi — bugün de öyle)*.

### `ChatScreen.test.jsx` — bir yeni

Cevap akarken yazma kutusunun altı üç düğme taşıyor — `Skills`, model, ve `Stop` — dördüncü yok.
Var olan *"the foot carries Skills, the model and Send, in that order"* testinin akan hâli, ve bu
maddenin tek cümlelik kanıtı.

**İki test bilerek dokunulmadan bırakılıyor:** *"an answer that is running can be stopped"* ve
*"with nothing running there is nothing to stop"*. İkisi de düğmeyi adıyla arıyor, sahibini değil
— yani davranışı soruyorlar. **Değişmeden yeşil kalmaları maddenin kanıtı**: görünen değişti,
çalışan değişmedi. Bir tanesi bile düşerse durdurma gerçekten bozulmuş demektir.

## Beklenen kırmızı

**Ön yüzde 4 kırmızı, 1 bekçi yeşil.**

| Test | Durum |
|---|---|
| Akarken düğme `Stop` diyor | 🔴 |
| Akarken boş taslakta basılabiliyor ve `onStop` çağırıyor | 🔴 |
| Akarken basmak göndermiyor | 🔴 — bugün gönderiyor |
| Akmıyorken düğme eskisi gibi | 🟢 bekçi |
| Altta üç düğme var ve sonuncusu `Stop` | 🔴 — bugün dört var |

**Arka uçta değişiklik yok:** `2 failed, 442 passed`, ikisi defterin dalı.

**Var olan hiçbir ön yüz testi düşmemeli.** `Composer` iki prop kazanıyor ama ikisi de opsiyonel,
ve `ChatScreen`'in ayrı `Stop` düğmesi bu turda hâlâ yerinde. Düşen olursa mekanik değil gerçek bir
kırılmadır.

## Bu turda yapılmayan

`Composer`'ın düğme mantığı · `ChatScreen`'in ayrı `Stop` düğmesinin silinmesi · `.stop` stilinin
silinmesi · `dist` derlemesi. Hepsi ikinci tur.
