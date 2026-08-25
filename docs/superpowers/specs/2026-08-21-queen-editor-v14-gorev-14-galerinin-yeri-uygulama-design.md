# v14 · Görev 14 — Detaydan dönünce galerinin yerinde durması · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-14-galerinin-yeri-testler-design.md) —
kararlar orada verildi ve commit edilmiş altı test onları tarif ediyor.

## Değişen dosyalar

| Dosya | Ne kazanıyor |
|---|---|
| `shared/shown_pictures.js` | **yeni** — ekrana gelmiş resimlerin kümesi |
| `features/photo_generation/useKeptScroll.js` | **yeni** — kayma yerinin belleği ve kancası |
| `features/photo_generation/TileImage.jsx` | iki kapıyı atlama |
| `features/photo_generation/ProjectScreen.jsx` | kancanın takılması, `data-scroll` |

### 1 · Kayma yeri

Kanca üç satır: kutuyu kurulurken hatırlanan yere koyuyor, sökülürken bulunduğu yeri yazıyor.

- **Yerleşim etkisi.** Geri koyma boyamadan önce olmalı; sıradan bir etki galerinin bir kare
  tepede çizilip sonra zıplamasına izin verirdi.
- **Düğüm gövdede yakalanıyor.** Temizlik anında `ref`'in hâlâ dolu olup olmaması React'ın işi;
  yakalanmış bir düğüm o soruyu ortadan kaldırıyor.
- **Yazma anı sökülme.** Her kaydırma olayında değil — ziyaret başına bir yazma, ve kısma
  makinesi yok.
- **`project` bağımlılığı.** Aynı ekran proje değiştirebiliyor (`useGeneration` bunu zaten
  biliyor); o zaman eski projenin yeri yazılıp yeninin yeri okunuyor.

Kanca boş `ref` için koruma taşımıyor: kutuyu takmak sözleşmenin kendisi ve `ProjectScreen` onu
koşulsuz çiziyor. Takmayı unutan bir çağıran orada, bir daha, sessizce değil.

### 2 · Bir kez gelmiş resim

`TileImage` doğarken tek bir soru soruyor: bu URL bu oturumda ekrana geldi mi? Cevap evetse **iki
kapı da** atlanıyor — gözlemci hiç kurulmuyor ve kuyruktan bilet istenmiyor; `src` ilk render'da
yerinde.

Bilet **istenmemesi** önemli: çizilmiş ama yine de sırada duran bir karo, gerçekten bekleyen bir
karonun turunu yerdi.

Küme yalnız `onLoad`'da büyüyor. `onError` yalnız bileti bırakıyor — ekrana gelmemiş bir şeyin
hatırlanacak hâli yok, ve bir sonraki kurulumda yeniden denenmesi doğru olan.

### 3 · Kutunun işareti

`data-scroll`, `data-tile` / `data-check` / `data-veil` ile aynı âdet: ekranın kendi parçalarını
biçimlerinden değil adlarından bulmak.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor, yol haritası 14/31 oluyor.
