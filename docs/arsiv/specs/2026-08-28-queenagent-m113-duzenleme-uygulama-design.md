# Madde 113 — prompt+ var olanı da düzenler · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m113-duzenleme-testler-design.md) — üç
kırmızı. Sebep orada; bu belge ne yazılacağını söylüyor.

## prompt+ metni — iki dokunuş

**Açılış iki işi birden söyler:** *"When the user wants the prompts of a scenario built **or
changed**, this is the skill for both."* Zayıf model açılışta görmediği işi üstlenmiyor; bu yüzden
sıfat cümlenin başında.

**Son paragraf düzenleme yolunu anlatır:**

- hangi kare olduğunu bul — üretilen liste **karelerin sırasında** koşar, yani üçüncü prompt
  üçüncü karedir;
- yanlış olanı `edit_file` ile düzelt: ya karenin kendi `action`/`camera` değeri, ya da adını
  taşıdığı haritadaki girdi;
- `build_prompts`'ı **tekrar** çağır.

Ve iki cümlelik gerekçe: harita girdisi, onu anan her kareye ulaşan tek düzenlemedir; prompt
dosyası her seferinde yapı dosyasından yazıldığı için **yamanmaz, yeniden kurulur** — elle
düzenlenirse kaynağıyla örtüşmesi biter.

## Seçici satırı — `skills.js`

*"Build the prompts from a structure file you already have."* →
*"Build the prompts from a structure file you already have, and change them later."*
`already have` pini korunuyor. `dist` kaynağıyla aynı commit'te derlenir.

## Değişmeyen

Elle prompt kurma yasağı, partili yazım, şema çağrısı, akış metni *(108 kapandı)*.

## Görülür hâli

Üç kırmızı yeşerir; başka test kırılmaz *(defter çifti hariç)*.
