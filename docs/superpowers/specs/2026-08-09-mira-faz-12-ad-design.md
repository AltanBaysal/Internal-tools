# Mira — Faz 12: Yeniden adlandırma (Madde 27)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 11](2026-08-09-mira-faz-11-silme-design.md)

**Kapsam:** sohbet başlığını ve dosya adını değiştirmek; boş girdi iptal eder.
**Kapsam dışı:** proje adı (Faz 3'te bitti) · arama (Faz 13).

---

## 1 · İki uç nokta

| Uç nokta | Gövde | Yanıt |
|---|---|---|
| `PATCH /api/projects/<pid>/chats/<cid>` | `{"title": "..."}` | sohbet özeti |
| `PATCH /api/projects/<pid>/files/<name>` | `{"name": "..."}` | `{name, ext, modifiedAt}` |

Boş başlık **400**; olmayan sohbet/dosya **404**.

**Dosyanın yeni adı diskteki addır.** Ayrı bir "görünen ad" alanı yok — `CODE-STANDARD`'ın kuralı:
liste dizinin kendisidir.

## 2 · Çakışma: `-2`, 409 değil

Alınmış bir ada geçmek **reddedilmez**, `unique_name` uygulanır ve yanıt **gerçekten kullanılan adı**
söyler (Madde 19'un kuralı; `create_file` de böyle davranıyor).

**Faz 11'in Undo'su neden 409 veriyordu da bu vermiyor?** Undo'nun sözü *"tam olarak eskisini geri
koy"*; `-2` ile dönen dosya kullanıcının bastığı düğmenin sözü olmazdı. Yeniden adlandırmanın sözü
ise *"buna şu adı ver"* ve uygulamanın her yerdeki cevabı zaten *"plan-2.md olarak kaydedildi"*.
Farklı sözler, farklı sonuçlar.

**Kullanıcının yazdığı ad da temizlenir.** `safe_name` modelin adına ne yapıyorsa kullanıcınınkine de
yapar — ad diske gidiyor. Kökün kilidi ikinci savunma; tek savunma değil.

**Taşımak yeniden yazmak değildir:** `os.replace` mtime'ı korur, yani adı değişen dosya listede
yerinden oynamaz.

## 3 · Yeniden adlandırılan dosyaya bakan kart

Yol haritasının açık maddesi. Karar: **hiçbir mesaj yeniden yazılmaz.**

Mesajın `files` alanı *"bu cevap şunu üretti"* der ve bu, söylendiği anda doğruydu; sonradan
değiştirmek bir kaydı tahrif etmek olurdu. Kart ise *"şu dosya var ve adı bu"* der.

Bu yüzden kart **iki kaynağın kesişimidir**: mesajın hatırladığı ad, projenin bugünkü dosya
listesinde de varsa çizilir. Faz 9 bu cümleyi zaten yazmıştı ("kart listeyle eşleşmezse çizilmez")
ama uygulanmamıştı; burada uygulanıyor ve hem yeniden adlandırmayı hem **silmeyi** birden karşılıyor.

Sonuç: dosyanın adı değişince eski kart kaybolur, yeni ad rayda ve listede görünür. Sohbet metni
olduğu gibi kalır — kullanıcının okuduğu cümle değişmez.

## 4 · Ekranlar

- **`name` düğmesi** proje ekranındaki sohbet satırında ve dosya satırında; `×`'in yanında, aynı
  sessiz dilde. Kenar çubuğunda yok (orası gezinme yeri) ve sohbet ekranının başlığında yok.
- Soru tarayıcının kendi kutusuyla sorulur (`window.prompt`), Faz 3'teki proje adı gibi. **Boş girdi
  iptal eder** ve hiçbir istek gitmez.
- Yeni ad üç yerde birden görünür: satır, ray ve açık panel. **Açık panelin dosyası yeniden
  adlandırılırsa panel yeni adı okumaya devam eder** — kapanmaz, çünkü dosya duruyor.
- Sohbet başlığı iki listede de değişir (kenar çubuğu ve proje ekranı).
- **Faz 11'in şeridi genişliyor ve adı `FileStrip` oluyor.** Başarısız bir yeniden adlandırmanın
  söyleyecek bir yeri olmalı; sessizce reddeden bir liste, açıklayan bir listeden kötüdür. Şerit
  silme teklifi yokken de yalnızca hata satırını gösterebiliyor — o hâlde "File deleted." ve Undo
  çizilmiyor.

## 5 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain/errors | `InvalidChatTitle` |
| domain/ports | `FileStore.rename(project_id, name, wanted) -> str \| None` |
| domain/usecases | `rename_chat` · `rename_file` |
| data | `FileFileStore.rename` — `unique_name` + `move` |
| presentation | `PATCH …/chats/<cid>` · `PATCH …/files/<name>` |
| frontend | `useChatLists.renameChat` · `useFiles.rename` · satırlarda `name` düğmesi · `ChatScreen` kartı listeyle kesiştirir · `DeletedStrip` → `FileStrip` |

## 6 · Testler

1. Sohbet başlığı değişiyor ve diske yazılıyor; mesajlara dokunulmuyor.
2. Boş başlık 400, başlık eski hâlinde kalıyor.
3. Dosya adı değişiyor; içerik ve **mtime** aynı kalıyor.
4. Alınmış ada geçince `-2` alıyor ve yanıt kullanılan adı söylüyor; öbür dosya duruyor.
5. Kullanıcının verdiği kirli ad temizleniyor (`../x` → `x`).
6. Olmayan dosyayı/sohbeti adlandırma 404.
7. Ön yüz: kart yalnız listede karşılığı olan ad için çiziliyor.
8. Ön yüz: `name` düğmesi soruyor; iptal edilince istek gitmiyor.
9. Ön yüz: açık panelin dosyası adlandırılınca panel yeni adı gösteriyor.

## 7 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: sohbeti yeniden adlandır → iki listede de yeni ad. Dosyayı
yeniden adlandır → satırda, rayda ve açık panelde yeni ad; cevabın altındaki eski kart kaybolur,
sohbetin metni değişmez.
