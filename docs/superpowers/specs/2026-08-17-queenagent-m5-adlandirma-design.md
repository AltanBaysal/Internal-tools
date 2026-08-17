# Madde 5 — Yeniden adlandırmalar, `← back` ve yardım notları gider · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 5](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 21, 22, 23, 30, 37 · **karar 4** · `HANDOFF.md` §11
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Açık soru yok, ama bir kaynak düzeltmesi var

Yol haritası bu maddeyi *"karar 7"* ile etiketliyor. Karar 7 dosyasız cevabı konu alıyor ve bu
maddeyle ilgisi yok; kastedilen **karar 4**'tür:

> **4. Sohbet yeniden adlandırma kalkıyor** (madde 22 — çelişki çözüldü) … Yeniden adlandırma yalnız
> **projede** kalıyor.

Fark 22'nin çelişkisi buydu: sözleşme "Chats and files are not renameable" diyor ama duyarlı yerleşim
tablosu 780px'te *"the `name` button hides"* diyerek düğmenin varlığını varsayıyordu. Kullanıcı
çelişkiyi düğme aleyhine çözdü. Fark 30 (dosya yeniden adlandırma) zaten üç yolun üçünde de `öksüz`
çıkmış. Sorulacak bir şey kalmıyor.

---

## 1 · Ne gidiyor

### 1.1 · Yeniden adlandırma — sohbet ve dosya

Yeniden adlandırma **yalnız projede** kalıyor: proje başlığındaki "Rename". Sohbet ve dosya için
kapı, use case ve uç nokta birlikte gidiyor — arayüzü söküp uç noktayı bırakmak, kimsenin
çağırmadığı bir yazma yolu bırakmak olurdu.

| Katman | Ne gider |
|---|---|
| `domain/usecases/rename_chat.py` | **silinir** |
| `domain/usecases/rename_file.py` | **silinir** |
| `domain/errors.py` | `InvalidChatTitle` — tek kullanıcısı `rename_chat`'ti |
| `domain/ports.py` | `FileStore.rename` bildirimi |
| `data/file_file_store.py` | `rename` metodu |
| `presentation/routes.py` | `PATCH /api/projects/<pid>/chats/<cid>` ve `PATCH /api/projects/<pid>/files/<name>` |
| `FileRow.jsx` | "name" düğmesi ve `onRename` prop'u |
| `FileRail.jsx`, `ChatScreen.jsx`, `ProjectScreen.jsx` | `onRenameFile` / `onRenameChat` geçişleri |
| `ProjectScreen.jsx` | sohbet satırındaki "name" düğmesi |
| `useChatLists.js` | `renameChat` |
| `useFiles.js` | `rename` |
| `App.jsx` | `renameFile`, `retitleChat` |
| `workspace.css` | `.row-act` |

**İki uç nokta 404 değil 405 döndürür.** Aynı adreste `GET` ve `DELETE` duruyor; adres tanınır,
yöntem tanınmaz.

**`unique_name` kalıyor** — çöp kutusuna taşınan dosyaya ad verirken hâlâ kullanılıyor.
`store.move` de kalıyor: silme ve geri alma onu kullanıyor.

### 1.2 · `← back` (fark 21)

Proje ekranının başındaki mono `← back` gider — **iki yerden**: normal ekrandan ve "That project does
not exist." dalından. Ekran doğrudan başlık satırıyla başlar.

**Sohbet ekranının `← project name` başlığı KALIR.** Tasarım onu kendi yerleşim tablosunda açıkça
istiyor (`HANDOFF.md` §2: *"Header with `← project name`"*), dolayısıyla `.back` sınıfı da kalır.

Bu, Madde 3'te bilerek bırakılan geçici bağı da kapatır: `App.jsx`'teki `leaveProject` gider.

### 1.3 · Composer'ın altındaki mono notlar (fark 37)

Sözleşme *"No helper text under the composer"* diyor. Proje ekranındaki "the answer is saved as a
file" ve sohbetteki "save the answer as a file" gider; `Composer`'ın `note` prop'u ve
`.composer__note` kuralı da onlarla birlikte — başka çağıran yok.

### 1.4 · Dosya listesinin altındaki öğüt satırı (fark 23)

"Chats create the files; you just open and read them." gider. Sözleşme boş hâllerin metinlerini tek
tek veriyor ve **dolu** bir listenin altına konacak hiçbir metin tanımlamıyor; kuralı da *"Empty is
instructive, never decorative"*. Bu satır dolu listede de duruyordu, yani öğüt değil süstü.

**Boş hâl satırı kalır:** "No files yet — start a chat and QueenAgent will create one." — tasarımın
kendi cümlesi.

---

## 2 · Ne kalıyor

- **Proje yeniden adlandırma** — başlıktaki "Rename" ve `PATCH /api/projects/<id>`.
- **Sohbet ve dosya silme** — satırdaki `×`. Onay kutusuna geçişi Madde 19'un işi.
- **Sohbet ekranının geri başlığı** ve `.back` sınıfı.
- **Dosya panelinin `←` düğmesi** — `×`'e dönüşmesi Madde 23'ün işi, burada dokunulmuyor.

---

## 3 · Katman denetimi

Silinen her şey kendi katmanında: iki use case `domain/usecases/`'ten, bir metot `data/`'dan, iki
rota `presentation/`'dan. Yeni dosya, yeni bağ, yeni yön yok.

**`ports.py`'den bir metot çıkması bir daralmadır, gevşeme değil:** `FileStore` protokolü artık daha
az söz veriyor ve `data/` katmanı o sözü tutmak zorunda değil. `presentation → domain ← data →
services` aynen duruyor; üç yasak (`feature ↛ feature`, `service ↛ feature`, `service ↛ service`)
zorlanmıyor.

---

## 4 · Kabul ölçütü

1. Sohbet satırında ve dosya satırında (hem ray hem proje sütunu) "name" düğmesi yoktur; yalnız aç
   ve sil kalır.
2. `PATCH /api/projects/<pid>/chats/<cid>` ve `PATCH /api/projects/<pid>/files/<name>` **405** döner.
3. `rename_chat` ve `rename_file` modülleri import edilemez.
4. Proje ekranı başlık satırıyla başlar; `← back` yoktur — proje bulunamadığında da yoktur.
5. Sohbet ekranının `← proje adı` başlığı yerindedir.
6. Hiçbir composer'ın ayağında mono not yoktur.
7. Dosya listesinin altında öğüt satırı yoktur; boş hâl cümlesi yerindedir.
8. Proje yeniden adlandırma çalışmaya devam eder.

## 5 · Risk

En büyük risk **fazla silmek**: `.back` sınıfı, `unique_name`, `store.move` ve dosya panelinin `←`
düğmesi silinenlere benziyor ama hepsinin yaşayan bir kullanıcısı var. Her biri yukarıda adıyla
korunuyor ve testleri bunu tutuyor.
