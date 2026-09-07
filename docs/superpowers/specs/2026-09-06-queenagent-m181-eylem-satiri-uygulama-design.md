# Madde 181 · uygulama turu — eylem satırının içi

**Kaynağı:** [test turu spec'i](2026-09-06-queenagent-m181-eylem-satiri-testler-design.md).
Commit `00fb596` 5 kırmızı bıraktı.

---

## Tek dosya, tek paragraf

`WRITE_FRAME_SYSTEM_PROMPT`'a bir paragraf giriyor, ve **176'nın kıyafet paragrafından hemen sonra**:
o paragraf neyin yazarın olmadığını söylüyor, bu da neyin olduğunu. Ayrı yerlere düşerlerse model
ikisini iki ayrı kural gibi okur ve aralarındaki sınırı kendisi çizer — Deneme 4'te olan tam olarak
buydu.

Paragrafın söyledikleri:

- **Görünen adlandırılır**, etrafından dolaşılmaz. Üç örnek metnin içinde, çünkü bu metnin öteki
  bütün kuralları örnekli — ve Deneme 4 ilkeyi bilen bir modelin yine de dolandığını gösterdi.
- **Sebebi yanında.** Model adı geçmeyeni uydurur; gerekçesi olan kural, listede olmayan bir duruma
  da uygulanabilir. Gerekçesiz üç örnek, modelin yazacağı şeyin tamamı olurdu.
- **Yüz ifadesi.** Karakter etiketi yüzü tarif eder, ama şu anda ne yaptığını hiçbir yer yazmaz.
- **Çıplaklık yazarın işi değil.** Karede kıyafeti olmayan zaten çıplak; `nude` yazmak kadronun
  söylediğini bir daha söylemek olurdu — 176'nın *"ikinci kopya birinciyle çelişendir"* kuralı.

## Nereye girmiyor

`SDXL_PROMPT_RULES`'a. O metin `add_character`, `add_outfit`, `add_location` ve `build_prompts`'un
açıklamalarına ekleniyor, ve bir karakterin etiketine giren anatomi kelimesi o karakterin **her
karesine** çizilir. Kullanıcının Deneme 4'te elle kaçındığı sızma bu, ve maddenin yazara gitmesinin
sebebi de bu. İki nöbetçi test bunu tutuyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **831 yeşil.** 5 kırmızının hepsi dönmeli, iki nöbetçi yeşil kalmalı.
3. Öteki üç takım: **589 · 739 · 591.** `dist` derlenmiyor.
