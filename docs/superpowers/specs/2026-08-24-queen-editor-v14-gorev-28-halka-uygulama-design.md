# v14 Görev 28 eki — Bekleyen karo da döner: İMPLEMENTASYON döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** [test spec'i](2026-08-24-queen-editor-v14-gorev-28-halka-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 28

## Kırmızı testin istediği

| # | Test | Ne istiyor |
|---|---|---|
| K1 | `turns while it waits its turn, the same as while it downloads` | İzin almamış karo da `.wf-spinner` gösteriyor |

## Değişiklik

`TileImage.jsx`, tutucunun seçildiği yer. Bugün iki şeye birden bakıyor:

```jsx
{state !== "here" && (granted && state === "waiting" ? … : …)}
```

Yarın yalnız birine:

```jsx
{state !== "here" && (state === "waiting" ? … : …)}
```

**`granted` koşuldan düşüyor**, ve o an dönmesinin sebebini anlatan yorum da onunla birlikte
düşüyor — anlattığı şey artık olmuyor. Yerine bekleyenin de dönmesinin sebebi geliyor.

Değişkenin kendisi kalıyor: `granted` fotoğrafın `src`'sini ve süreyi hâlâ yönetiyor. Düşen yalnız
çizimdeki payı.

### Verilen karar

**Ayrı bir "sırada" görünümü bırakılmıyor.** Daha soluk bir halka ya da daha yavaş bir dönüş
düşünülebilirdi; alınmadı. Kullanıcının aldığı karar iki hâlin **aynı** görünmesi, ve bir ara ton
hem o kararı hem de sadeliği yarım bırakırdı.

## Doğrulama

`npm test --prefix queen-editor/frontend` → **553 passed.** Bir kırmızı yeşile döner, 552 yerinde
kalır. Özellikle şu üçünün yeşil kalması gerekiyor, çünkü aynı bloğu okuyorlar: *inen karo döner*,
*gelmeyen karo sessiz kutu*, *gelen fotoğraf tutucuyu düşürür*.

`python -m pytest queen-editor -q` → **711 passed.**

Ekranda görülecek olan: galeri açılınca **her** boş karo dönüyor, fotoğraflar teker teker ve baştan
sona oturuyor.

## Kapsam dışı

- **Test dosyasına dokunulmuyor.**
- **Kuyruk, sıra, süre, gizli fotoğraf** — hiçbiri değişmiyor.
- **`dist` yine aynı commit'e giriyor.**
