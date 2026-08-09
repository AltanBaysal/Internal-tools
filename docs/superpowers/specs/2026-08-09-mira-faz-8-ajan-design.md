# Mira — Faz 8: Ajan döngüsü (Madde 17-19)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 7](2026-08-09-mira-faz-7-akis-design.md)

**Kapsam:** ajan döngüsü ve `list_files` (Madde 17) · `read_file` (Madde 18) · `create_file` (Madde 19).
**Kapsam dışı:** dosyanın ekranda görünmesi — kesikli kart, dosya kartı, listeler (Faz 9).

---

## 1 · Doğrulanmış gerçekler

xAI dokümanından:

- Araçlar OpenAI biçiminde: `[{"type":"function","function":{"name","description","parameters"}}]`.
- Model araç isterse cevabın mesajında `tool_calls` durur: her birinde `id` ve
  `function.name` + `function.arguments` (JSON **metni**).
- Sonuç geri gönderilirken mesaj `{"role":"tool","tool_call_id":…,"content":…}` olur.
- **Akışta araç çağrısı bölünmez:** *"the function call is returned in whole in a single chunk"*.
- Model aynı turda **birden fazla** araç isteyebilir.

Son madde döngüyü ciddi basitleştiriyor: parça parça gelen bir çağrıyı birleştirme işi yok.

## 2 · Döngü

```
tur = 0
while tur < MAX_ROUNDS:
    motoru araçlarla akıt
      metin parçaları geldikçe: biriktir ve dışarı ver
      araç çağrıları geldiğinde: topla
    çağrı yoksa → çık
    her çağrıyı çalıştır, sonucunu konuşmaya ekle
    tur += 1
sonunda biriken metni tek bir ai mesajı olarak yaz
```

**`MAX_ROUNDS = 8`.** Sekiz tur, "listele → oku → oku → yaz → anlat" gibi en uzun makul zinciri
rahat karşılıyor; sınırsız bırakmak hem para hem zaman yakar. Sınıra gelinince döngü kesilir ve model
elindekiyle konuşmuş olur — hata değil, durak.

**Biriken metin turlar boyunca taşınır.** Model bir tur konuşup sonra araç çağırabilir; o konuşma da
cevabın parçasıdır. Diske **tek** `ai` mesajı yazılır.

**Ara mesajlar sohbette saklanmaz.** Araç çağrıları ve sonuçları yalnız motora giden listede yaşar.
Gerekçe: sohbet kullanıcının okuduğu şeydir, modelin iç muhasebesi değil; ve tasarımda o satırların
çizileceği hiçbir yer yok.

## 3 · Üç araç

| Araç | Girdi | Ne döndürür |
|---|---|---|
| `list_files` | — | Projedeki dosya adları |
| `read_file` | `name` | Dosyanın içeriği |
| `create_file` | `name`, `content` | Yazılan dosyanın **gerçek** adı |

**Araçları sunucu çalıştırır.** Model yalnız "şunu çağır" der; hangi projenin okunacağı çağrının
değil, isteğin bağlamındadır. Model başka bir projenin adını yazsa bile o proje okunmaz — araçlar
zaten yalnız içinde bulunduğumuz projeye bağlıdır.

**Olmayan dosya hata değildir.** `read_file` bulamazsa döngü patlamaz; modele "böyle bir dosya yok"
denir ve model devam eder. Aynısı bilinmeyen araç adı için de geçerli.

## 4 · Dosya adı modelden gelir, olduğu gibi kullanılmaz

`create_file`'ın adı **temizlenir**:

- Yalnız dosya adı alınır; yol ayırıcıları atılır (`notes/a.md` → `a.md`). Model alt klasör
  açamaz — tasarımda klasör diye bir kavram yok.
- Harf, rakam, `-`, `_`, `.` dışındaki karakterler `-` olur; baştaki noktalar atılır.
- Uzantı yoksa `.md` eklenir. v1'de üretilen dosya markdown'dır.
- Temizlik sonrası boş kalırsa `note.md` olur.
- Ad çakışırsa **üstüne yazılmaz**, sondan önce sayı eklenir: `plan.md` → `plan-2.md`.

Store'un kök hapishanesi (Faz 1) ikinci savunma hattıdır. Faz 1'de yazdığım gerekçe tam da bugün
işliyor: o gün bir hatayı yakalıyordu, bugün modelin ürettiği bir adı yakalıyor.

## 5 · Sistem yönergesi

`domain/prompt.py` genişler. Üç şeyi söyler:

1. Araçların ne olduğu ve projedeki dosyaların ortak olduğu.
2. **Dosyayı ancak kullanıcı bir belge istediğinde** üret; her cevabı dosyaya çevirme.
3. Cevabı sohbette de yaz — dosya cevabın yerine geçmez.

İkinci madde kullanıcının kararının doğrudan karşılığı: dosya üretmek modelin kararı, ama varsayılanı
"üretme".

## 6 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain | `tools.py` — araç tanımları (`TOOL_SPECS`), ad temizleme, `run_tool` dağıtıcısı |
| domain/ports | `FileStore`: `list_names`, `read`, `write` · `Engine.stream` artık `{"text"…}` / `{"tool_calls"…}` veriyor |
| domain/usecases | `stream_answer` ajan döngüsüne dönüşür |
| data | `file_file_store.py` — `files/` dizinini bilen tek yer |
| services/xai | `stream` metin **ve** araç çağrısı üretir |

`Engine.stream`'in sözleşmesi değişiyor: artık düz metin değil, tek anahtarlı sözlükler veriyor
(`{"text": …}` ya da `{"tool_calls": […]}`). Tek tip iki şey taşımaktan (metin mi, çağrı mı) daha
açık ve testte ayırt etmesi kolay.

## 7 · Testler

1. Araç çağrısı olmayan tur döngüyü bir turda bitiriyor.
2. `list_files` çağrısı çalıştırılıyor, sonucu konuşmaya `role="tool"` olarak ekleniyor, ikinci tur
   yapılıyor.
3. Model iki aracı aynı turda isterse ikisi de çalışıyor.
4. `MAX_ROUNDS`'a gelen döngü kesiliyor ve biriken metin yazılıyor.
5. Turlar boyunca biriken metin **tek** `ai` mesajı olarak diske düşüyor.
6. Ara mesajlar (araç çağrısı, araç sonucu) sohbette saklanmıyor.
7. `read_file` olmayan dosyada hata değil, açıklama döndürüyor.
8. Bilinmeyen araç adı döngüyü düşürmüyor.
9. Ad temizleme: yol ayırıcı, geçersiz karakter, uzantısız ad, boş ad, çakışma.
10. `create_file` dosyayı diske yazıyor ve **gerçek** adı döndürüyor.
11. `XaiClient.stream` araç çağrısı taşıyan kareyi `{"tool_calls": …}` olarak veriyor.

## 8 · Kabul kriteri

`pytest` yeşil. Gerçek anahtarla: "bunu bir dosyaya yaz" → dosya `files/` altında; "merhaba" → dosya
yok; var olan bir dosyayı sor → cevap içeriğine dayanıyor.
