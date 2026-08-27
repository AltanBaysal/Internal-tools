# Madde 99 — Kapı çalıştırma anına iner · **test turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [izin tasarımı](2026-08-28-queenagent-izin-tasarimi-design.md) — ve onun kaynağı
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 99 ·
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod bir sonraki turda.

---

## Neyin adı ne

Testler yazılmadan önce adların durması gerekiyor, çünkü kırmızı testler onları çağıracak.

| Ad | Nerede | Ne |
|---|---|---|
| `needs_permission(mode, tool)` | `domain/modes.py` | Bu çağrı sorulmadan çalışır mı |
| `Decision` | `domain/permission.py` | `allowed` ve `reason` taşıyan karar |
| `PermissionWanted` | `domain/permission.py` | Akışa çıkan soru: `tool`, `arguments` |
| `Waiting` | `domain/permission.py` | Nabız |
| `refusal_text(tool, reason)` | `domain/permission.py` | Modele giden açıklama |
| `Permissions` | `domain/ports.py` | Port: `answer`, `wait`, `wake`, `clear` |
| `MemoryPermissions` | `data/memory_permissions.py` | Kaydın kendisi |
| `HEARTBEAT_SECONDS` | `domain/usecases/stream_answer.py` | 15 |

`tools_for` **gidiyor.** Kip artık isteğin taşıdığı listeyi belirlemiyor, ve argümanına bakmadan
hep aynı şeyi döndüren bir işlev okuyanı yanıltır. `stream_answer` doğrudan `TOOL_SPECS` veriyor.

`ask` diye bir port yöntemi **yok.** Soruyu açan ayrı bir çağrı olsaydı, kapıdan önceden gelmiş bir
cevabı silmesi mi yoksa saklaması mı gerektiği bir kararı olurdu — ve iki cevabın sırası bu kararın
üstünde durur. Bunun yerine `wait` cevabı **tüketiyor**: önceden bırakılmış cevap ilk soruyu
karşılıyor, aynı turdaki ikinci soru temiz bekliyor.

## Bekleyişin nasıl test edildiği

**Hiçbir test 15 saniye beklemiyor.** Üç yer, üç yol:

- **Alan testleri** sahte bir kayıt kullanıyor; `wait` çağrıldığı anda cevabı veriyor, nabız
  aralığına hiç bakmıyor. Nabzı görmek isteyen test, sahte kaydın önce `None` sonra karar
  döndürmesini söylüyor.
- **Kaydın kendi testi** kendi aralığını veriyor — saniyenin yüzde biri. Gerçekten bekleyen tek
  test bu, ve beklediği şey milisaniyeler.
- **Kapı testleri cevabı soru sorulmadan bırakıyor.** Kayıt bunu zaten karşılıyor *(bu, `hold`'un
  bugün çözdüğü yarışın aynısı)*, yani `wait` beklemeden dönüyor. Gerçek sıra — önce soru, sonra
  cevap — kaydın kendi testinde ve alan testlerinde kanıtlanıyor; HTTP üstünde bir kez daha
  kanıtlamak ikinci bir iş parçacığı ister, ve o iş parçacığı testi zamanlamaya bağlar.

## Kırmızılar

### A · `test_modes.py` — kural

Dosya yeni sorunun etrafında yeniden yazılıyor. `tools_for`'un üç testi **siliniyor** — sordukları
işlev kalkıyor, ve kalkan bir işlevin testi tur 2'de kırmızı kalırdı.

1. Soru kipi yazan bir aracı **soruyor**.
2. Soru kipi okuyan üç aracı sormuyor.
3. Edit kipi **hiçbir şeyi** sormuyor — `TOOL_SPECS`'teki her ad tek tek.
4. Plan kipi `write_plan`'i sormuyor, `create_file`'ı soruyor.
5. Kimsenin bilmediği bir kip edit gibi davranıyor: sormuyor.
6. Kimsenin bilmediği bir **araç** hiç sorulmuyor. Uydurulmuş bir ad zaten çalışmayacak; onu sormak
   kullanıcıya var olmayan bir şeyi onaylatmak olurdu.
7. `ends_the_turn` duruyor — bugünkü testi olduğu gibi kalıyor.

### B · `test_permissions.py` — kayıt *(yeni dosya)*

1. Soru sorulmadan bırakılmış cevap, ilk beklemede hemen alınıyor.
2. Cevapsız bekleyiş, aralık dolunca **hiçbir şey** döndürüyor.
3. Bekleyen biri varken gelen cevap onu uyandırıyor — ölçülen şey, beklemenin aralıktan **çok
   önce** bitmesi.
4. `wake` cevapsız uyandırıyor: dönen şey yine hiçbir şey. Stop'un çıkış yolu bu.
5. Bir sohbetin cevabı komşusunu cevaplamıyor.
6. Sebep reddin içinde geliyor.
7. `clear` hem soruyu hem cevabı unutuyor — kalırsa bir sonraki turu cevaplar.
8. Cevap **tükeniyor**: aynı cevap ikinci bir beklemeyi karşılamıyor.

### C · `test_stream_answer.py` — tur

1. Kipin kapsamadığı çağrı, araç çalışmadan **önce** soruluyor.
2. Soru aracın adını ve **ham argümanlarını** taşıyor.
3. Onay aracı çalıştırıyor — dosya diske iniyor.
4. Onay kipi değiştiriyor: aynı turdaki ikinci yazma bir daha sorulmuyor.
5. Red aracı çalıştırmıyor — ortada dosya yok.
6. Red modele bir araç cevabı gönderiyor, ve cevap aracın adını anıyor.
7. Kullanıcının sebebi varsa o cevabın içinde.
8. Red bir kart yazıyor, ve kart hiçbir dosya adı taşımıyor.
9. Red turu bitirmiyor: sonraki tur hâlâ koşuyor.
10. Bekleyiş sırasında gelen stop turu **durdu** olarak kapatıyor.
11. Cevapsız geçen aralık bir nabız çıkarıyor, ve bekleyiş sürüyor.
12. Edit kipi kayda hiç dokunmuyor — dokunursa test patlıyor.
13. Her kip modele **bütün** araçları veriyor.
14. Soru, kesik çizgili karttan önce geliyor. Sırası tersse kart bekleyiş boyunca boşuna durur.
15. Tur nasıl biterse bitsin kayıt temizleniyor.

### D · `test_chats_api.py` — kapı

Uygulama kurucusu izin kaydını da alıyor, yani bu dosyanın ve `test_files_api.py`'nin kurucu
çağrıları büyüyor. İkisi de aynı turda düzeliyor.

1. Soru kipinde yazan bir iş, akışta `permission` karesi çıkarıyor ve karede aracın adı var.
2. Kapıya bırakılan onay turu sürdürüyor: dosya doğuyor, akış `done` ile bitiyor.
3. Kapıya bırakılan red dosyayı doğurmuyor, ve tur yine de bitiyor.
4. Olmayan bir sohbete verilen cevap 404.
5. Nabız karesi tarayıcının ayrıştırıcısında **hiçbir şey** olarak düşüyor — `event:` taşımıyor.

Beşincisi ön yüz testi değil: `parseFrame`'in bugünkü davranışı zaten öyle, ve bu turda ön yüze
dokunulmuyor. Python tarafında ölçülen şey, karenin `event:` satırı taşımadığı.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `run_tool` ve araçların kendisi | Kapı önlerinde açılıyor, içlerinde değil |
| `MemoryStops` | Uyandırma onun bugünkü `hold`'una veriliyor; sınıf değişmiyor |
| `ends_the_turn` | Kural yerinde; yalnız kipi değişebiliyor |
| Ön yüz | Kart **Madde 102**'nin işi; `dist` derlenmiyor |
| Yönerge metinleri | Yetkiye dair bir cümle girmiyor *(Madde 91)* |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
```

Yukarıdaki kırmızılar sayılıyor. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi —
defterin `BRANCH`'i koşu bitince `main`'e dönecek.

Yeni modüller henüz yok, ve bir dosyanın toplanması sırasında patlayan import bütün suite'i
susturuyor. Bu yüzden yeni adlar **testin içinden** import ediliyor — `test_modes.py`'nin bugün
yaptığı gibi, ve sebebi o dosyanın başlığında yazılı.
