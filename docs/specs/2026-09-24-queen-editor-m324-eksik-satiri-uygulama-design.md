# Madde 324 — Üretimi ne durduruyorsa basmadan söyleniyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-b` *(Kol B)* · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m324 test turu](2026-09-24-queen-editor-m324-eksik-satiri-testler-design.md),
`8adc8de5`. Havuzun kablosu için koordinatörün seçimi: havuzun her cevabı ekrana çıkıyor, ekran
tutuyor, yan panel video paneline indiriyor *(test spec'indeki seçenek 1)*.

## Sunucu

- **`list_producers.py`** — video satırı `reads_references` taşıyor: `video_model == "h3"`. Satırın
  `model`'i gibi yalnız videoda; fotoğraf ve ses satırı değişmiyor. Karar `groups_for`'un ve
  `video_model_name`'in okuduğu aynı seçimden — oturumda H3 kuruluysa referans okuyan odur.
- **`queue_references.py`** — yalnız boş havuz cümlesi: `Havuzda referans yok — önce en az bir
  referans ekle.` Çevresindeki satırlara dokunulmuyor; 321 onları öteki kolda değiştiriyor.

## Ekran

- **`ReferencePanel.jsx` — olabildiğince az.** Yeni prop `onPool`, varsayılanı hiçbir şey yapmıyor.
  Durumun kendi setter'ı `showPool` adını alıyor, ve `setPool` artık ikisini birden yapan bir
  fonksiyon: havuzu çiziyor ve cevabı `onPool`'a veriyor. Yani dört çağrı yeri *(ilk okuma, yükleme,
  sıralama, silme)* hiç değişmiyor — 321 silmeyi, 322 sıralamayı öteki kolda yeniden yazıyor, ve
  onların satırlarına dokunulmuyor. Değişen yalnız bileşenin ilk satırları. **Neden etkide değil:**
  `useEffect(…, [pool])` bekleme yerine konan boş havuzu da *(`{ references: [], limits: {} }`)*
  ekrana verirdi, ve satır her açılışta bir an "havuz boş" derdi. Buraya yalnız sunucunun cevapları
  gelir.
- **`ProjectScreen.jsx`** — `pool` durumu, `null`'dan başlıyor; `ReferencePanel`'e `onPool={setPool}`,
  `SidePanel`'e `pool`. Havuz kapanınca *(Kareden, `Referansları kapat`)* cevap duruyor: o arada bu
  ekranda havuzu değiştiren bir şey yok, ve havuz yeniden açılınca kendi okumasını yapıp tazeliyor.
  `setPool` React'in kendi setter'ı, yani hiç değişmiyor — `ReferencePanel`'in ilk okuması onu ilk
  çizimde yakalasa da doğru yere yazıyor.
- **`SidePanel.jsx`** — `pool`'u alıyor, `LayerPanel`'e geçiriyor. Tek başına çizilen bir sütunda
  yok, ve "cevap yok" demek.
- **`LayerPanel.jsx`:**
  - İki cümle, `NO_VARIANTS`'ın yanında: `H3_ONLY` ve `NO_REFERENCES`. İkisi de sunucunun cümlesi
    *(`queue_references.py`)*, harfi harfine.
  - `poolRefusal(producer, pool)` — satırın cümlesi ya da `null`, uygulamanın sırasıyla: üretici
    kurulu ve `reads_references` değilse `H3_ONLY`; havuzun cevabı varsa ve boşsa `NO_REFERENCES`.
    Cevap vermemiş olan *(üretici satırı yok, `pool` yok)* hiçbir şey söylemiyor.
  - Satır yalnız Referanstan'da: varyant satırının altında, düğme bloğunun üstünde, kendi başına bir
    `Note` — tasarımın `#poolMissing`'i gibi 12px, `--ink-2`, ortalı.
  - Düğme: bugünkü üç kilide *(istek yolda, üretici eksik, başka projede üretim)* Referanstan'da iki
    kilit ekleniyor — satır bir şey söylerken, ve kutu `trim()` sonrası boşken. Kareden'inki
    değişmiyor.
  - Düğmenin üstündeki yorum artık Kareden için doğru: "boş alan basınca cevaplanır" Kareden'in
    kuralı; Referanstan eksiğini basmadan söylüyor. Yorum ikisini de söyleyecek şekilde yazılıyor.
  - `refusalOf` değişmiyor: basışın ilk sorusu hâlâ varyant kutusu, ardından istek sunucuya gidiyor.

**Önizleme, kural değil** *(FOUNDATION 4)*. Satır ve iki yeni kilit sunucunun reddinin önizlemesi;
kapı aynı durumları yine kendisi reddediyor. Satırın göremediği durumda — havuz ya da üreticiler
henüz cevap vermemişse, ya da son referans Drive'dan elle silinmişse — basış gidiyor ve cevap
sunucunun, bugünkü kırmızı kartta.

## Dist

Kolda derlenmez — [yol haritası](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md), *320–324 iki
paralel kolda*: birleşme commit'i bir kez derler.

## Birleşme

`queue_references.py` *(beklenen)*; `ReferencePanel.jsx` *(yalnız bileşenin ilk satırları)*.

## Bitti sayılır

Dört test satırı yeşil — koordinatör koşuyor; kod, spec ve plan tek commit.
