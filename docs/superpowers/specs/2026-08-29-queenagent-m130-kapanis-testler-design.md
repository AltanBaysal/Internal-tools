# Madde 130 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 130
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Yedinci denemenin kapanışı üç şıklı bir menüydü — *"bir kareyi değiştirelim · sadece belirli
kareleri göster · başka bir şey ekle"* — ve öncesinde model `build_prompts`'un yazdığı dosyayı
okuyup 25 promptu cevaba döktü. Dosya zaten projede.

Madde 112 bu kuralı taban yönergeye yazdı. prompt+ turunda tutmuyor, ve sebebi 93'ün yerleşimi:
**skill metni isteğin son sözü**, ve kapanış hakkında hiçbir şey söylemiyor. Zayıf model en sonda
duran metni dinliyor, ve o metin susuyorsa boşluğu kendi dolduruyor — 108 ile 118 aynı şeyi
gösterdi.

## Yol

prompt+ kendi kapanışını söyler: kurulan dosya cevabın kendisidir, promptlar geri basılmaz, menü
açılmaz.

**Yer 128'den geliyor.** Kare ekleme cümlesi *"Add frames with edit_file in batches of five, each
on disk before the next"*ten *"Add frames with add_frames, in batches of five"*e indi. 123'ün
kuralı: bir cümle ancak bir cümle silinerek girer, ve tavan *(300 kelime)* bir test tarafından
tutuluyor — girmiyorsa bu turda görülür.

## Kurallar

- **Taban ellenmez.** 112 zaten orada, ve doğru yazılmış; sorun tabanın söylememesi değil, skill'in
  susması.
- **Akış ellenmez.** 118 onun kapanışını zaten yazdı — devir mesajı teklif değil bildirim.
- **Kelime tavanı bir bekçi.** Cümle giriyorsa tavan da tutmalı; tutmuyorsa metinden bir cümle
  çıkar, ve hangisi olduğu uygulama turunun kararı.

## Bu turun testleri

`test_skills.py` *(yeni)*:

- `test_prompt_plus_closes_with_the_file_rather_than_a_menu` — **kırmızı**

`test_skills.py` *(bekçi, mevcut)*: `test_the_texts_stay_short_enough_to_be_read` — 300 kelimelik
tavan. Uygulama turunda yeşil kalmak zorunda, ve bu maddenin asıl kısıtı o.

## Ayakta kalması gerekenler

112'nin taban cümlesi, 118'in akış kapanışı, 128'in `add_frames` cümlesi ve beşerli ritmi,
prompt+'ın şema çağrısı, elle-kurma yasağı, ve 113'ün `edit_file` ile düzenleme yolu.

## Bilerek yapılmayanlar

Ön yüz, taban yönerge, akış metni. Tek dokunulan yer prompt+.
