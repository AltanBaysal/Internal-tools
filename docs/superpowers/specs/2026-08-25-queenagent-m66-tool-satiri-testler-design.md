# Madde 66 — Tool call'lar sohbette görünür · **test turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 66 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Yol haritasının iki cümlesi: *"cevap gelmeden önce hangi dosyanın okunduğu ekranda yazıyor"* ve
*"sayfa yenilendiğinde o satırlar hâlâ duruyor."* Yani iki ayrı iddia — **akarken görünür** ve
**kayıtta kalır** — ve ikisi ayrı ayrı kanıtlanmalı. Biri olmadan öteki maddeyi kapatmıyor:
akarken görünüp kaybolan satır kullanıcının "sonradan da göremiyorum" şikâyetini çözmüyor.

## Karara bağlananlar

**Kayıt ne taşır: aracın adı ve hedefi** *(kullanıcı kararı, 25 Ağustos — seçenek A)*.
`read_file · aylin.json`. Sonuç saklanmaz: okunan dosyanın içeriği zaten diskte duruyor ve
FOUNDATION hiçbir kaydın başkasının cevabını tekrarlamamasını istiyor. Kopyalanırsa aynı metin iki
yerde yaşar ve birinde bayatlar.

**Nerede durur: mesajın üstünde, `calls` diye.** `files` alanının bire bir aynısı — boşken diske
hiç yazılmaz, okunurken yoksa boş sayılır. Bu yüzden **göç gerekmiyor**: bugünkü sohbetler alanı
taşımıyor ve taşımadıkları için bozulmuyorlar.

**Hepsi kaydedilir, `create_file` dahil.** Dosya doğuran çağrı ekranda ayrıca bir kart çiziyor, ama
kart başka bir soruya cevap veriyor — *dosya burada, aç*. Satır ise *cevap şunu yaptı* diyor.
Kuralı "dosya doğuranlar hariç" yapmak, kaydı okuyanın ezberlemesi gereken bir istisna üretirdi.

**Hedef, sunucunun çözdüğü addır.** Model `aylin.json` isteyip ad çakıştığı için dosya
`aylin-2.json` olarak yazıldıysa kayıtta `aylin-2.json` durur. Kayıt ne olduğunu söyler, modelin ne
dilediğini değil.

**Sonuç kaydedilmez.** Var olmayan bir dosyayı isteyen çağrı da olmuş bir çağrıdır ve öyle
yazılır; başarısız olduğu ayrıca işaretlenmez. Kullanıcının seçtiği kayıt "araç adı + dosya adı".

**`list_files`'ın hedefi yoktur.** Alan boş kalır, uydurulmuş bir hedef yazılmaz.

**Satır, araç koştuktan sonra doğar.** Hedef o ana kadar kesin değil — dosya kartının adının
neden çalıştıktan sonra belli olduğuyla aynı sebep.

## Yazılacak testler

### Arka uç

**`test_tools.py` — çağrı kendi hedefini söyler**

1. `read_file` çalıştığında sonucun yanında hedef olarak temizlenmiş dosya adı döner.
2. `create_file` ad çakıştığında hedef olarak **yazılan** adı döner, modelin istediğini değil.
3. `list_files` hedefsiz döner.
4. `edit_file` ve `build_prompts` hedeflerini döner.

*Neyi tutuyor:* adın nasıl temizlendiği ve çakışmanın nasıl çözüldüğü zaten burada yaşıyor; hedefi
başka bir yerde hesaplamak o kuralı ikinci kez yazmak olurdu.

**`test_stream_answer.py` — akışta ve kayıtta**

5. Araç çağıran bir tur, her çağrı için sıraya bir çağrı parçası koyar; parçalar araç adını ve
   hedefi taşır.
6. Tur bittiğinde diske düşen cevap mesajı aynı çağrıları `calls` olarak taşır.
7. Hiç araç çağırmayan bir cevabın `calls`'ı boştur.
8. Aynı dosya iki kez okunursa iki çağrı kaydedilir — `files` alanının aksine burada tekrar
   ayıklanmaz, çünkü iki kez okumak gerçekten iki adımdır.

**`test_file_chat_store.py` — diskteki şema**

9. Çağrısı olan mesaj `calls` alanıyla yazılır; olmayan mesajda alan **hiç yoktur**.
10. `calls` taşımayan eski bir sohbet okunduğunda mesajlar boş `calls` ile gelir, patlamaz.

**`test_chats_api.py` — dışarı çıkan şekil**

11. Cevap akışı her çağrı için bir olay yayar ve olay araç adını ve hedefi taşır.
12. Sohbetin JSON'u mesajların `calls` alanını taşır.

### Ön yüz

**`ChatScreen.test.jsx`**

13. Kayıtlı bir mesaj çağrılarını satır satır çizer: her satırda araç adı, hedefi olan çağrıda
    hedef de.
14. Hedefsiz bir çağrı yalnız araç adını çizer, boş bir ayraç bırakmaz.
15. Çağrısı olmayan mesaj hiçbir şey çizmez — boş bir liste kabı bile.

**`useChat` (kendi test dosyasında)**

16. Akış sırasında gelen çağrı olayı ekranda o an görünür.
17. Akış bitip sunucunun kaydı geldiğinde satırlar kaybolmaz — kayıt aynı çağrıları taşıyor, yani
    akıştan çizilenler bırakılır ve kaydınkiler çizilir.

*17 neden ayrı:* bugün dosya kartları tam olarak böyle çalışıyor — akıştan çizilenler cevabın
kaydı gelince bırakılıyor. Çağrılar için aynı devir yapılmazsa satırlar cevabın son anında bir
kez yanıp sönerdi.

## Kapsam dışı

Çağrının aldığı bütün değerler *(kullanıcı A'yı seçti: ad ve hedef)* · sonucun gösterilmesi ·
başarısız çağrının ayrıca işaretlenmesi · satırın görünümü *(tasarım sonra gelecek — koşunun kaydına
bakılsın)* · durdurma *(Madde 67)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

On yedi testin tamamı kırmızı: bugün ne `calls` diye bir alan var, ne çağrıyı taşıyan bir akış
parçası, ne de onu çizen bir satır. Kırmızı görüldükten sonra **kırmızı hâliyle commit'lenir**;
`skip` ve `xfail` yok.
