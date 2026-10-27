# Madde 399 — Karenin bilgileri açılır kapanır bir bölümde, implementasyon turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m399 test turu](2026-09-30-queen-editor-m399-ayrintilar-testler-design.md),
`83211eb3` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Tek dosya: `PhotoDetail.jsx`

**Hâl sayfada.** `const [unfolded, setUnfolded] = useState(false);` — açık sekmenin (`open`) yanında.
Tasarımda da `ayrintilarAcik` sayfanın kendi değişkeni, `senaryoAcik`'in yanında. Kare değişince
önceki kareye ait olanı temizleyen effect ona dokunmaz: basış kullanıcınındı, karenin değil. Oklar
sayfayı açık tuttuğu için hâl yürür; galeriden yeni açılan sayfa kapalı başlar.

**Bölüm, dosyanın küçük bileşenlerinden biri** — `Field`, `BoxLabel` gibi: `Details({ shown, onToggle,
children })`.

- Dış kutu `data-group="details"`, dikey, gap 12 *(tasarım: `.ayrintilar`)*.
- Başlık bir `<button>`: `aria-expanded={shown}`, zemin ve çerçeve yok, padding 0, tam genişlik,
  yazıyla ok arası 6, renk `--ink-3` *(tasarım: `.ayrintilar-baslik` ve `.label`)*. Yazı sütunun
  öteki etiketleri gibi: `<Mono size={10} style={LABEL}>Ayrıntılar</Mono>`.
- Ok, kitin `Icon.Down`'ı — tasarımın `g.down`'ıyla aynı çizgi —, `data-caret` taşıyan bir `span`'in
  içinde; açıkken `rotate(180deg)`, dönüş `transform .12s` *(tasarım: `.ayrintilar-ok`)*.
- Açıkken altında satırlar, bilgi grubunun sarma kuralıyla.

**Sarma kuralı bir kez yazılır:** `FACTS = { display: "flex", flexWrap: "wrap", columnGap: 24,
rowGap: 16 }` — üstteki bilgi grubu ve bölümün satırları ikisi de onu kullanır *(tasarımda ikisi de
`.info`)*.

**Sütun üç parça:** `data-group="info"` yalnız *Sıra* — 408 *Üretim süresi*'ni onun yanına koyacak;
`Details`'ın içinde *Dosya adı*, *Model*, *LoRA*, *Üretim modu*, bugünkü koşulları ve yorumlarıyla,
yerlerinden taşınmış; `data-group="production"` değişmez.

**Yorumlar doğru kalır:** kare değişince çalışan effect'in yorumu *"the open tab is the one thing that
stays"* diyor; artık bölüm de kalıyor, cümle ona göre düzelir.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. `dist` bu turda yapılmaz: dalga birleşince bir kez
yapılıyor *(koşuyu yöneten oturumun kararı)*.
