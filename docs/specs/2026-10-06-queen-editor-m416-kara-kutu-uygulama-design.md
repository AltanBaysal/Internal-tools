# Madde 416 — DeepSeek'in kara kutusu, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 416 · v9-3a · **Tur:** 2/2 — kod.
**Testler:** [m416 test turu](2026-10-06-queen-editor-m416-kara-kutu-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler.

## Yaklaşımlar

1. **Seçilen — istemcinin üstünde ayrı bir kutu, `services/deepseek/box.py`.** İstemci bugünkü gibi
   tek istek atar ve hatayı sunucunun kendi metniyle fırlatır; kutu onu en çok beş kez sorar, ve
   cevabı ya da son hatanın metnini bir `Answer` olarak döner. Her dosyanın tek işi var: bir deneme
   `client.py`'nin, kaç deneme ve ne dönüleceği `box.py`'nin. İstemcinin testleri olduğu gibi kalır.
2. *Elendi —* denemeleri `DeepSeekClient.complete`'in içine koymak: bir sınıf iki iş, istemcinin tek
   isteği anlatan testleri yeniden yazılır, ve 418'in kontrol isteği taşımanın içine girer.
3. *Elendi —* denemeleri yazarlara koymak (`prompt_writer.py`): kutu bir özelliğin içinde kalır, ve
   420'nin agent'ı aynı kutuyu ikinci kez yazmak zorunda kalır. Kullanıcı DeepSeek'e giden her isteğin
   **tek** bir kutudan geçmesini istedi.
4. *Elendi —* `policy.MAX_ATTEMPTS`'ı büyütmek: kullanıcı döngünün üçünü bıraktı *("abi şimdili
   karıştıma 15 kere denesin sıkıntı yok ya vazgeçtim")*.

## Kutunun biçimi — 418 ve 419 nereye oturur

- **`Box(client).ask(system, text="", images=())` → `Answer(text, failed=False)`.** `ask`, istemcinin
  `complete`'iyle aynı soruyu alır. `Answer` donmuş bir dataclass.
- **Her hata yeniden denenir** — `except Exception`: istemcinin üç `RuntimeError`'ı, `requests`'in
  bağlantı ve zaman aşımı hataları, ve anahtar yokken `NotConfigured`. Anahtarsızlık da sayılır,
  çünkü istemci onu hiçbir şey göndermeden reddediyor — beş denemesi bedava —, ve tek kural bir hata
  listesinden basit. Kutu hiç fırlatmaz: döngü kuran bir çağıran — agent — kırılmasın diye (v9-3).
- **Beşi de olmazsa** `Answer(son hatanın str'i, failed=True)`. Sebep eklenmez, sayı eklenmez.
- **418:** kontrol, `try`'ın içinde, `complete`'in cevabından sonra ikinci bir `complete` olur; ret
  bir hata gibi sayaçtan düşer, ve beşi de retse metin *"Model hata döndü, farklı şekilde dene."*
- **419:** araçlı istek kutuya ikinci bir yol olarak girer, aynı beşlik döngüden geçer; `Answer`
  ret mi teknik mi olduğunu söyleyen bir alan kazanır. Bugün o alanı okuyan yok, o yüzden yok.

## Dosyalar

### `backend/services/deepseek/box.py` — yeni

`TRIES = 5`, `Answer`, `Box`. Modül belgesi kutunun sözünü ve neden fırlatmadığını söyler.

### `backend/services/deepseek/client.py`

Yalnız modül belgesi: bir deneme bu dosyanın, yeniden denemek `box.py`'nin.

### `backend/features/photo_generation/data/prompt_writer.py`

- **`_prompt(answer)`** — başarılıysa metin; başarısızsa kutunun metniyle `RuntimeError`. Döngünün
  bugünkü hata yolu `Exception`'ı yakalıyor, ve `RuntimeError` karenin hatası değil
  (`policy.is_frame_fault`): üç denemeden sonra üretim durur, iş borçlu kalır.
- Üç yazar `self._queen_ai.ask(...)`'ı sorar ve `_prompt`'tan geçirir; kurucunun argümanı
  `queen_ai`. Söyledikleri — talimat, sözler, resimler — aynen.
- Modül belgesi: her yazar kutudan sorar.

### `backend/main.py` — yalnız 106–109. satırlar

`_queen_ai = Box(DeepSeekClient(...))`; içe aktarma `client`'ınkinin altında; yorum kutuyu anar.
Dosyanın sonuna — 417'nin bağlayacağı yere — dokunulmaz.

## Bir sonuç, açıkça

Zaman aşımı deneme başına 120 sn (`config.DEEPSEEK_TIMEOUT`). Hiç cevap vermeyen bir sunucu artık
üretimi en çok 15 × 120 sn'de, yarım saatte durdurur; bugün üç denemede, altı dakikada. Kullanıcı 15
denemeyi bunu bilerek seçti *("15 kere denesin sıkıntı yok")*; sayı değişmez.

## Bilinçli olarak yapılmayan

- Denemeler arasında bekleme, deneme sayısının ayarı, denemelerin günlüğü yok.
- `Answer`'a 419'un alanı, kutuya 418'in kontrolü girmez.
- `policy.py`, `run_loop.py`, `ports.py`, `config.py`, ekran, `dist` ve yol haritası değişmez.
