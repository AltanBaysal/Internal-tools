# Madde 194 · ek · uygulama turu — şeridin sırası

**Kaynağı:** [test turu](2026-09-07-queenagent-m194-serit-sirasi-testler-design.md), `3cb8dff`'de
2 kırmızı.

---

## Tek dosya, tek fonksiyon

`ChatScreen.jsx`'in `LiveStrip`'i. Üç parça aynı, sırası başka:

```
<span>round {round}/{of} · {tokens} tokens · </span>
<span class="msg__spinner" />
<span>{word}…</span>
```

Kelime kendi `<span>`'ine giriyor. Eskiden çıplak bir metin düğümüydü; spinner'ın *bir sonraki
kardeşi* olarak sınanabilmesi için bir öğe olması gerekiyor, ve düzenin kilitlenmesinin tek yolu o.

## Metnin sonundaki boşluk

`· ` — boşluk `textContent`'te var, ekranda yok. Flex öğesinin sonundaki boşluk sıkıştırılıyor, ve
parçalar arasındaki mesafeyi `gap: 7px` zaten veriyor. Kazanılan şey: okunan cümle `round 4/16 ·
12.3k tokens · Ideating…`, yani testin gördüğü şey ile kullanıcının gördüğü şey aynı cümle.

## CSS'e dokunulmuyor

`.msg__stamp--live` bir flex satırı, ve öğelerin sırası markup'ın. `.msg__spinner` de yerinde: ne
döndüğü ne de nasıl göründüğü değişiyor.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 2 kırmızı kapanır — **890 · 621 · 739 · 591**. Sonra
`npm run build --prefix queen-agent/frontend`, ve `dist` bu commit'e girer.
