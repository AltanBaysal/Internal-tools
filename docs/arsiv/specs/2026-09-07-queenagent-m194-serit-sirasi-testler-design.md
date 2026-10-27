# Madde 194 · ek · test turu — şeridin sırası tersine döner

**Kaynağı:** kullanıcı kararı, 7 Eylül. Şerit `deb0a9e`'de kapandı; değişen yalnız satırın sırası.

---

## Bugün ne var, ne isteniyor

```
bugün:     ⟳ Ideating… · round 4/16 · 12.3k tokens
isteniyor: round 4/16 · 12.3k tokens · ⟳ Ideating…
```

Yol haritasının çizimi spinner'ı başa koyuyordu; kullanıcı sonu istiyor. **Karar yerinde:** satırın
taşıdığı iki bilgi *(kaçıncı raunt, ne kadar büyüdü)* öne geçiyor, dekoratif olan sona. Spinner'ın
işi kımıldamak, ve nerede durduğu kımıldamasını değiştirmiyor — yol haritasının *"donmuş
görünmemek"* gerekçesi ikisinde de aynı ölçüde geçerli.

## Ne değişiyor

`LiveStrip`'in üç parçası aynı, sırası başka: **metin, spinner, kelime.**

Metin `· ` ile bitiyor. Boşluk `textContent`'te var, ekranda yok — flex öğesinin sonundaki boşluk
sıkıştırılıyor ve aradaki mesafeyi zaten `gap` veriyor. Yani okunan cümle `round 4/16 · 12.3k
tokens · Ideating…`, ve ekranda ikisi arasında bir spinner duruyor.

CSS'e dokunulmuyor: `.msg__stamp--live` zaten bir flex satırı, ve öğelerin sırası markup'ın.

## Testler

`ChatScreen.test.jsx`'te iki satır:

1. **satırın tamamı** — bugün `/^[A-Z][a-z]+ing… · round 4\/16 · 12\.3k tokens$/` bekliyor;
   tersine dönüyor. Tek satır, aynı ayraçlar, yeni sıra.
2. **spinner sayıların arkasında** *(yeni)* — düzenin kendisini kilitleyen tek şey bu.
   `textContent` bir düzen kanıtı değil: aynı harfler farklı bir markup'tan da çıkabilir. Spinner'ın
   bir önceki kardeşi jeton sayısını taşıyor.

Öteki üç şerit testi `toContain` ile bakıyor ve sıradan bağımsız; kımıldamıyorlar, ve bilerek —
sordukları şey sıra değil.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` ön yüzünde 2 kırmızı; arka uçlar ve
`queen-editor` kımıldamıyor — **890 · 739 · 591** yerinde.
