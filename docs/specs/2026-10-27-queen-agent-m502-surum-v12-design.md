# Madde 502 · Başlıkta sürüm V12 yazar — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-5),
502 · v12-5 · **Dal:** `feat/queenagent-v12` · **Önceki:** v11'de
[489](../arsiv/specs/2026-10-22-queen-agent-m489-version-v11-design.md) ·
**Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 27 Ekim — "bir de her roadmapin başında şun uyapmanı istiyorum ui daki sürümü arttıralım
olur mu"; "ilk görev o olsun ynai". Koşunun ilk işi: ekrandaki sürüm `V11`'den `V12`'ye.

## Değişen

**Tek satır:** `queen-agent/frontend/src/shared/version.js`'te `VERSION = "V11"` → `"V12"`. Sayıyı
tutan tek yer o; üst çubuk (`Bar.jsx`) onu `QueenAgent` yazısının yanına çiziyor. `dist/` ve
`node_modules/` dışında `queen-agent/` altında `V11` geçen başka yer yok (tarandı).

Dosyanın yorumu değişmiyor: sayının neden elle yazıldığını ve ayrı bir modülde durduğunu söylüyor,
ikisi de bugün doğru.

## Testler

**Hiçbir test değişmiyor, yenisi de eklenmiyor.** `version.test.js` sayının biçimini (`/^V\d+$/`)
tutuyor, `V12` de ona uyuyor; `Bar.test.jsx` başlığın `QueenAgent ${VERSION}` olduğunu,
`Sidebar.test.jsx` kenar çubuğunun sürümü çizmediğini tutuyor. Değeri bir teste yazmak tek kararı iki
yere koyardı. Bu yüzden kırmızıya düşen bir test yok: değişiklik bir karar, davranış değil.

## `dist/`

Defter depoyu klonluyor ve build etmiyor; `dist/` aynı değişiklikle yeniden build'lenir. Colab'da
`V12`, o commit itildikten sonra görünür.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmiyor: sabit bir dize, disk ya da ağ yok.

## Bitti sayılır

Üst çubukta "QueenAgent V12" yazıyor; queen-agent'ın iki takımı yeşil.
