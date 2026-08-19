# Madde 52 — Çatal, kullanıcı gitmişse karar vermez · Plan (iki tur)

**Madde:** [v3 yol haritası Madde 52](2026-08-18-queenagent-v3-roadmap.md) ·
**Kaynak:** [test bulguları, bulgu 15](../research/2026-08-18-queenagent-test-bulgulari.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Bulgu ne diyor

Açılışta liste gelmemişken kenar çubuğundan bir yere gitmek tutmuyor: liste gelince `/` çatalı ilk
projeye `replace` ile gidiyor ve kullanıcının seçtiği adresin üstüne yazıyor.

## Kodun bugün söylediği

`App.jsx`'te karar `atFork = route.view === "root"` ile korunuyor, ve `navigate` adresi **aynı anda**
duruma yazıyor (`useRoute.js`). Yani kullanıcı Settings'e bastığı anda `atFork` yanlış oluyor ve
çatalın hesabı `null` kalıyor.

Bu okuma ile bulgunun anlattığı sıra **çelişiyor**. Bulgu elle turdan geliyor ve orada görülen
gerçek; koddan okunan da gerçek. Hangisinin doğru olduğunu tahmin etmek yerine **test söyler** —
bu maddenin ilk turu tam olarak bunun için var.

## Tur 1 — Test, ve testin verdiği cevap

`App.test.jsx`, iki test:

1. `the fork keeps quiet once the user has gone somewhere` — `/`'da liste **beklemede**; kullanıcı
   Settings'e basar; liste ancak ondan sonra gelir. **Bugün geçiyor.** Koddan okunan doğruymuş:
   `navigate` adresi duruma aynı anda yazdığı için `atFork` tıklamanın hemen ardından yanlış oluyor.
   Test kilit olarak kalır — roadmap'in "nasıl görülür"ü tam olarak bu.
2. `the fork asks the browser where we are, not the render it was built from` — **kırmızı.** Asıl
   tehlike buymuş: bir React etkisi, kendisini planlayan commit'in değerlerini taşır. Liste bir
   hareketle **aynı toplu güncellemede** gelirse, çatal kullanıcının çoktan terk ettiği bir adres
   için karar vermiş olur. Test bunu belirli hâle getiriyor: adres React'e söylenmeden değişiyor,
   yani commit bayat — ve çatal `/settings`'in üstüne `/p/p1` yazıyor.

19 Ağustos'ta paralel bir oturumun `c288d4b`'de "iki oynak iddiayı sabitledi" ve bulgu 15'i teste
yorum olarak yazdığı yer de burası: oynaklığın sebebi bu bayat commit.

## Tur 2 — Uygulama (yeşil commit)

`App.jsx` — çatal, karar verdiği an tarayıcının kendi adresine bakar. Render'dan taşınan değer
bayatlayabilir; tarayıcının adresi bayatlayamaz.
