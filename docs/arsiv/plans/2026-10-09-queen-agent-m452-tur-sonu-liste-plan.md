# Madde 452 — Proje listesi ve sohbet sırası, konuşunca, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** All projects'e girilince proje listesi bir kez okunur; soru sunucuya ulaşan bir tur
bitince kenar çubuğunun sohbet listesi bir kez okunur. Var olan sohbette konuşup projeden çıkınca
proje listenin başında, zamanı yeni.

**Yaklaşım:** Önce test, kırmızı görülür, sonra kod. Dosyalar Edit ile değişir.

**Spec:** [m452](../specs/2026-10-09-queen-agent-m452-tur-sonu-liste-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce.
- Arka ucun koduna, yol haritasına ve queen-editor'e dokunulmaz.

---

## Görev 1: sunucunun son kullanımı — `test_last_activity.py`

- [ ] `test_talking_in_an_existing_chat_brings_its_project_and_the_chat_up`: iki proje, eskisinde iki
  sohbet, hepsi 2000'den, açık `add` satırlarıyla yazılıp `flush` edilir; eski projenin eski sohbetine
  `{"chat": "cold", "text": …}` gönderilir; proje listede öne geçer, `lastActivity` yenilenir, sohbet
  `/chats`'te öne geçer. Sunucu zaten doğru olduğu için ilk koşuşta yeşil — bu test bir kontroldür.

## Görev 2: testler — `App.test.jsx`

- [ ] Madde 192'nin turun sonu testlerinin altında: sunucusu POST'ta proje ve sohbet sırasını
  değiştiren bir sahte; `gatedSse` ile `chat` ve iki `progress` karesi; şerit `round 2/16` derken
  sohbet listesi 1 kez okunmuş; akış bitince 2, kenar çubuğunda sohbet önde, proje listesi hâlâ 1;
  Exit project'ten sonra All projects'te proje başta, zamanı `just now`, proje listesi 2. Kırmızı.
- [ ] `stubRefusingChat` ile bağlantı hatasıyla düşen gönderiş: sohbet listesi 1, proje listesi 1,
  kenar çubuğu satırlarını tutuyor, *"Couldn't load chats."* yok. Kırmızı.

## Görev 3: kod

- [ ] `useChat.js`: `ended.current?.(reached)`, yorumuyla.
- [ ] `App.jsx`: `onTurnEnd` → `refresh()`, `reached` ise `reloadProjectChats()`; `onFileCreated` →
  `reloadFiles`; `onChatBorn` yalnız `reloadProjectChats`; `route.view` `"root"`'a girince — önceki
  görünüm bir `useRef`'te, ilk çizim sayılmaz — `reloadProjects()`. `refresh`'in üstündeki yorum
  güncellenir. Yeşil; bütün ön uç suite'i yeşil.

## Görev 4: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`; `dist` `git add` ile sahnelenir.
- [ ] Dört suite, birer birer: `python -m pytest queen-agent -q`, `npm test --prefix
  queen-agent/frontend`, `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
