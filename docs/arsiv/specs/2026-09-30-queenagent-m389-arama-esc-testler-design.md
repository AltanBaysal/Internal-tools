# Madde 389 — Sohbet aramasında Esc yalnız aramayı boşaltır · test turu

**Kaynak:** [yol haritasının 389'u](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — 365
tarayıcıda denenirken bulundu. Kullanıcı, 30 Eylül: "bunlarıda düzelt". Bitti sayılır: "`Search
chats`'te Esc aramayı boşaltıyor, açık dosya açık kalıyor."

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; aşağıdaki tek karar (boş kutuda Esc) teknik bir
seçim ve bugünkü davranışı koruyor.

## Bugün ne oluyor

Esc'i iki yer dinliyor:

- `Sidebar.jsx`'in arama kutusu, kendi `onKeyDown`'ında Esc'te `setQuery("")` yapar (365).
- `App.jsx`'in tek `window` dinleyicisi Esc'te açık olanı içten dışa kapatır: proje menüsü → onay
  kutusu → açık seçici → açık dosya → adlandırma ekranının Cancel'ı.

Kutunun olayı durdurulmadığı için `window`'a kadar kabarır. Kutuda yazı varken ve sağda bir dosya
açıkken tek Esc ikisini birden yapar: arama boşalır, dosya kapanır.

## Karar: boş kutuda Esc

Tasarımın `BEHAVIOUR.md`'si yalnız "Escape clears the box" diyor; katmanlamaya dair bir şey yok.
Seçilen kural: **Esc bir basışta bir şey kapatır, içten dışa** — `App.jsx`'in zaten uyduğu kural.
Kutuda yazı varken en içteki şey o yazıdır: Esc onu boşaltır ve orada durur. Kutu boşken boşaltılacak
bir şey yoktur: Esc bugünkü gibi sıradakine geçer, açık dosyayı kapatır.

Neden: öteki yol — kutudaki her Esc'i kutuda tutmak — boş kutuda hiçbir şey yapmayan bir tuş bırakır
ve bugün çalışan bir davranışı (boş kutuda Esc dosyayı kapatır) sessizce siler. Seçilen kural yalnız
hatalı basışı değiştirir; başka her Esc bugünkü gibi kalır.

## Ne kanıtlanacak

Testler `App.test.jsx`'e, "Escape closes the reading panel"ın hemen altına girer — Esc'in sırası
App'in işi, ve iki taraf (kutu ile açık dosya) yalnız orada birlikte durur.

1. **Yazı varken Esc aramayı boşaltır, açık dosya açık kalır.** Dosya açılır, kutuya yazılır, Esc
   kutunun üstünde basılır: kutu boş, dosyanın metni hâlâ ekranda. Bugün metin kaybolur: kırmızı.
2. **Boş kutuda Esc açık dosyayı kapatır**, başka her yerde olduğu gibi. Bugün de böyle: yeşil
   başlar, yukarıdaki kararı kilitler — uygulama olayı her durumda durdurursa kırmızıya döner.

## Testler ne tutmaz

- Kutunun kendi davranışı (daraltma, Enter, Esc'in kutuyu boşaltması) `Sidebar.test.jsx`'te zaten
  tutuluyor; değişmez.
- Mesaj düzeltme kutusunun ve proje adı alanının Esc'i: madde yalnız `Search chats` hakkında.

## Bu turda yazılmayanlar

- `Sidebar.jsx` ve `App.jsx` değişmez; uygulama turunda.
- `dist` derlenmez: kaynak değişmiyor, yalnız testler ve belgeler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` birinci testte kırmızı,
ikincide yeşil verir; öteki üç süit değişmez. Kırmızı hâliyle commit edilir.

Adım adım dökümü
[test turunun planında](../plans/2026-09-30-queenagent-m389-arama-esc-testler-plan.md).
