# Queen Editor v9 · Görev 2 — Fotoğraf modelleri defterde kurulsun

**Tarih:** 2026-08-13 · **Yol haritası:** [v9](../plans/2026-08-13-queen-editor-v9-roadmap.md) · Görev 2
**Önkoşul:** [Görev 1](2026-08-13-queen-editor-v9-gorev-1-kurulum-uygulamadan-kalksin-design.md) —
uygulamadaki ikinci kurulum yolu kalktı.

## Problem

Görev 1'den sonra hiçbir model kurulamıyor: uygulama artık indirmiyor, defter henüz indirmiyor.

## Karar

**Defterin bu daldan önceki hâli geri gelir — birebir** (kullanıcı kararı). O hücreler bu
uygulamada fotoğraf üretimini uçtan uca çalıştırmıştı; yeniden yazmak, çalıştığı bilinen bir şeyi
tahmine çevirmek olurdu.

Geri gelen üç parça, v7'de çıkarıldıkları yerden:

| Parça | Ne yapar |
|---|---|
| Yardımcılara `human`, `head_text`, `check_safetensors` | boyutu insanca yazar, bir yanıtın ilk baytlarını ham gösterir, safetensors dosyasının kendi başlığından beklenen boyutu hesaplar |
| "Modeller — önce gated probe, sonra indir" markdown'ı | ne olacağını ve model eklemenin nasıl yapılacağını anlatır |
| İndirme hücresi | beş dosyayı indirir ve doğrular |

İndirme hücresinin taşıdığı ve bizim kaybettiğimiz bilgi de bunun içinde:

- **Kapılı dosya `curl` ile iner, `aria2c` ile inmez.** Civitai depoya yönlendiriyor; çerez o
  host'a taşınırsa 403 geliyor. `curl` çerezi host değişince bırakıyor, `aria2c` taşıyor. Bizim
  403'ümüzün sebebi buydu.
- **Ağır indirmeden önce 1 KB'lık yoklama.** Çerez ölmüşse 6.5 GiB'a başlamadan, Civitai'nin kendi
  yanıtıyla durur.
- **Dosya `.part` adıyla iner**, doğrulama "ok" deyince gerçek adına geçer. ComfyUI hiçbir zaman
  yarım dosyayı model sanmaz.
- **Bozuk dosya silinmez**, incelensin diye diskte kalır ve hücre durur.

## Kapsam

**Yalnız fotoğrafın beş dosyası** — iki Civitai (checkpoint + lora), üç açık kaynak (Remacri, yüz
dedektörü, SAM). Eski hücrenin listesi zaten tam olarak bu; ekleme yapılmıyor.

Video ve ses modelleri bu görevde yok (kullanıcı kararı). MMAudio kütüphanesi de geri gelmiyor:
sesin sırası geldiğinde konuşulur.

## Yeri

Custom node hücresinden sonra, **ComfyUI başlatılmadan ve Flask kalkmadan önce** — v7 öncesindeki
yerinin aynısı. Sebebi artık ikinci bir işe de yarıyor: panel "kurulu mu" cevabını uygulama
açılırken bir kez okuyor, o yüzden dosyalar o andan önce yerinde olmalı.

## Test

Bir test, uygulamanın **okuduğu** listeyle defterin **indirdiği** listeyi birbirine bağlar:
fotoğraf grubundaki beş dosya adının her biri defterde geçmeli. Bu bağ olmazsa gruba eklenen bir
dosya panelde sonsuza kadar "kurulu değil" der ve kimse sebebini bulamaz.

Hücrenin kendisi test edilmez: indirme dış dünya, ve bu makine zaten kanıtlanmış.

## Birebir olmayan tek şey

Yardımcılar hücresinin başındaki yorum, eski defterde olmayan bölüm numaraları sayıyordu ("section
6 (render)"). Çalışan tek satır değişmiyor; yalnız o cümle bu defterdeki gerçek kullanıcılarını
söyler. Yorumun kodla çelişmemesi kuralı, kopyanın birebirliğinden önce gelir.
