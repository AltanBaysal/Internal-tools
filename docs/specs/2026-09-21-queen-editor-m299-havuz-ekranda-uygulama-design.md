# Madde 299 — Havuz ekranda, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m299 test turu](2026-09-21-queen-editor-m299-havuz-ekranda-testler-design.md),
`458e45ef` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Sunucu tarafı: liste sınırları da söyler

`/api/projects/<p>/references` cevabı `{"references": […], "limits": {picture, video, audio}}`
oluyor. Sınırlar **298**'in tablosundan okunuyor; ekranın kendi kopyası olsaydı, tablo değiştiği gün
ekran eski sayıyı söylemeye devam ederdi.

## `shared/api.js`

`request` bir **`timeout`** seçeneği alıyor *(varsayılanı bugünkü 10 sn)*, ve `fetch`'e
geçirilmiyor — bizim sayacımız. Yükleme **iki dakika** kullanıyor: 15 saniyelik bir video Drive'a
on saniyede çıkmayabilir.

Üç çağrı ve bir adres yardımcısı: `listReferences`, `uploadReferences` *(FormData; `Content-Type`
elle konmaz — sınırı tarayıcı yazar)*, `removeReference`, `referenceUrl`.

## `ReferencePanel.jsx`

Kendi verisini kendi çekiyor: proje değişince listeler. Üç sıra, her biri tipinin karolarını ve
başlığında **doluluğunu** taşıyor. Karo: fotoğraf resmini, video sessiz bir `<video>`'yu, ses bir
karoyu gösteriyor; kliplerin altında süresi *(`4,2 sn` — virgüllü, Türkçe)*.

**Ekle** düğmesi bir `<label>`, içinde gizli çoklu dosya girdisi: vendor kit'in düğme görünümü,
tarayıcının kendi dosya seçicisi. **Sil** her karonun köşesinde ve önce soruyor *(madde 83)*.

Sunucunun cümlesi olduğu gibi basılıyor — `StatusErrorCard`, ekranın geri kalanında olduğu gibi.

## `ProjectScreen.jsx`

Üçüncü sütun en sola giriyor. Açık/kapalı bileşenin kendi durumu — sunucuya sorulmuyor, diske de
yazılmıyor: panelin hâli oturumun, havuz diskin.

Kapalıyken yerinde onu geri açan ince bir şerit kalıyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Frontend değiştiği için **`dist` aynı commit'te**
yeniden üretilir *(CLAUDE.md)*.
