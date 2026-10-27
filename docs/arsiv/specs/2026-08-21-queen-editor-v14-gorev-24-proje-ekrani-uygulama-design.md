# v14 · Görev 24 — Proje ekranının hizalaması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-24-proje-ekrani-testler-design.md) ·
commit `c7a8ce2` (dokuz test, sekizi kırmızı) · tasarım v4 fark listesi 5, 6, 8, 9 · 1. karar ·
43, 44, 45. kararlar.

Kırmızı duran sekiz test ne istiyorsa o yazılıyor. Dört dosya ön yüzde, biri stil. Motor açılmıyor.

## Çöp yıkıcı standarda, kalem `ghost`'a

`ProjectCard` bugün iki düğmeyi de kendi eliyle çıplaklaştırıyor: `border: "none"`,
`background: "none"`, `padding: "4px 8px"`. İkisi de kaldırılıyor, çünkü ikisi de tasarım kitinin
zaten cevapladığı sorular.

| | Bugün | Olacak |
|---|---|---|
| **Çöp** | `border: none`, kırmızı ikon | `Btn sm icon` + evin yıkıcı kalıbı: `color`, `borderColor` kırmızı, `background: none` |
| **Kalem** | `border: none`, elle padding | `Btn sm icon ghost` |

`wf-btn--ghost` kitte duruyor ve tam bunun için yazılmış: `background: transparent`,
`border-color: transparent`. Çizgi çizmiyor ama **kutuyu koruyor** — `border: none` kutuyu her
kenardan bir piksel küçültüyordu ve iki düğme birbirine göre bir piksel kayıyordu.

`wf-btn--icon` de kitte var ve uygulamada hiç kullanılmamış: içeriği yalnız bir ikon olan düğmenin
iç boşluğu (`5px 7px`). İkisi de onu alıyor, dolayısıyla iki kutu aynı ölçüde.

Yazı yok, ve bu standardın eksik uygulanması değil: standardın istediği söz silme onayının
penceresinde duruyor. Kullanıcının 9 Ağustos 2026 kararı da (v2 fark listesi N4) yazısız diyor.

## Pencerenin ölçüsü penceresinin oluyor

`NameModal`'ın `width` parametresi düşüyor; genişlik 380 olarak pencerenin içinde duruyor. İki
çağıran da `width` vermeyi bırakıyor.

Bileşenin başındaki yorum da düzeltiliyor: *"başlığı, açılış değeri, sözleri ve ölçüsü çağıranından
gelir"* diyordu — ölçü artık gelmiyor.

`ConfirmModal`'ın `width`'i duruyor. Onun üç penceresi gerçekten farklı uzunlukta cümleler taşıyor;
105. maddenin kuralı orada hâlâ iş görüyor.

## Ekran bir ekran boyuna iniyor

`minHeight: "100vh"` → `height: "100vh"`. Gövde ikiye ayrılıyor:

```
<div height:100vh column>
  <header>                                  ← yerinde duruyor
  <div flex:1 position:relative minHeight:0> ← bant için çerçeve
    <div data-list class=qe-thin-scroll>     ← kayan kutu
    {kalabalık && <div data-fade>}           ← kutunun üstünde, içinde değil
```

**Bant kutunun içinde olamaz**, çünkü içerikle birlikte kayıp gider. Kutunun üstünde duruyor,
`pointer-events: none` ile — görünmeyen bir perde, altındaki karta gitmesi gereken tıklamayı
yemesin.

**`minHeight: 0` şart.** Flex çocuğu varsayılan olarak `min-height: auto` ve içeriğinden küçülmüyor:
onsuz kutu ızgara kadar uzuyor ve `overflow-y: auto` hiç tetiklenmiyor. Aynı satır uygulamanın
diğer kayan sütunlarında da var.

`data-list` her hâlde çiziliyor — yükleniyor, hata, boş, dolu. Gövdenin kendisi o kutu; yalnız bant
şarta bağlı.

### `.qe-thin-scroll`

`app.css`'e giriyor, çünkü bir sözde-eleman kuralı inline yazılamaz. Kural yalnız WebKit'in
sözde-elemanları: uygulama Colab'ın çıktı çerçevesinde, yani Chrome'da koşuyor.

Tutamak `--border-strong`, üstüne gelince `--border-active` — evin kendi iki çizgi rengi. Yol
saydam: bir oluk çizmek, kayacak bir şey olmadığında bile kutunun kenarında bir şerit bırakırdı.

## Onayın cümle sırası

İki cümle yer değiştiriyor, "Bu işlem geri alınamaz." sonda kalıyor. Metin `ProjectsScreen`'deki
`ConfirmModal` çağrısında, tek yerde.

## Ne değişmiyor

- **Motor.** Dört farkın hiçbiri sunucuya dokunmuyor; Python takımı 709'da kalıyor.
- **`ConfirmModal`'ın genişliği** (340) ve **`width` parametresi.**
- **Boş listenin metni**, **yükleme ve hata hâlleri** — hepsi kararla kapalı.
- **Kalemin ve çöpün yeri**: sağ üstte, 4px arayla, kalem solda.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 709 / 533. Derlenmiş çıktı aynı commit'e giriyor.
