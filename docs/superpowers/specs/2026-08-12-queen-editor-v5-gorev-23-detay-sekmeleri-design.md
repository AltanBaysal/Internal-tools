# Queen Editor v5 · Görev 23 — Sekme şeridi ve katman sütunu · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 7, Görev 23 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
73, 75, 82 · **Tür:** arka uç + ön yüz.

## Neden

Kare artık üç katman taşıyor ama detay sayfası hâlâ tek katmanlık: yalnız fotoğrafı gösteriyor,
yalnız onun prompt'unu yazıyor. Videonun ve sesin dosya adı da prompt'u da hiçbir yerde okunmuyor.

## Ne olacak

Görsel alanının üstüne **Foto | Video | Ses** şeridi gelir; karenin sahip olmadığı sekme pasif
durur. Sağ sütun açık sekmeye göre büyür: sıra, o katmana kadarki dosya adları, açık katmanın
prompt'u ve altındakilerin prompt'ları. Bekleyen ve çalışan karenin görsel alanı tasarımın diline
geçer.

## Kararlar

### 1. Kare satırı katman prompt'larını da taşır

`list_frames` her satıra `prompts` ekler: `{"photo": …, "video": …, "audio": …}` — kaydın katman
katman cevabı (Görev 20'de açıldı), fotoğrafın prompt'u için satırın kendi `prompt` alanı yedek.

`queue_layer` de bunu kendi okumayı bırakıp satırdan alır: aynı soruyu iki yerde cevaplamak, ikisinin
ayrışması demek.

### 2. Sekme, karenin sahip olduğu katmanı açar; ötekiler pasif

Madde 73: sahip olunmayan sekme **gizlenmez**, pasif kalır ve katman üretilince açılır. Sebep
tasarımın kendi cümlesi — kullanıcı karenin nelere sahip olabileceğini görür.

"Sahip olmak" burada da biten katman demek: hatalı katmanın sekmesi pasiftir (hata hâli Görev
27'nin işi).

Açılışta sekme **Foto**'dur: fotoğraf karenin kendisi, ötekiler onun üstüne binen şeyler.

### 3. Sütun açık sekmeye kadar büyür

Sıra satırı hep durur. Sonra açık katmana kadar **dosya adları** (Foto · Video · Ses), sonra açık
katmanın **prompt'u**, sonra altındakiler **salt okunur** — madde 75'in "video sekmesinde video
prompt'u düzenlenebilir, foto prompt'u salt okunur" cümlesinin genel hâli.

Düzenlenebilirlik Görev 25'te geliyor; bu görevde bütün kutular okunur, ama hangisinin kimin olduğu
şimdiden belli.

Negatif prompt yalnız Foto sekmesinde durur: video ve ses işleri negatif taşımıyor.

### 4. Görsel alan bu görevde fotoğrafı göstermeye devam eder

Oynatma Görev 24'ün işi. Sekme değişince bu görevde **sütun** değişir; görsel alan karenin
fotoğrafını göstermeye devam eder. Yerine geçici bir kutu koymak, bir sonraki görevde silinecek bir
ekran icat etmek olurdu.

### 5. Bekleyen ve çalışan karenin alanı (madde 82)

Bekleyen karenin tutucusu **karenin kendi oranını** alır ve içindeki iki satır %45 opaklıkta
çizilir; çalışan karede alan dönen göstergeye döner (bugün de öyle, bu yarısı duruyor).

"Karenin kendi oranı" pratikte 1:1 kalır — üretilen fotoğrafın oranını sunucu bilmiyor ve tasarımın
kendi karesi kare. Değişen şey iki satırın opaklığı ve tutucunun kutu ölçüsünü fotoğrafın kapladığı
alandan alması.

## Nasıl görülür

1. Üç katmanlı karede üç sekme açık; katmansız karede yalnız Foto açık, ötekiler soluk ve tıklanmaz.
2. Video sekmesinde sütunda foto ve video dosya adları, video prompt'u ve altında salt okunur foto
   prompt'u var.
3. Ses sekmesinde ses prompt'u, altında video prompt'u.
4. Bekleyen karenin tutucusundaki iki satır soluk.

## Testler

**Arka uç:** kare satırı katman prompt'larını taşır · foto prompt'u kayıtta yoksa satırın kendi
prompt'u kullanılır · `queue_layer` kopyaya bu prompt'ları yazar (var olan testler yeşil kalır).

**Ön yüz:** üç sekme çizilir · sahip olunmayan sekme pasif · hatalı katmanın sekmesi pasif · sekme
değişince sütun o katmanın prompt'unu gösterir · video sekmesinde foto prompt'u salt okunur olarak
altta · foto sekmesinde negatif var, video sekmesinde yok · bekleyen karenin iki satırı soluk.

## Kapsam dışı

- **Oynatma** — Görev 24.
- **Düzenleme ve Yeniden üret** — Görev 25.
- **Sekme başına yıkıcı eylem** — Görev 26 (bu görevde alttaki tek buton bugünkü hâlinde kalır).
- **Hata sebebi ve kopya kare detayı** — Görev 27.

## Riskler

- **Sütun uzuyor.** Ses sekmesinde üç dosya adı ve üç prompt kutusu var; sütun kaydırılabilir
  kalıyor, kutular kendi içinde kaydırıyor (bugünkü kalıp).
