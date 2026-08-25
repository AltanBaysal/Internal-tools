# v14 Görev 32 — Elde cevap varken gösterge yanmaz: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** kullanıcı kuralı, Colab turu
**Öncesi:** [Görev 32 test spec'i](2026-08-24-queen-editor-v14-gorev-32-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 32

## Ne yeşile döndürülüyor

Yedi kırmızı test. Üçü kaydın, ikisi model listesinin, ikisi üretici satırlarının bir ziyaret
boyunca hatırlanmasını istiyor.

## Üç depo, tek kural

| Hook | Depo | Anahtar |
|---|---|---|
| `useProjectSettings` | `Map` | proje adı |
| `useModels` | tek yuva | yok — liste makinenin |
| `useProducers` | tek yuva | yok — satırlar makinenin |

Kural üçünde de aynı: **mount hatırlanandan başlar, arkada yine sorulur, gelen cevap yerini alır, ve
düşen bir tazeleme hatırlanana dokunmaz.**

## Hatırlanan şey her zaman gerçekten cevaplanmış olan

Üç depo da yalnız başarılı bir cevabı tutar. Düşen bir istek hiçbir yere yazılmaz — yoksa bir sonraki
mount, sunucunun hiç söylemediği bir şeyi hatırlanmış cevap sanardı.

Bunun kolay kaçırılan hâli **model listesi**: bir istek düştüğünde bugün liste boşa düşüyor, ve boş
liste geçerli bir cevap gibi görünüyor — "hiçbir model kurulu değil" de boş liste. İkisini ayıran
şey yanındaki hata: boş liste ancak hatasız geldiğinde hatırlanır.

## Depo state'i izler, cevabı değil

Üçünde de yazma işi state'i izleyen bir effect'te. Sebebi `useProducers`'da görünüyor: `Kur`
satırların üstüne bir cümle yazıyor, yani ekrandaki liste artık sunucunun verdiği liste değil. İlk
cevabı hatırlamak, kullanıcının bir saniye önce okuduğu cümleyi geri dönüşte silerdi.

`REMEMBERED` de aynı sebeple effect kullanıyor; üç yeni depo o kalıbı sürdürüyor.

## Proje değişince ne olur

`useProjectSettings` bir mount'un içinde proje değiştirebiliyor — adres bir projeden ötekine
geçebilir. O anda state, yeni projenin kendi hatırlananıyla değişir; hatırlanmıyorsa beklemekle
başlar. Bu, `useGeneration`'ın kare listesi için yaptığının aynısı ve aynı biçimde yazılır.

Projeye ait geç gelen cevabı yutan bugünkü koruma olduğu gibi kalıyor.

## Bir şey değişmiyor: ne zaman sorulduğu

Üç istek de her mount'ta yine gidiyor. Bu madde **cevap beklenirken ekranda ne olduğunu**
değiştiriyor, ne sıklıkta sorulduğunu değil. İsteği hiç göndermemek ayrı bir karar ve burada
verilmiyor.

## Ömür

Üçü de bellekte. Sayfa yenilenince her şey ilk günkü gibi sorulur — `KEPT` ve `shownPictures` ne
kadar yaşıyorsa o kadar. Bir ziyaret içinde durmak isteniyor, projenin bir özelliği yazılmak değil.

## Beklenen görünüm

Bir kareye girip geri dönmek: **ekranda hiçbir şey kıpırdamaz.** Fotoğraf panelinin kutuları dolu,
model kutusu seçili modeliyle, üretici satırları notlarıyla yerinde. Üç istek arkada gider ve gelir.

İlk giriş bugünkü gibi: kayıt panelinde halka, model kutusunda `yükleniyor…`, üretici satırları
cevap gelene kadar yok.

## Kapsam dışı

- **Kuyruk paneli** — 33. madde.
- **Açık panel ve seçim** — 34. madde.
- **Sunucu tarafı** hiç açılmıyor.
- **Test dosyaları değişmiyor.**

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer.
