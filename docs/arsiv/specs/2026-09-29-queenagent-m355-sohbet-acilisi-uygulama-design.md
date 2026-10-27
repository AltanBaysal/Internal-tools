# Madde 355 — Sohbet açılırken açılmış gibi görünür · uygulama turu

**Kaynak:** [yol haritasının 355'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2l);
tasarım: `queen-agent-v3`'ün 194'ü. Testler
[test turunda](2026-09-29-queenagent-m355-sohbet-acilisi-testler-design.md) yazıldı ve kırmızı
commit'lendi; bu tur yalnız onları yeşile çeviren kodu yazar.

**Kullanıcıdan gereken:** hiçbir şey.

## Yaklaşım

İki yol vardı:

1. **Tek ağaç** — `ChatScreen` kaydı gelmemiş sohbette de aynı `chat-layout`'u çizer; yalnız
   sütunun içi değişir (kayıt varsa mesajlar ve tur, yoksa spinner), başlık `loadingTitle`'a düşer,
   kutu ve seçiciler kapalıdır. Yazma kutusu ve dosya paneli tek yerde yazılı kalır.
2. **Ayrı erken dönüş** — açılış çerçevesi kendi JSX'iyle. Kutunun ve panelin prop'ları iki yerde
   yazılır; 358 (model seçicisi kalkar) ve 352 (dolu sohbetin bildirimi) iki yeri değiştirmek zorunda
   kalır.

**Seçilen: 1.** Tasarım da aynı `chatScreen()`'i iki hâlde çağırıyor. Bedeli, sütunun bugünkü
içeriğinin bir koşulun içine girmesi (girinti değişir).

## Değişenler

- **`ChatScreen.jsx`**
  - `if (!chat)` dalı yalnız `missing` için kalır: `← back` ve `That chat does not exist.`
    Parlayan iskelet ve `Skeleton` import'u gider.
  - Yeni prop `loadingTitle`: kaydı gelmemiş sohbetin başlığı; yoksa boş.
  - Sütun: `chat` varsa bugünkü içerik aynen; yoksa yalnız
    `<div className="chat__spinner"><Spinner /></div>` — cevabı hâlâ gelen sohbete dönülse bile
    açılış bir tur çizmez (tasarım: yüklenen kayıt tur çalıştırmaz).
  - Kutu: `disabled={!chat}`; seçicilere de `disabled={!chat}`; ölçüm `chat?.context`.
  - Kutuya `key={chat ? "read" : "loading"}`: çerçeve açılışta da durunca React aynı kutuyu tutar,
    ve bir sohbette kalan cümle ötekine geçer. Anahtar kutuyu açılışta ve kayıt gelince yeniden
    doğurur — bugün açılış dalının kutuyu sökmesiyle aynı sonuç, tasarımın *start afresh*'i.
- **`Composer.jsx`** — `disabled` prop'u yazı alanına gider. Gönder düğmesi zaten boş taslakta
  kapalı; kapalı alana yazılamadığından ayrıca kapatılmaz.
- **`ModePicker.jsx`, `SkillPicker.jsx`, `ModelPicker.jsx`** — `disabled` prop'u düğmeye gider.
- **`App.jsx`** — `ChatScreen`'e `loadingTitle`: `projectChats`'te adresin sohbetinin satırı.
- **`workspace.css`**
  - `.chat__spinner { display: flex; justify-content: center; padding: 40px 12px; }` —
    `.file-list__spinner`'ın yanında.
  - `.composer__input:disabled, .picker:disabled { cursor: default; opacity: 0.4; }` — kit'in
    kuralı, yorumu nedenini söyler.
  - `.skeleton--message` kuralı kalkar: tek kullanıcısı gitti.

## Dokunulmayan

- `APP-BUGS.md` 30 (404 dışı okuma hatası) bugünkü gibi çizilmez: hata kartı açılışta çıkmaz,
  spinner döner. Tasarım çizmiyor, madde istemiyor.
- Açılışta bir tur hâlâ akıyorsa gönder düğmesi `⏹` olarak durur (bugünkü `running`); tasarımın
  kutusu bu durumu hiç görmüyor, ve durdurmak o sohbetin kendi turunu durdurur. Ayrıca kapatılmaz.
- CODE-STANDARD'ın hareket paragrafı (379): yeni animasyon yok, 340'ın halkası.

## Nasıl görülür

Dört satır: queen-agent'ın ön yüzü yeşile döner, öteki üç süit aynı. Tarayıcıda: kenar çubuğundan bir
sohbet açılırken başlık satırın adıyla, dosya paneli ve soluk, kapalı kutu yerinde; mesajların
yerinde küçük halka döner; `← back` yok. Olmayan bir sohbetin adresinde `← back` ve
`That chat does not exist.` kalır.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m355-sohbet-acilisi-uygulama-plan.md).
