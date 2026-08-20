# Madde 63 · Tur 2 (uygulama) — Tasarım

**Tur 1 tasarımı:** [2026-08-20-queenagent-m63-test-design.md](2026-08-20-queenagent-m63-test-design.md)
— kararın kendisi, götürdükleri ve dokunulmayanlar orada, ve burada tekrar edilmiyor.

**Bu belgenin konusu:** listeyi kaldırmanın açığa çıkardığı **bir tane** karar.

---

## `FileList` artık asla bir okuyucunun yanında çizilmiyor

Bugün `FileList` iki şeyi okunan dosyaya göre karara bağlıyor:

```jsx
selected={file.name === reading?.name}
onDelete={file.name === reading?.name ? undefined : deleting?.remove}
```

Bu iki satır, listenin okuyucunun yanında durabildiği dünyanın parçasıydı. O dünya kapanıyor:
`FileList`'i çizen tek yer, `if (reading?.name)` dalının **else**'i. Yani o dalın içinde
`reading?.name` tanım gereği yok — iki karşılaştırma da her zaman `false`.

**Kaldırılıyorlar.** Hiçbir zaman doğru olamayacak bir koşul, kodun kendisi hakkında söylediği bir
yalan: okuyan kişi "demek ki okurken de çiziliyor" diye anlıyor, ve öyle değil.

Prop'ların şekli **korunuyor** — `reading` ve `deleting` nesneleri olduğu gibi geçmeye devam ediyor.
Bunları `onOpen`/`onDelete`/`deleteError` diye üç ayrı prop'a açmak daha temiz görünürdü ama bu
maddenin sorduğu soru değil, ve `deleting.error` de listenin içinde çizildiği için sadeleşme
göründüğü kadar sade değil. Değişen yalnız iki ölü karşılaştırma.

## Bunun kıyısında duran, ve bilerek bırakılan

`FileRow`'un `selected` prop'u ve onu boyayan `.file-row--selected` kuralı. Ray artık geçirmiyor,
proje ekranı da hiç geçirmiyordu — yani uygulamada **çağıranı kalmıyor.**

Silinmiyorlar, ve gerekçe tur 1'de yazıldı: `FileRow` sunum bileşeni, bu durum onun kendi testinde
tanımlı, ve bir bileşenin yeteneğini budamak ayrı bir karar. Ama çağıransız kaldıkları iki yerde de
yazılı olmalı ki bir dahaki okuyan "bu nerede kullanılıyor" diye aramasın — biçem testinin yanına
da bu düşülüyor.

Bu, bilerek bırakılan tek artık, ve bırakıldığı burada duruyor.
