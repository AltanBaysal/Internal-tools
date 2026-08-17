# Madde 14 — Akış görselleri · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 14](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 41, 42, 43 · `HANDOFF.md` §3
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Üç farkın biri zaten kapandı

**fark 41 — yarım gelen kod bloğu.** Madde 13'ün ayrıştırıcısı kapanmamış çiti metnin sonunda
kapatıyor; bu onun doğal davranışı, eklenmiş bir emniyet değil. Bu maddede yalnız **akış içinde**
sınanıyor: parça parça uzayan bir metnin her adımı yerleşimi bozmadan çiziliyor mu.

Geriye iki iş kalıyor: **imleç** ve **kaydırma kuralı**.

---

## 1 · İmleç (fark 42)

Akış sürdüğü sürece metnin **ucunda** 7×15px, yanıp sönen bir blok durur. Son parça gelince kaybolur.

**Ucu bulmak bir kural gerektiriyor**, çünkü metin artık düz değil, bloklardan oluşuyor. İmleç en son
bloğun en derin son yerine iner:

| Son blok | İmlecin yeri |
|---|---|
| paragraf, başlık | satırın sonunda, metnin hemen ardında |
| kod bloğu | `<code>`'un içinde, son karakterin ardında |
| liste | son maddenin sonunda |
| alıntı | içindeki son bloğun kuralı neyse o |
| tablo, yatay çizgi | bloğun altında, kendi satırında |

Son ikisi bir istisna değil, kuralın kendisi: içine yazılacak bir metin ucu yok.

**İmleç vurgu rengi değildir.** `--accent` yalnız birincil eylemi işaretler; imleç metnin kendi
mürekkebiyle çizilir. Yanıp sönmesi uygulamadaki iki keyframe'den biri olan `blink`'tir — üçüncü bir
hareket icat edilmiyor.

İmleç `<Markdown>`'ın bir özelliği (`caret`), ayrı bir bileşen değil: yerini ancak blok ağacını
tanıyan biri bilebilir.

---

## 2 · Kaydırma kuralı (fark 43)

İki ayrı olay, iki ayrı davranış:

1. **Yeni bir mesaj** — liste dibe atlar. Kullanıcı kendi mesajını gönderdiğinde onu görmek ister.
2. **Akış sürerken** — liste dibe **yalnız kullanıcı zaten dibe 220px'ten yakınsa** yapışır.

İkincisi tasarımın kendi cümlesi ve sebebi tek satırda söylenebilir: yukarı çıkıp okuyan biri hiç
kesilmez. 220px `HANDOFF.md` §3'ün kendi sayısı.

Ölçü kaydırma kabının kendisinden okunur: `scrollHeight - scrollTop - clientHeight`.

**Bu bir sunum kararıdır**, arka uca sorulmaz — FOUNDATION karar 4 "ne gösterilir, ne kaydırılır"
sorusunu ön yüze bırakıyor.

---

## 3 · Katman denetimi

Değişen üç dosya: `Markdown.jsx` (imleç), `ChatScreen.jsx` (kaydırma), `workspace.css` (imlecin
ölçüsü). Yeni servis yok, yeni özellik yok, ayrıştırıcı hiç değişmiyor.

---

## 4 · Kabul ölçütü

1. Akan metnin ucunda bir imleç durur; akış bitince hiç kalmaz.
2. İmleç son bloğun türüne göre yerini bulur — paragrafın ucunda, kod bloğunun içinde, tablonun
   altında.
3. Yarım gelen çit `A`, `A\n\`\`\`js`, `A\n\`\`\`js\nx =` adımlarının hepsinde düzeni bozmadan
   çizilir.
4. Yeni mesaj listeyi dibe atar.
5. Dibe 220px'ten uzaktayken gelen akış parçası kaydırmaz; yakınken kaydırır.

## 5 · Risk

Kaydırma jsdom'da gerçekten kaymaz; testler `scrollHeight`/`clientHeight` tanımlayarak kuralı
sınıyor — yani sınanan şey **kararın kendisi**, kaydırmanın gözle görünür sonucu değil. Gözle
doğrulama Madde 35.
