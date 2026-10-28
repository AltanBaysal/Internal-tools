# v14 · Görev 20 — Sekmelerin ayrılması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-20-sekme-ayrimi-testler-design.md) ·
kırmızı commit `dadc9c5` (484 testin 2'si kırmızı).

Tek dosya, tek bileşen: `PhotoDetail.jsx` içindeki `LayerTabs`. Değişen üç satır ve iki yorum.

## 1 · Şerit boşluk veriyor

```js
const STRIP = { position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                display: "flex", gap: 8, zIndex: 2 };
```

Boşluk şeridin `gap`'i. Düğmelerin marjı olsaydı üç düğmeye yazılan bir değerden iki boşluk
çıkarmak gerekirdi — `gap` iki boşluğu bir kere söylüyor.

Şerit `data-strip` alıyor: ölçü şeridin kendisine ait, testin onu adıyla bulması lazım. Evin
alışkanlığı (`data-corner`, `data-field`, `data-owns` aynı sebeple duruyor).

## 2 · Çakışma kalkıyor

```js
                         // Joined, not three separate pills: one control with three states.
                         marginLeft: index ? -1 : 0 }}>
```

Satır ve yorumu gidiyor. `index` de gidiyor — `map`'in ikinci parametresini okuyan başka kimse yok.

Yerine yeni bir yarıçap **konmuyor**: `wf-stroke` sınıfı her düğmeye `--r-md` veriyor ve hep
veriyordu. Görünmesini engelleyen tek şey iki yuvarlak köşenin aynı pikselde buluşmasıydı.

## 3 · Şeridin yorumu düzeliyor

Bugün:

> *"Madde 73's strip: three joined buttons over the stage."*

**joined** artık doğru değil ve bir yorum yalnız bugün doğru olanı söyler. Cümlenin ikinci yarısı
(*"sahip olmadığı katmanın sekmesi gizlenmez, pasif kalır"*) olduğu gibi kalıyor — o hâlâ doğru ve
fark 85'in son cümlesi de aynı şeyi istiyor.

## Değişmeyen

- Açık sekmenin rengi ve çerçevesinin rengi (**32. karar**) — bu madde geometriden ibaret.
- Pasif sekmenin `disabled`'ı, opaklığı, `aria-current`, ikonlar, `onOpen`.
- Sahne, sağ sütun, oynatıcı, silme düğmeleri.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 484. `dist` aynı commit'te derleniyor.
