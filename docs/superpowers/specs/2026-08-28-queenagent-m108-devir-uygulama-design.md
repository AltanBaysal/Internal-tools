# Madde 108 — Devir beşinci adım olur · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m108-devir-testler-design.md) — iki kırmızı
`3ddcba8`'de. Sebep orada; bu belge ne yazılacağını söylüyor.

## Değişen tek şey: akış metni

- **Dört adım beşe çıkar.** Giriş cümlesi *"Five steps in a fixed order"* olur.
- **Kapanış paragrafı numaralı adım olur** — `5. The handoff.`:
  - iki dosyayı adıyla söyler, senaryonun hazır olduğunu söyler, ve kullanıcıyı skill
    menüsündeki Generate prompts+'a yollar;
  - kural olarak: frame'ler burada **hiç** yazılmaz, kullanıcı istese bile — partili yazım ve
    kamera kararı öteki skill'in işi, ve istek oraya işaret edilerek cevaplanır;
  - onay beklemez: 1. adım gibi, bu da beklemeyen adım — son sözdür.

Devir artık listenin içinde ve emir kipinde. Eski gerekçe *("doing its work twice")* yerini kurala
bırakıyor: gerekçe zayıf modelde kural yerine geçmiyor.

## Değişmeyen

- 4. adımın kendisi *(sahne listesi, frames boş)*.
- Onay döngüsü ve *"marked done"* cümlesi — 5. adım onay beklemediğini kendi içinde söylüyor.
- prompt+ metni ve seçici satırı **113**'ün işi; burada ellenmiyor.

## Görülür hâli

İki kırmızı yeşerir, başka test kırılmaz *(defter çifti hariç)*. Ön yüz değişmediği için `dist`
derlenmez.
