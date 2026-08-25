# v14 Görev 31 — Galeri gerekmeyen bir cevabı beklemez: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** Colab turu, aynı gün · kullanıcı kuralı
**Öncesi:** [Görev 31 test spec'i](2026-08-24-queen-editor-v14-gorev-31-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 31

## Ne yeşile döndürülüyor

Önceki commit yedi testi kırmızı bıraktı. Üçü ekranın bölünmediğini istiyor, dördü bekleyişin
fotoğraf üret panelinin kendi sütununda durduğunu.

## Değişikliğin şekli

Bugün proje kaydının durumu **adres seviyesinde** okunuyor: `App` kaydı bekliyor, gelene kadar
`ProjectScreen` hiç doğmuyor. Yarın kayıt bir **prop** olarak aşağı iniyor ve durumunu isteyen panel
okuyor.

```
Bugün                            Yarın
─────                            ─────
App                              App
 └ kayıt hazır mı?                └ ProjectScreen (her zaman)
    ├ hayır → ProjectLoading         └ SidePanel
    ├ hata  → tam ekran kart             └ fotoğraf üret paneli
    └ evet  → ProjectScreen                  ├ hata  → kart
                                             ├ yok   → halka
                                             └ var   → form
```

Kaydın kendisi, okunması, ne zaman istendiği — hiçbiri değişmiyor. Değişen tek şey **kimin
beklediği.**

## Üç prop

`ProjectScreen` ve `SidePanel` aynı üçlüyü taşıyor; ikisi de yalnız geçiriyor, hiçbiri okumuyor.
Okuyan tek yer `SidePanel`'in fotoğraf panelini çizdiği dal.

| Prop | Ne taşır |
|---|---|
| `settings` | Kayıt, ya da henüz yoksa `null` |
| `settingsError` | Sunucunun kendi cümlesi, ya da `null` |
| `onRetrySettings` | Yeniden sormanın yolu |

`settings` zaten vardı; yeni olan **`null` olabilmesi**. Diğer ikisi yeni.

## Sıralama: hata halkadan önce

Kayıt okunamadığında `settings` de `null` oluyor — yani iki koşul aynı anda doğru. Hata önce
sorulur, yoksa dönmeyi bırakmayan bir halka çıkar ve hiçbir şey gelmeyeceğini kimse söylemez.

## Bir şey bilerek olduğu gibi kalıyor

**Fotoğraf üret paneli kutularını açılışında bir kez dolduruyor.** Bu, kullanıcı yazarken üstüne
yazılmamasının tek sebebi ve dosyanın kendi yorumu bunu söylüyor. Panel bundan sonra da kayıt
geldikten sonra doğar; yalnız arkasındaki ekran artık boş değil. Sözleşme aynı, sonradan senkron
edilen kimse yok.

## Silinen dosya

`ProjectLoading.jsx` gider. Tek çağıranı `App.jsx`'ti ve o dal kalkıyor; testi hiç yoktu, yerine ne
geldiğini `App.test.jsx`'in üç testi söylüyor.

## Beklenen görünüm

| Hâl | Ekranda |
|---|---|
| Kayıt yolda | Galeri, başlık, ray, beş panel — hepsi çalışır. Fotoğraf paneli kendi sütununda halka. |
| Kayıt geldi | Bugünkü ekranın aynısı. |
| Kayıt okunamadı | Aynı ekran; fotoğraf panelinde `Proje ayarları yüklenemedi` kartı ve `Tekrar dene`. |

Uygulamanın dili değişmiyor: kartın cümlesi bugün ne diyorsa aynısını diyor, yalnız durduğu yer
değişti.

## Kapsam dışı

- **Hatırlama yok** — 32. madde. Kayıt hâlâ her mount'ta yeniden isteniyor; bu döngü yalnız
  beklemenin nereye indiğini değiştiriyor, ne sıklıkta olduğunu değil.
- **Kuyruk panelinin ilk cevaptan önceki cümlesi** — 33. madde.
- **Açık panel ve seçimin hatırlanması** — 34. madde.
- **Sunucu tarafı** hiç açılmıyor.

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` **aynı commit'e** girer (CLAUDE.md). Defter derlemiyor; itilmemiş
bir `dist` Colab'da görünmez.
