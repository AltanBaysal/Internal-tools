# Mira — Faz 10: Okuma (Madde 22-24)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 9](2026-08-09-mira-faz-9-dosya-gorunur-design.md)

**Kapsam:** dosyayı okuma paneli — sohbette rayın 320 → 560px genişlemesi (Madde 22), proje
ekranında sağdan 560px panel ve ızgaranın tek sütuna inmesi (Madde 23), **Download** (Madde 24).
**Kapsam dışı:** silme ve Undo (Faz 11) · yeniden adlandırma (Faz 12) · arama (Faz 13) · tam ekran
okuyucu ve düzenleme (tasarım ikisini de yasaklıyor).

---

## 1 · Dosyayı okuma uç noktası

`GET /api/projects/<pid>/files/<name>` → `{name, ext, modifiedAt, size, text}`; dosya yoksa **404**
ve `{"error": "file not found"}`.

- **`size` metinden türetilir**, diske ikinci bir soru sorulmaz: `len(text.encode("utf-8"))`. Aynı
  okumadan çıktığı için içerikle asla çelişemez. Tarayıcı bunu kendisi sayamaz — JS'in karakter
  sayısı UTF-8 baytı değildir.
- Ad URL'in bir parçası; Flask'ın `<string>` dönüştürücüsü eğik çizgi kabul etmez, `store`'un kökü de
  kaçmayı reddeder. Adı kullanıcıdan almak bu iki kısıt sayesinde güvenli.
- **v1'de her dosya metindir:** dosyaları yalnız `create_file` üretir ve yükleme yoktur. Bu yüzden
  gövde JSON'dur ve ikili (binary) bir yol yok.

## 2 · Panel neyi gösterir

Üstte `←` + dosya adı · ortada **düz metin** · altta tek satır mono meta.

**Meta satırı:** `md · 1.4 KB · 2h ago` — çip, boyut, göreli zaman. Üçü de zaten cevabı olan
sorular; panel yeni bir bilgi uydurmaz. Boyut biçimi: 1024'ün altında `412 B`, üstünde tek ondalıkla
`1.4 KB`, 1 MB'ın üstünde `2.3 MB`.

**Metin düz kalır.** Markdown render edilmez: `create_file` bir metin yazar, ekran da onu yazar.
Render etmek v1'in vermediği bir söz olurdu.

**Yüklenirken hiçbir şey çizilmez** — sohbet ekranı da yoldaki sohbet için hiçbir şey çizmiyor.
İskeletler Faz 14'ün işi.

**Dosya gitmişse** panel *"That file is gone."* der (Faz 11'de silme geldiğinde bu cümlenin gerçek
bir kullanıcısı olacak).

## 3 · Panel nerede durur

Tek bileşen, iki kap:

| Ekran | Kap | Davranış |
|---|---|---|
| Sohbet | rayın kendisi | 320 → **560px**, 220ms geçiş; sohbet sütunu daralır, hiçbir şeyin üstü örtülmez |
| Proje | sağda 560px `aside` | ızgara **tek sütuna** iner, sohbet listesi tam genişliğe geçer |

Genişlik geçişi tasarımın izin verdiği tek hareketlerden biri — `app.css` bunu zaten yazıyor.

**Açık dosya `App`'te tutulur** (bir ad), adres çubuğuna girmez: tasarım dosya için bir URL
tanımlamıyor ve "kaynak sohbete git" bağlantısını yasaklayan karar da dosyayı bir konum yapmamaktan
yana. **Proje değişince kapanır**; aynı projenin iki ekranı arasında gidip gelirken açık kalır,
çünkü okunan şey projeye ait.

**`←` listeye döner, Esc paneli kapatır.** İkisi de aynı şeyi yapar; tasarım iki yol veriyor. Esc
dinleyicisi `window`'a panel açıkken takılır ve kapanınca sökülür — kapalıyken tuşu dinleyen bir şey
kalmaz. Faz 13 Esc'i katmanlayacak (önce arama, sonra panel); bu fazda tek katman var.

**Açıkken başka bir satıra tıklamak dosyayı değiştirir**, paneli kapatıp açmaz: kap zaten açık, içi
yenisiyle dolar.

## 4 · Download

Buton dosyayı **sunucudan yeniden okur**, ekrandaki kopyayı kaydetmez: panel bir dakika önce
okumuş olabilir, indirilecek olan diskteki hâlidir.

- İstek uçarken butonun içine spinner girer ve etiket **"preparing…"** olur. Bu bekleme **gerçek**
  bir isteğin beklemesi; uydurma bir ilerleme değil. Yerel makinede kısa sürer, o zaman kısa görünür.
- **Buton yerinden oynamaz:** genişliği sabitlenir, etiket içinde değişir.
- Kaydetme yolu: yanıttan bir `Blob`, `URL.createObjectURL`, gizli bir bağlantıya tıklama, sonra
  `revokeObjectURL`. Ayrı bir indirme uç noktasına gerek yok — `Content-Disposition` verilse tarayıcı
  işi kendi üstlenir ve tasarımın istediği "preparing…" hâli hiç doğmazdı.
- İndirme başarısız olursa buton eski hâline döner ve panelin altında sunucunun kendi sözleri yazar —
  sebep uydurulmaz (hata kartının Faz 7'de konan kuralı).

## 5 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain | `FileBody(file, text)` — `size` metinden türeyen bir özellik · `FileNotFound` |
| domain/ports | `FileStore.read_body(project_id, name) -> FileBody \| None` |
| domain/usecases | `read_file(file_store, project_id, name)` — yoksa `FileNotFound` |
| data | `FileFileStore.read_body` — tek dosya için tek okuma + tek `mtime` |
| presentation | `GET …/files/<name>` |
| frontend | `useFile.js` · `FilePanel.jsx` · ray ve proje ızgarasının açık hâli |

**Neden `read` dururken `read_body`?** İki farklı soru: `read` modelin sorusudur ("içinde ne var"),
`read_body` panelin sorusudur ("bu dosya nedir ve içinde ne var"). Panelin sorusunu iki çağrıya
bölmek diskte yarış açardı — arada silinen dosya için `read` metin, `get` `None` döndürürdü.

## 6 · Testler

1. `GET …/files/<name>` metni, çipi, zamanı ve boyutu veriyor.
2. Olmayan dosya 404, gövdede sunucunun cümlesi.
3. `size` metnin UTF-8 bayt sayısı — ASCII olmayan karakterde karakter sayısından farklı.
4. `read_file` yoksa `FileNotFound` atıyor.
5. Ön yüz: raydaki satıra tıklayınca panel açılıyor, ad ve metin görünüyor.
6. Ön yüz: `←` listeye dönüyor, **Esc** paneli kapatıyor.
7. Ön yüz: meta satırı çip, boyut ve göreli zamanı yazıyor.
8. Ön yüz: proje ekranında dosyaya tıklayınca panel açılıyor ve ızgara okuma sınıfını alıyor
   (jsdom stil hesaplamaz; sınıf adı sözleşmedir).
9. Ön yüz: Download sürerken etiket "preparing…", bitince eski etiket.
10. Ön yüz: Download **yeni bir istek** atıyor — paneldeki kopyayı kaydetmiyor.

## 7 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: sohbette raydaki dosyaya tıkla → ray genişler, metin okunur,
sohbet daralır ama okunmaya devam eder; Esc kapatır. Proje ekranında dosyaya tıkla → sağda panel,
ızgara tek sütun; `←` kapatınca ızgara geri gelir. Download → dosya diske iner ve içeriği panelde
görünenle aynıdır.
