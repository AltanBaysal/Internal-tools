# Mira — Faz 9: Dosya görünür (Madde 20-21)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 8](2026-08-09-mira-faz-8-ajan-design.md)

**Kapsam:** kesikli "creating file…" kartı, cevabın altındaki dosya kartı, proje ekranının **Files**
sütunu (Madde 20) · sohbetteki 320px ray (Madde 21).
**Kapsam dışı:** dosyayı açmak — okuma paneli ve indirme (Faz 10) · silme (Faz 11).

---

## 1 · Dosya listesi uç noktası

`GET /api/projects/<pid>/files` → her satırda `name`, `ext`, `modifiedAt`.

- **Sıra:** yeniden eskiye, `modifiedAt`'e göre. Yeni dosya en üstte.
- **Kaynak dizinin kendisi.** Ayrı bir kayıt dosyası yok: ad dosya adı, zaman mtime (Faz 1 kararı).
- `ext` uzantının ilk üç harfi — tasarımın çipi bu.
- Göreli zaman (`2h ago`) yine **tarayıcıda** hesaplanır.

`store` bir `mtime` metodu zaten veriyordu (Faz 1); ilk gerçek kullanıcısı burası.

## 2 · Akışta dosya olayı

`create_file` çalıştığı anda akışa bir olay girer:

| Olay | Ne zaman | Ekranda |
|---|---|---|
| `file` | araç dosyayı yazdıktan hemen sonra | kesikli kart yerini **dolu** dosya kartına bırakır |

**Kesikli kart ne zaman çıkar?** Model `create_file`'ı çağırdığı anda — yani araç çalışmadan **önce**.
Bunun için ikinci bir olaya gerek yok: döngü çağrıyı gördüğünde `file` olayını *"yazılıyor"* hâlinde
göndermek yerine, tarayıcı `create_file` çağrısını hiç görmez. Bu yüzden kesikli kartın tetiği
**araç çağrısının kendisi** olur ve akış iki olay taşır: `file-start` (ad henüz kesin değil) ve
`file` (yazıldı, adı bu).

`file-start` ad taşımaz — modelin istediği ad temizlenmeden ve çakışma çözülmeden kesin değildir, ve
tasarımın kesikli kartında zaten ad yok, yalnız *"creating file…"* yazıyor.

## 3 · Mesaj dosyayı hatırlar

Tasarımda dosya kartı **cevabın altında** duruyor. Bunun için `Message` bir alan kazanır: `files`
(ad listesi, varsayılan boş).

- Tek turda birden çok dosya doğabilir; hepsi listeye girer ve her biri bir kart olur. Tasarım tek
  kart gösteriyor çünkü prototipte tek dosya var — çoğulu düşürmek veri kaybı olurdu.
- Alan **diske yazılır**: sayfa yenilenince kart yerinde durmalı.
- Dosya sonradan silinirse (Faz 11) kart ne olur — o kararı Faz 11 verir; bu fazda dosya listesi
  cevaptır, kart onunla eşleşmezse çizilmez.

**`file.from` hâlâ yok.** Dosyanın hangi sohbetten doğduğu diske yazılmıyor; mesajın hangi dosyayı
doğurduğu yazılıyor. İkisi ters yönler: tasarım "kaynak sohbete git" bağlantısını yasaklıyor, ama
"bu cevabın ürettiği dosya" kartını istiyor.

## 4 · Ekranlar

**Sohbet — kesikli kart:** üç noktanın altında, `#FBF8F3` zemin, `1px dashed #DED5C9` çerçeve, mono
*"creating file…"*.

**Sohbet — dosya kartı:** cevabın altında, uzantı çipi + ad + yeşilimsi mono `✓ saved to project`.

**Sohbet — ray:** sağda kalıcı 320px. Başlık **Project files**, altında liste. Boşken
*"No files yet — send a message and Mira will create one."* Ray sohbet ekranının parçası; kullanıcı
yazarken neyin var olduğunu görsün diye hep açık.

**Proje ekranı — Files sütunu:** aynı liste, boşken zaten yazılı olan öğretici metin.

Yeni dosya üretildiğinde **ray ve proje listesi tazelenir** — kart ile listeler aynı anda dolar.

## 5 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain | `Message.files` · `file.py` — `File(name, ext, modified_at)` |
| domain/ports | `FileStore.list_files(project_id) -> list[File]` (adların yanına zaman) |
| domain/usecases | `list_files(file_store, project_id)` — yeniden eskiye · `stream_answer` `file-start`/`file` üretir |
| data | `FileFileStore.list_files` |
| presentation | `GET …/files` · `_sse` iki yeni olay |
| frontend | `useFiles.js` · `FileRow.jsx` · `FileRail.jsx` · sohbet ve proje ekranı |

`run_tool` artık `ToolResult(text, created)` döndürür: modele verilecek cümle ile "şu dosya doğdu"
bilgisi iki ayrı sorudur ve cümleyi ayrıştırmak kırılgan olurdu.

## 6 · Testler

1. `GET …/files` boş projede boş liste, patlamıyor.
2. Liste yeniden eskiye geliyor ve `ext` uzantının ilk üç harfi.
3. `run_tool` `create_file`'da doğan adı ayrıca bildiriyor; öbür araçlarda `created` boş.
4. Döngü araç çağrısını görünce `file-start`, dosya yazılınca `file` üretiyor.
5. Yazılan dosyanın adı `ai` mesajının `files` alanına giriyor ve diske yazılıyor.
6. Dosya üretmeyen cevabın `files` alanı boş.
7. Ön yüz: `file-start` kesikli kartı çıkarıyor, `file` onu dolu karta çeviriyor.
8. Ön yüz: cevabın altındaki kart adı ve `✓ saved to project` yazıyor.
9. Ön yüz: ray boşken öğretici metni, doluyken satırları gösteriyor.
10. Ön yüz: yeni dosya üretilince ray ve proje listesi tazeleniyor.

## 7 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: dosya isteyen mesaj at → kesikli kart → dolu kart; proje
ekranına dön → dosya listede en üstte; sohbette sağdaki ray onu gösteriyor.
