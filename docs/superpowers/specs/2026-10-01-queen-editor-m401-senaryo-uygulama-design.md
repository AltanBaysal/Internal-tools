# Madde 401 — Karenin senaryosu kartta görünür, implementasyon turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m401 test turu](2026-10-01-queen-editor-m401-senaryo-testler-design.md),
`82c50959` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Sunucu değişmez

Her kart `scene`'i 397'den beri taşıyor *(`list_frames.py` — `""` senaryosuz kartta)*, ve
`useGeneration` kartları olduğu gibi veriyor. Sayfa `frame.scene`'i okur.

## Dört dosya

**`glyphs.jsx` — `ScenarioGlyph`.** Tasarımın `scenario` ikonu: bir sayfa, içinde üç satır — senaryo
bir resim değil, yazılı bir cümle. Dosyanın öteki ikonları gibi `Glyph`'in içinde, adı `scenario`.

**`PhotoDetail.jsx`:**

- **Hâl sayfada.** `const [sceneShown, setSceneShown] = useState(false);` — `unfolded`'ın yanında.
  Kare değişince önceki kareye ait olanı temizleyen effect ona dokunmaz: basış kullanıcınındı,
  karenin değil — tasarımdaki `senaryoAcik` gibi. Effect'in yorumu buna göre düzelir.
- **Düğme şeridin içinde.** `LayerTabs` iki prop daha alır — `sceneShown`, `onScene` — ve üç sekmenin
  ardına tasarımın `.sen-sep`'ini ve `.sen-btn`'ini çizer: 1px genişliğinde, `--border` renginde,
  şerit boyu bir çizgi *(yanlarda 2px)*; sonra `aria-pressed` taşıyan bir `<button>` — zemin ve
  çerçeve yok, `4px 10px` padding, ikonla söz arası 4, renk açıkken `--accent`, kapalıyken `--ink-3`,
  renk geçişi `.12s`. İçinde `ScenarioGlyph` ve `<Mono size={10}>Senaryo</Mono>` — sekmelerin söz
  boyu ve ikon boyu *(10)*.
- **Kart, dosyanın küçük bileşenlerinden biri:** `ScenarioCard({ scene, lifted })`, `data-scenario`
  taşıyan bir `div` — yazı kutusu değil. Ölçüleri tasarımın `.sen-card`'ı: `absolute`, sol, sağ, alt
  12, `z-index` 3, zemin `rgba(10,8,7,.72)`, yazı beyaz, köşe 4, padding `8px 12px`, yazı 12.5 /
  1.5, ortalı, gölge `0 1px 3px rgba(0,0,0,.6)`, `pointer-events: none`. `lifted` iken alt 40
  *(`.sen-onscene`)*. Senaryo yoksa *"Bu karenin senaryosu yok"*, yazı `rgba(255,255,255,.55)`.
- **Kart resmin kendi kutusunda,** sahnenin her dalında bir kez: fotoğrafı tutan `FRAMED` kutusu
  *(üretilmiş kare, ve üstünde katman üretilirken)*; oynatıcının sahnesi *(`lifted`)*; kuyruktaki,
  üretilen ve hata alan karenin `.wf-img` yer tutucusu — tasarımın `square()`'i. `.wf-img` zaten
  `position: relative` *(`vendor/styles.css`)*, `FRAMED` de. Kapalıyken hiçbir şey çizilmez.
  Dallar tek bir yardımcıdan alır: `const scenarioCard = (lifted) => sceneShown && <ScenarioCard …/>`.

**`LayerPlayer.jsx` — `children`.** Oynatıcı ona verileni sahnenin (`data-scene`) içine, en sona
koyar: kart ölçüsünü sahnenin kendi kenarlarından alsın diye. Başka bir şey değişmez.

**`frame_status.jsx` — `Rendering`'e `children`.** Yer tutucu ona verileni halkanın ardına koyar.
Galeri onu çocuksuz kullanıyor, ve orada bir şey değişmez.

## Bilerek yapılmayan

- **`ust`, `kose`, ve tasarımın `senaryoYeri` şeridi** — kullanıcı `alt`'ı seçti.
- **Tasarımın `?acik=` ve `?kare=` adresleri** — tuvalin kendisi için.
- **Düğmeye basınca videonun durması** — tasarımda `draw()` sayfayı yeniden çizdiği için oluyor, ve
  tasarımcı onu ayrı bir dala değmez buluyor. Burada kartın açılıp kapanması oynatıcıyı yeniden
  kurmuyor; video oynamayı sürdürür.
- **Yer tutucunun soluk olması:** kuyruktaki karenin kutusu `.45` saydam, ve kart onun içinde —
  tasarımda da `square()` öyle. Kart da soluk görünür.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. `dist` bu turda yapılmaz: dalga birleşince bir kez
yapılıyor *(koşuyu yöneten oturumun kararı)*.
