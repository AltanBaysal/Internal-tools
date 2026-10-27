# Madde 489 · Başlıkta sürüm V11 yazar — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
489 · v11-4 · **Dal:** `feat/queenagent-v11` · **Önceki:** v10'da
[442](2026-10-09-queen-agent-m442-surum-v10-design.md) · **Kurallar:**
[FOUNDATION](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı bunu Queen Editor v10 için istedi *(20 Ekim — "v10 btin ceditorde sürüm bump etmeyide yaz
sonra unutyorsun", "yad başta bump et ui da")*; QueenAgent için de onayladı *(20 Ekim — "evet
lütfen")*. Koşunun ilk işi: ekrandaki sürüm `V10`'dan `V11`'e.

## Değişen

**Tek satır:** [version.js](../../../queen-agent/frontend/src/shared/version.js)'te `VERSION = "V10"` →
`"V11"`. Sayıyı tutan tek yer o; ekranda yalnız üst çubuk
([Bar.jsx](../../../queen-agent/frontend/src/features/workspace/Bar.jsx)) onu çiziyor — *"QueenAgent
V11"*. `dist/` ve `node_modules/` dışında `queen-agent/` altında `V10` yazan başka yer yok (tarandı);
442 yorumları sayısız bıraktı.

Dosyanın yorumu değişmiyor: sayının neden elle yazıldığını ve çubuğun onu çizdiğini söylüyor, ikisi
de bugün doğru.

## Testler

**Hiçbir test değişmiyor, yenisi de eklenmiyor.** `version.test.js` sayının biçimini (`/^V\d+$/`)
tutuyor, `V11` de ona uyuyor; `Bar.test.jsx` başlığın `QueenAgent ${VERSION}` olduğunu,
`Sidebar.test.jsx` kenar çubuğunun sürümü göstermediğini tutuyor. Değeri bir teste yazmak tek kararı
iki yere koyardı (`version.test.js`'in yorumu). Bu yüzden kırmızı adım yok: değişiklik bir karar,
davranış değil.

## Sınırlar

- Defterin `BRANCH`'ı sürüm değil, defterin klonladığı dal; bu maddenin işi değil.
- queen-editor'e ve geçmişi kaydeden roadmap ve spec'lere dokunulmaz.

## `dist/`

Defter depoyu klonluyor ve build etmiyor; `dist/` aynı değişiklikle yeniden build'lenir. Colab'da
`V11`, o commit itildikten sonra görünür.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmiyor: sabit bir dize, disk ya da ağ yok.

## Bitti sayılır

Üst çubukta *"QueenAgent V11"* yazıyor; `V10` hiçbir yerde yok; queen-agent'ın iki takımı yeşil.
