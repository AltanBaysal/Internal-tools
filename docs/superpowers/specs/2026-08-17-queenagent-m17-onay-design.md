# Madde 17 — Onay kutusu bileşeni · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 17](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 26'nın görsel yarısı · **karar 16, 17** · `HANDOFF.md` §6, §9
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Yol haritasının kaynak etiketi yine yanlış

Yol haritası bu maddeyi "karar 1" diye anıyor; karar 1 **model düğmesinin yeri** ile ilgili ve
composer'a ait. Buradaki kararlar **karar 17** — "sohbet silme onayı tarayıcının kutusuyla değil,
tasarımın modal'ıyla sorulur, böylece uygulamada tek bir onay dili olur" — ve onun dayandığı
**karar 16**, geri almayı tümüyle kaldıran karar.

(Bu, yol haritasında bulunan altıncı kayma: Madde 5, 6, 10, 11, 15 ve şimdi 17.)

---

## 1 · Bu madde bir bileşen üretir, bir davranış değil

Kutuyu açan iki iş **Madde 18** (proje silme) ve **Madde 19** (sohbet ve dosya silme). Bu madde
yalnız kalıbı kuruyor: karartı, kart, serif başlık, sonucu anlatan cümle, "Cancel" ve dolu kırmızı
onay düğmesi.

Kalıbın kendisi karar 16'nın sonucudur: **onay var, geri alma yok.** FOUNDATION'ın "ya onay ya geri
alma, asla ikisi de değil" kuralı onay tarafından karşılanıyor; diskte hiçbir şey kaybolmuyor, silinen
`trash/` altına taşınmaya devam ediyor.

---

## 2 · Esc bu maddede gelmiyor, Madde 18'de geliyor

Uygulamada **klavyeyi tek bir dinleyici sahiplenir** — App'in kendi `keydown` kancası — ve sıralamanın
tek yerde durması bilerek verilmiş bir karar (`FilePanel.test.jsx` bunu yazıyor: "Escape bu bileşenin
tuşu değil"). Kutu kendi dinleyicisini kurarsa iki dinleyici aynı olayı paylaşır ve sıra iki yere
bölünür.

Bu maddede kutuyu açan kimse yok, yani App'in kapatacağı bir şey de yok. **Esc, ilk çağıran ile
birlikte Madde 18'de** App'in tek dinleyicisine ekleniyor — okuma panelinden **önce**, `HANDOFF.md`
§9'un sırasına göre. Yol haritası Esc'i bu maddede sayıyor; bileşene kendi dinleyicisini yazdırmamak
için bir madde ötelendi.

Karartıya tıklamak burada, çünkü o kutunun kendi olayı: dinleyici yok, sıra sorunu yok.

---

## 3 · Bileşen

`features/workspace/ConfirmDialog.jsx`:

```
<ConfirmDialog
  title={'Delete "Thesis research"?'}
  body="The 3 chats and 2 files in this project are deleted with it. This can't be undone."
  confirmLabel="Delete project"
  onConfirm={…}
  onCancel={…}
/>
```

Cümleleri **çağıran** verir. Kutu ne sildiğini bilmez; bildiği tek şey iki düğme ve bir karartıdır.
Sayıların tekil/çoğul hâli ("1 chat") çağıranın işi, Madde 18'de.

**Odak açılınca "Cancel"a gider.** Tasarım söylemiyor ama bir yere gitmesi gerekiyor: klavyeyle
gelen biri Enter'a bastığında yıkıcı olan değil, vazgeçiren şey olmalı.

`role="dialog"`, `aria-modal="true"` ve başlığa bağlı `aria-labelledby`.

---

## 4 · Ölçüler

`HANDOFF.md` kutunun ölçülerini vermiyor; §6 yalnız cümleleri ve düğmeleri veriyor. Bu yüzden ölçü
uydurulmuyor, paletin kendi belirteçleri kullanılıyor: kart `--surface` ve `--radius-card`, onay
düğmesi `--destructive` dolu ve `--destructive-hover`, karartı `--ink`in saydamı, beliriş
`fadeIn` 160ms — yani var olan tek banttan.

Genişlik 420px'te duruyor: iki düğme ve iki satır cümle için, `.creating`in 340px'iyle aynı ailede.

---

## 5 · Katman denetimi

Tek yeni bileşen, tek özellik (`workspace`). Yeni servis yok, `shared/` büyümüyor — bu bir çizim.

---

## 6 · Kabul ölçütü

1. Başlık, cümle, "Cancel" ve onay düğmesi çizilir; onay düğmesinin adı çağırandan gelir.
2. "Cancel" `onCancel`ı, onay düğmesi `onConfirm`ı çağırır.
3. Karartıya tıklamak iptal sayılır; **kartın kendisine** tıklamak sayılmaz.
4. Kutu açılınca odak "Cancel"dadır.
5. Kutu kendi `keydown` dinleyicisini kurmaz.
6. Onay düğmesi `--destructive` ile dolu, karartı ekranı kaplar.

## 7 · Risk

Yok denecek kadar az: kutu bu maddede hiçbir yerden açılmıyor, dolayısıyla bozacak bir davranış da
yok. Asıl sınama Madde 18 ve 19'da, kutu iş görmeye başladığında.
