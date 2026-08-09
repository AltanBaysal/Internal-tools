# Mira — Faz 3: Proje ekranı (Madde 6-7)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım dokümanı v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) ·
[Faz 2](2026-08-09-mira-faz-2-kabuk-design.md)

**Kapsam:** proje ekranı (Madde 6) · proje adının ve açıklamasının değiştirilmesi (Madde 7).
**Kapsam dışı:** composer'ın çalışması (Madde 8) · sohbet listesinin dolması (Madde 12) · dosya
listesinin dolması (Madde 20) · proje silme (tasarımda yok).

---

## 1 · Ekran

`← back` · başlık · açıklama · composer kabuğu · iki sütunlu ızgara. Sol sütun **Chats**, sağ sütun
**Files Mira created** (320px). İkisi de bu fazda boş.

**Boş dosya listesi öğretici konuşur:** *"No files yet — start a chat and Mira will create one."*
Altında tasarımın ikinci satırı: *"Chats create the files; you just open and read them."*

**Boş sohbet listesi bu fazda metinsiz kalır.** Gerekçe: composer tam üstünde duruyor ve ne yapılacağını
zaten söylüyor; ikinci bir çağrı aynı şeyi iki kez söylemek olurdu. Dosya sütununda metin var, çünkü
orası kullanıcının **hiçbir şey yapamayacağı** bir sütun — dosyayı o üretmiyor, açıklama olmadan boşluk
anlamsız.

**Proje bulunamazsa** (elle yazılmış geçersiz adres) tek satır: *"That project does not exist."* ve
`← back`. Uygulama çökmemeli; adres kullanıcı tarafından yazılabilen bir şey.

**Veri kaynağı yeni bir uç nokta değil.** Ekran, Faz 2'nin çektiği proje listesinden kendi projesini
bulur. Tek kullanıcılı yerel bir uygulamada liste zaten tam; ikinci bir `GET` aynı cevabı ikinci kez
sormak olurdu.

## 2 · Yeniden adlandırma (Madde 7)

Tasarım: *"Projects and chats rename through a single prompt; empty input cancels."* Aynen uygulanır —
`window.prompt`, boş girdi iptal eder.

### Açıklama da değişir

Yol haritasının açık sorusu burada kapanıyor: **açıklama düzenlenebilir olur.**

Gerekçe prototipin kendi metni: yeni proje `Click to add a description.` yazıyor. Düzenlenemezse bu
cümle bir yalan — kullanıcıya tıklamasını söyleyip hiçbir şey yapmayan bir metin. İki çıkış vardı,
metni değiştirmek ya da tıklamayı çalıştırmak; ikincisi tasarımın kendi sözünü tutuyor ve yeni bir
kontrol icat etmiyor.

Yani: **açıklamaya tıklamak** aynı tek-prompt kalıbını açar. Yeni bir buton yok, yeni bir kalıp yok.

Boş girdi **iptal eder** — ne adı ne açıklamayı boşaltmanın yolu var. Ad zaten boş olamaz; açıklama
için de aynı kural, çünkü iki alan için iki farklı iptal davranışı öğrenilecek fazladan bir şey olurdu.

### Sunucu tarafı

Tek uç nokta: `PATCH /api/projects/<id>`, gövdesinde `name` ve/veya `desc`.

- Ad boş ya da yalnız boşluksa **400**. Kural sunucudadır; tarayıcının iptal etmesi bir kolaylıktır,
  güvence değil.
- Bilinmeyen id **404**.
- Gönderilmeyen alan **değişmez**; istek kısmi bir güncellemedir.
- Ad ve açıklama **kırpılır** (baştaki/sondaki boşluk atılır).

`hue` ve `createdAt` bu uç noktadan değişmez: biri projenin kimliğinin parçası, öbürü geçmişi.

## 3 · Katmanlar

| Katman | Ekleme |
|---|---|
| domain/ports | `ProjectStore` iki metot kazanır: `get(project_id) -> Project \| None`, `replace(project)` |
| domain/usecases | `edit_project(store, project_id, name=None, desc=None) -> Project` — kırpar, doğrular, yazar |
| data | `FileProjectStore.get` ve `.replace` |
| presentation | `PATCH /api/projects/<id>` |

`edit_project` hatayı iki ayrı tiple bildirir: `ProjectNotFound` ve `InvalidProjectName`. Rota
bunları 404 ve 400'e çevirir; **domain HTTP kodunu bilmez.**

## 4 · Testler

Kanıtlanacak cümleler:

1. Ad değişiyor ve diskte kalıcı.
2. Yalnız açıklama gönderilince ad değişmiyor (ve tersi).
3. Boş ya da yalnız boşluktan oluşan ad reddediliyor, eski ad duruyor.
4. Bilinmeyen id 404.
5. Ad ve açıklama kırpılıyor.
6. `hue` ve `createdAt` düzenlemeden sonra aynı.
7. Proje ekranı başlığı, açıklamayı ve iki sütun başlığını çiziyor.
8. Boş dosya sütunu öğretici metni gösteriyor.
9. Geçersiz adres "yok" satırını gösteriyor, çökmüyor.
10. Rename prompt'u boş dönerse istek atılmıyor.
11. Yeniden adlandırılan proje sidebar'da ve kartta **aynı anda** yeni adı yazıyor.

## 5 · Kabul kriteri

`pytest` ve `npm test` yeşil; derlemeden sonra: karta tıkla → proje ekranı açılır; Rename → ad
değişir ve sidebar aynı anda güncellenir; açıklamaya tıkla → değişir; sayfayı yenile → ikisi de durur.
