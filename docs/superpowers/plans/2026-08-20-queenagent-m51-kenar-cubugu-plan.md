# Madde 51 — Sol kenar çubuğu tek düğmeyle kapanır · Plan (iki tur)

**Madde:** [v3 yol haritası Madde 51](2026-08-18-queenagent-v3-roadmap.md) ·
**Kaynak:** [test bulguları, bulgu 3](../research/2026-08-18-queenagent-test-bulgulari.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Ayrı tasarım belgesi yok: karar zaten yol haritasında, ve rayın (Madde 20, 50) katlanması bu ekranda
aynı sorunun çözülmüş hâli.

---

## Karar

claude.ai davranışı: **sürüklenmez**. Tek düğme kapatır, aynı düğme açar.

Rayın kuralı burada da geçerli — katlı bir çubuk gizlenmiş değil, **yerine bir şerit geçmiş**
çubuktur. Şeritte tek bir şey durur: onu geri açan düğme. Proje adları, sohbet başlıkları ve
Settings gider, çünkü hepsi okunacak kadar yer isteyen metinler; ikon hâlleri yok ve uydurmak bu
maddenin işi değil.

Düğme açıkken markanın yanında, kapalıyken şeridin kendisidir — "aynı düğmeyle açılır" ancak düğme
kapalıyken de duruyorsa doğru olur.

Durum `App`'te, `railCollapsed` ile aynı sebeple: oturum boyu yaşar ve adres değiştikçe yeniden
kurulan bir bileşende duramaz.

## Tur 1 — Testler (kırmızı commit)

`Sidebar.test.jsx`:

1. çubuk kendini gizleyen bir düğme taşır
2. düğme kendi gizlemez, gizlemeyi ister (`onToggle` çağrılır)
3. katlıyken şeritten başka bir şey kalmaz — proje adları, Recent chats ve Settings yok
4. katlıyken aynı düğme oradadır ve adı artık göstermeyi söyler
5. katlı olduğunu sınıfında söyler (`sidebar--collapsed`)

`App.test.jsx`:

6. çubuğu kapatmak proje adlarını götürür, açmak geri getirir, ve kapalılık adres değişince durur

`workspace.css.test.js`:

7. katlı çubuk bir şerittir ve oraya çubuğun kendi geçişiyle varır

### Beklenen kırmızı

Yedisi de kırmızı: bugün ne düğme var ne katlı hâl.

## Tur 2 — Uygulama (yeşil commit)

- **`Sidebar.jsx`** — `collapsed` ve `onToggle` alır; katlıyken yalnız düğmeyi çizer.
- **`App.jsx`** — `sidebarCollapsed` durumu ve düğmenin bağlandığı yer.
- **`workspace.css`** — `.sidebar--collapsed` şeridi, `.sidebar__fold` düğmesi, `.sidebar`'a genişlik
  geçişi.

## Bilerek yapılmayan

- Dar kabukta kendiliğinden katlanma yok: Madde 33'ün adımları çubuğu zaten daraltıyor, ve bu madde
  kullanıcının kendi düğmesini istedi.
- Kapalı şeritte ikon yok — çubuğun satırları metin, ve ikon uydurmak ayrı bir tasarım kararı.
