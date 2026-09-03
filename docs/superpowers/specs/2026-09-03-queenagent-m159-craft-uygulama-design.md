# Madde 159 — Şema aracı uçar · **uygulama turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Test turu:**
[m159 craft testler design](2026-09-03-queenagent-m159-craft-testler-design.md) ·
**Kırmızı commit:** `test(m159)`

19 test kırmızı. Bu belge onları yeşile çeviren kodu anlatır.

## `CRAFT` — tek metin

`tools.py`'de, `WRITING`'in üstünde. Bir promptun değerinin nasıl yazıldığı, ve **yalnız o**:
dosyanın şeklinden hiç söz etmiyor.

İçindekiler, ve her birinin nereden geldiği:

| Cümle | Kaynağı |
| --- | --- |
| Etiket yazılır, cümle değil; artikel yok | Şemanın *"comma-separated fragments"* paragrafı, kural 7 |
| Tek donmuş an; hareket geçtiği poz olarak yazılır | Şemanın açılışı, kural 10 |
| `action` yalnız kameranın gördüğü; sebep neye benziyorsa o | Şemanın action paragrafı, kural 9 |
| `camera` iki karar, ikisi de verilen listelerden | Şemanın camera paragrafı, kural 11 |
| Değerin içinde `or` yok | Kural 13 |
| Kalite ve sayı koda ait | 150 ve 156 |
| Kareyi ilk anılan karakter açar | Şemanın characters paragrafı |
| Her şey İngilizce, `scene` hariç | Şemanın son cümlesi, 155 |

**Kalanlar bilerek düşüyor:** kitapçığın *"aynı ad iki dosyada farklı metin taşımasın"* kuralı
*(dosyalar arası, hiçbir araç göremiyor)*, ve şeklin tamamı.

## Nereye giriyor

Dört aracın açıklamasının **sonuna**, aracın kendi cümlesinden sonra: model önce ne yaptığını,
sonra nasıl yazacağını okuyor.

`WRITING` de `CRAFT` üstüne kuruluyor — 155'in ikinci kopyası burada tek kaynağa dönüyor. Alt modele
özgü olan kısım kalıyor *(ne verildiği, JSON ile cevap, adların haritalardan gelmesi)*; craft
oradan siliniyor ve `CRAFT` ekleniyor.

## Ne siliniyor

| Yer | Ne |
| --- | --- |
| `schema.py` | dosyanın tamamı |
| `tools.py` | `SCHEMA` import'u, aracın tanımı, `run_tool`'daki dalı |
| `modes.py` | `READS`'ten ikinci ad |
| `context_box.py` | `schema_was_read` |
| `stream_answer.py` | `schema_was_read` import'u ve kutudaki blok |
| `skills.py` | iki metindeki şema cümleleri, ve modül docstring'inin ilgili paragrafı |

## Ödenen bedel, kayda geçiyor

Araç açıklamaları da her turda gidiyor. `CRAFT`'ın dört kopyası her isteğe biniyor — kabaca 700–900
jeton. Şema aracı bunu yalnız çağrıldığında ödetiyordu.

Kazanç jeton değil **dikkatin yeri**: kural, yönettiği parametrenin yanında duruyor ve model onu tam
o aracı seçerken okuyor. Bir de kaybolan bir round var. Bu takas bilerek yapılıyor; dar gelirse
metnin dört kopyası tek bir yere indirilebilir, ve o zaman kural parametrenin yanından uzaklaşır.

## Nasıl yeşil olacak

19 kırmızı `CRAFT`'ın var olması ve şemanın gitmesiyle kapanır. Notebook'un iki kırmızısı yerinde
kalır.
