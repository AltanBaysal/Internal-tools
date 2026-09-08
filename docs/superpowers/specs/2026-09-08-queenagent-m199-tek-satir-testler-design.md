# Madde 199 · test turu — şerit ve kalem tek satırda

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 199.

---

## Bugün ne oluyor

Bubble'ın altında iki şey duruyor ve **ikisi de kendi satırında**: 195'in sürüm şeridi
*(`.versions`)* ve 197'nin kalemi *(`.msg__edit`)*. İkisi de `.msg`'in doğrudan çocuğu, `.msg` ise
bir sütun — sütun her çocuğa bir satır verir. Kusur değil, hiç yan yana getirilmemiş olmaları.

## Ne kurulacak

- Bubble'ın altında **tek bir satır** — solda şerit, sağında kalem.
- **Bubble o satırın içine girmiyor.** 197'nin kapattığı hizalama kusuru bubble'ın sarmalanmasıydı;
  bu satır yalnız altındaki iki notu tutuyor.
- **Boşken doğmuyor:** ne kalem ne şerit varsa satır da yok.
- **Düzenleme açıkken şerit kalıyor, kalem çekiliyor** — 197'nin kuralı değişmiyor.

## Testler

### `ChatScreen.test.jsx`

1. **şerit ve kalem aynı satırda** — iki sürümlü bir mesajda `.msg__foot` hem `.versions`'ı hem
   `Edit message`'ı taşıyor.
2. **şerit önce, kalem sonra** — satırın ilk çocuğu şerit. Ters dizilseydi kalemin yeri şeridin var
   olup olmamasına göre kayardı.
3. **tek sürümlü mesajın satırında yalnız kalem** — `.msg__foot` var, `.versions` yok.
4. **cevabın altında satır yok** — boş bir satır sütunun boşluğunu büyütmekten başka bir şey
   yapmazdı. *(Uygulamadan önce de yeşil: ortada `.msg__foot` diye bir şey yok. Nöbetçi olarak
   yazılıyor — uygulamanın satırı boşuna doğurmadığını tutan şey bu.)*
5. **düzenlenirken satırda yalnız şerit** — kalem çekiliyor, şerit duruyor.

### `workspace.css.test.js`

6. **satır bir satır** — `.msg__foot` `display: flex` ve `align-items: center`.
7. **şerit kendi payını taşımıyor** — `.versions`'ta `margin-top` yok. Satırın içine girdiği anda o
   pay sütunun boşluğunun üstüne binerdi.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Ön yüzde **6 kırmızı** — `.msg__foot` diye bir şey yok, ve
şerit hâlâ kendi `margin-top`'unu taşıyor. 4 numara baştan yeşil ve öyle olduğu yukarıda yazılı.
Arka uç ve `queen-editor` kımıldamıyor: **933 · 739 · 591** yerinde.
