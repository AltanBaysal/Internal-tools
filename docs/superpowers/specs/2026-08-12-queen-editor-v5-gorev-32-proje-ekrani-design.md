# Görev 32 — Proje ekranı ve silme davranışı

**Maddeler:** 1, 2, 3, 10
**Roadmap:** [v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) · Blok 9
**Fark belgesi:** [v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)

## Sorun

Üç ayrı yerde aynı kök: proje ekranı, kare dili ve üretimin arka planda sürdüğü gerçeğiyle henüz
buluşmadı.

- Proje silme onayı "İçindeki tüm fotoğraflar kalıcı olarak silinir" diyor — video ve ses
  dosyalarından hiç söz etmiyor, çalışan üretime ne olacağını da söylemiyor.
- Söylemiyor, çünkü **olmuyor**: onaydan sonra klasör siliniyor ama motor o projeyi üretiyorsa
  durmuyor. Koşu bir sonraki karede klasörü bulamayınca kendi hatasıyla düşüyor ve kullanıcı
  sildiği projeden bir hata kartı alıyor.
- Kart köşesindeki çöp kutusu kırmızı çerçeveli bir kutu olarak duruyor; kartın kendisi zaten bir
  kutu, ikisi üst üste biniyor.
- "Projeden çık" bir onay penceresi açıyor. Oysa çıkmak hiçbir şeyi bozmuyor: kuyruk sunucuda,
  çıkınca da durmuyor. Pencere, olmayan bir riski soruyor.

## Kararlar

1. **Onay metni ne gittiğini sayar ve üretimin akıbetini söyler** *(madde 1)*:
   `İçindeki tüm kareler — fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı olarak silinir.
   Çalışan üretim durdurulur, kuyruktaki işler atılır. Bu işlem geri alınamaz.`
2. **Silmek önce durdurur, sonra siler** *(madde 2)*. Sıra tersine dönemez: klasörü yarıda kalmış
   bir işçinin altından çekmek, tam da metnin olmayacağını söylediği hatayı üretir.
3. **Durdurma işi foto üretimi özelliğinin.** Projeler özelliği koşucuyu tanımıyor ve tanımayacak
   *(CODE-STANDARD: `feature ↛ feature`)*. `delete_project` bir **port** alır — `halt(project)` —
   ve o portu `main.py` bağlar. Portun arkasındaki yeni kullanım durumu
   `halt_project(runner, interrupt, sleep, project)` foto üretimi özelliğinde yaşar ve kendi
   testleriyle gelir.
4. **Durdurma başka projeyi vurmaz.** Koşucunun işi başka bir projeye aitse `halt_project` hiçbir
   şey yapmaz; kullanıcı «düğün»ü silerken «nişan» koşusunun kesilmesi kabul edilemez.
5. **Durdurma işçinin gerçekten çıkmasını bekler.** Bayrak tek başına yetmiyor: koşu kareler
   arasında biter, aradaki render'ı ComfyUI'ın interrupt'ı keser. Bu yüzden bayrak + interrupt'tan
   sonra koşucu "running" olmaktan çıkana kadar beklenir — **en çok 5 saniye**, onda birlik
   adımlarla. Süre dolarsa yine de silinir: kullanıcının silme isteği bir işçinin inadına
   bırakılamaz. Bekleme bittiğinde `reset()` çağrılır — işçi çıkmışsa durum boşa döner, hâlâ
   çalışıyorsa koşucu isteği reddeder ve durum olduğu gibi kalır. İkincisi kasıtlı: makineyi
   gerçekten elinde tutan bir işçiye "boşta" demek yalan olurdu, ve koşu kendi bittiğinde
   durumunu zaten kendi yazıyor.
6. **Kuyruk ayrıca boşaltılmaz.** Plan dosyası proje klasörünün içinde; klasör gidince kuyruk da
   gider. `reset()` de koşucunun kendi durumunu atar. Metnin "kuyruktaki işler atılır" sözü bu iki
   şeyle karşılanır; üçüncü bir temizleme, silinmiş bir klasöre yazmaya çalışmak olurdu.
7. **Kart köşesindeki çöp kutusu çerçevesiz** *(madde 3)*: zemin yok, kenarlık yok, yalnız kırmızı
   ikon. Yıkıcı standardın kartın içindeki hâli bu; standart "dolu kırmızı olmasın" diyor,
   "çerçeve olsun" demiyor, ve kartın kendi çizgisi zaten orada.
8. **Çıkış onayı kalkar, yerine bilgi balonu gelir** *(madde 10)*. "Projeden çık" doğrudan çıkar.
   Buton **üretim akarken** üstüne gelindiğinde 300 piksellik balon açar: canlı mor nokta +
   "Üretim arka planda sürüyor", altında "Projeden çıksan da pencereyi kapatsan da kuyruk durmaz.
   Döndüğünde biten kareleri galeride bulursun."
9. **Balonun şartı akan kuyruk, bekleyen iş değil.** Balonun cümlesi "kuyruk durmaz" diyor; bu
   yalnız akarken doğru. Duraklamış bir kuyruk zaten durmuş durumda, ona "durmaz" demek yanlış
   olurdu. Şart: `job.status === "running"`. Kuyruk boşken ya da duraklamışken hiçbir şey
   gösterilmez *(madde 10'un kendi cümlesi)*.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| Proje silme onayı | "İçindeki tüm fotoğraflar kalıcı olarak silinir. Bu işlem geri alınamaz." | kareleri ve dosyaları sayan, üretimin akıbetini söyleyen üç cümle |
| Proje silme davranışı | klasör silinir, koşu devam eder ve düşer | koşu durdurulur, çıkması beklenir, sonra klasör silinir |
| Kart çöp butonu | kırmızı çerçeveli kutu | çerçevesiz, zeminsiz kırmızı ikon |
| "Projeden çık" | onay penceresi açar | doğrudan çıkar |
| "Projeden çık", üretim akarken | hiçbir fark yok | üstüne gelince 300px bilgi balonu |

## Testler

Arka uç:

- `halt_project` — koşu bu projeye aitse durdurma ister, ComfyUI'ı keser ve koşucu boşalana kadar
  bekler; iş başka projeye aitse hiçbir şeye dokunmaz; interrupt patlarsa yutulur (ölü bir motor
  silmeyi engellemez); koşucu çıkmıyorsa süre dolunca yine de döner.
- `delete_project` — silmeden **önce** durdurur (sıra iddiası); durdurma çağrısı her silmede
  yapılır; olmayan proje yine `ProjectMissing` verir.
- Rota testi: `DELETE /api/projects/<ad>` durdurmayı tetikler.

Ön yüz:

- `ProjectsScreen.test.jsx` — onay metni birebir.
- `ProjectCard.test.jsx` *(yeni dosya)* — çöp butonunda kenarlık ve zemin yok, rengi `--danger`.
- `ProjectScreen.test.jsx` — "Projeden çık" onaysız çıkar; üretim akarken üstüne gelince balon
  belirir, ayrılınca kaybolur; kuyruk boşken ve duraklamışken balon yok.

## Öz eleştiri

- *Beklemek bir isteği kilitler mi?* — Evet, en çok 5 saniye. Alternatifi (beklemeden silmek) tam
  da madde 2'nin şikâyet ettiği hatayı bırakıyor. Sınırı olan bir bekleme, sınırı olmayan bir hata
  kartından iyidir; süre dolduğunda karar kullanıcının lehine (yine siler) veriliyor.
- *`sleep` neden dışarıdan?* — Testin gerçek zamanı beklememesi için. Aynı zamanda beklemenin bir
  karar olduğunu görünür kılıyor: gizli bir `time.sleep` çağrısı testte fark edilmez.
- *Balon neden `title` özniteliği değil?* — Tasarım genişliğini (300px), canlı noktayı ve iki
  satırı çiziyor; tarayıcının kendi ipucu bunların hiçbirini veremez.
- *Çıkış onayını kaldırmak veri kaybettirir mi?* — Hayır. Çıkmak yalnız adresi değiştiriyor;
  kuyruk sunucuda, kareler diskte. Zaten balonun söylediği de bu.
