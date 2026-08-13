# Queen Editor — Yol Haritası v11

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 2/6
**Öncesi:** [Colab kurulum seçimi](2026-08-13-queen-editor-colab-kurulum-secimi.md) ve
[v10 Görev 1](2026-08-13-queen-editor-v10-gorev-1-uretim-kendi-baslamasin.md) — ikisi de kapandı,
Colab turu sürüyor.

## Neden bu koşu var

Kullanıcı Colab'da üretim denedi. Video prompt'u yazılamadı — xAI anahtarı reddedildi — ve üretim
durdu. Bu arada üç arayüz hatası daha çıktı: video panelinde seçili kare sayısı artmıyor, üretim
durduğu hâlde kareler kuyrukta görünüyor, seçim kalkınca kareler üstündeki halkalar kalıyor. Listede
bekleyen iki küçük madde de var.

Kullanıcı asıl soruyu sordu: **"testler zayıf mı kalıyor, çünkü sürekli hata buluyorum?"** Bakıldı,
cevap kısmen evet. 584 backend + 307 frontend testi var ama bulunan hataların hepsi aynı yerde:
**dikişlerde.** Her test bir parçayı, ona elle verdiğim girdilerle sınıyor; parçaların birbirine
bağlandığı yeri hiçbiri sınamıyor. Video panelinin sayısı "gelen listeyi doğru sayıyor mu" diye test
edilmiş, "doğru liste geliyor mu" diye değil.

Onun için bu koşunun çalışma biçimi değişiyor (aşağıda).

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
**kırmızı bırakır** ve mesajı hangi testlerin neden düştüğünü söyler. Sonra implementasyon: spec →
plan → kodu yaz → commit; takım yeşile döner.

Sebebi: testi kodla aynı nefeste yazınca test kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor. Araya commit sınırı koymak testi davranıştan yazmaya zorluyor — ortada henüz implementasyon
yok ki ondan kopya çekilsin. Yan faydası, implementasyon spec'inin kırmızı bir takıma karşı
yazılması: "bitti" bir kanaat değil, ölçülen bir şey oluyor.

**İstisna yok** — iki satırlık bir silme de iki döngü. Ön yüz değişen her görevde `dist/`
implementasyon commit'ine girer. Kullanıcı en sonda toplu Colab testi yapar; koşu boyunca durulmaz.

## Kapsam sınırı

- **Kurulum maddelerine dokunulmuyor.** Listede duran foto 403, video 403 ve ses maddelerini bu koşu
  kapatmıyor — onları kullanıcının Colab testi kapatacak.
- **"Claude" başlığındaki iki karar dışarıda:** galeri karolarına küçük önizleme ve başarısız karede
  hover karartması. İkisi de kendi tasarımını ister, koşuyu uzatırlar.

## Görevler

### Görev 1 · xAI anahtarı indirmeden önce yoklanır

**Ne olacak:** Defter, dışarıya bakan her şeyi ağır işten önce yokluyor — GitHub token'ı, Civitai
çerezi, disk, GPU — ama xAI anahtarını yoklamıyor. Bu yüzden anahtarın ölü olduğu ancak kurulum,
foto üretimi ve kuyruğa video atıldıktan sonra öğreniliyor. Anahtar da ilk saniyede yoklanacak:
xAI reddederse kendi cevabı basılacak, video kurulacaksa koşu duracak, kurulmayacaksa uyarıp
geçecek. Yapıştırırken sona yapışan boşluk da temizlenecek — bugünkü hatanın olası sebeplerinden
biri o.

**Bağımlılık:** Yok.

**Bitti sayılır:** Geçersiz anahtarla açılan bir koşu, hiçbir şey inmeden, xAI'ın kendi cümlesiyle
duruyor. Anahtarsız foto koşusu eskisi gibi çalışıyor.

### Görev 2 · Video panelinde seçili kare sayısı görünür

**Ne olacak:** Galeride kare seçilince video paneli sayıyı görmüyor. Düzeltilecek. Bu görev aynı
zamanda koşunun test zeminini kuruyor: ekranı gerçek gibi kurup kullanıcı gibi kullanan testler —
kare seç, sayıyı oku. Sonraki iki görev bu zemine yaslanıyor.

**Bağımlılık:** Yok, ama 3 ve 4 buna bağlı.

**Bitti sayılır:** Galeriden kare seçmek video panelindeki sayıyı değiştiriyor, ve bunu ekranı
uçtan uca kuran bir test söylüyor.

### Görev 3 · Duran üretim kuyrukta görünmez

**Ne olacak:** Hata üretimi durdurduğu hâlde kareler hâlâ "video kuyrukta" diyor. Duran bir kuyruk
kuyrukta görünmeyecek. Hatanın arayüzde mi sunucuda mı olduğu kendi spec'inde çıkacak — test
davranışı yazacağı için ikisinde de aynı test geçerli.

**Bağımlılık:** Görev 2'nin zemini.

**Bitti sayılır:** Üretim durdurulduktan sonra hiçbir kare kuyrukta bekliyormuş gibi görünmüyor.

### Görev 4 · Seçim kalkınca ✓ halkaları da kalkar

**Ne olacak:** Kareler seçilip sonra seçim kaldırılınca alttaki çubuk kayboluyor ama karelerin
üstündeki halkalar duruyor; seçim sürüyor mu bitti mi anlaşılmıyor. Seçim biterse halkalar da
bitecek.

**Bağımlılık:** Görev 2'nin zemini. Görev 5'ten önce olmalı: halka önce doğru davransın, sonra
adres değiştirsin.

**Bitti sayılır:** Seçim kalktığı anda karelerde seçimden eser kalmıyor.

### Görev 5 · Kare köşeleri yeniden dağıtılır

**Ne olacak:** Durum yazısı ("foto kuyrukta") tasarımın dediği yere, sol üste geçecek. ✓ seçim
halkası sağ üste taşınacak; halka belirdiğinde sıra numarası kaybolacak — seçim yaparken bakılan şey
resim, numara değil. Böylece hiçbir şey fare gelince yerinden oynamıyor.

**Bağımlılık:** Görev 4.

**Bitti sayılır:** Yazı sol üstte, halka sağ üstte, halka görünürken numara görünmüyor ve kartın
içinde fare gelince yer değiştiren hiçbir şey yok.

### Görev 6 · LLM açıklamaları iki panelden de kalkar

**Ne olacak:** Video ve ses panellerinin altındaki "prompt'u otomatik: LLM yazar" açıklaması
kalkacak. İkisi birden — iki panel tek bileşen ve tasarım birebir aynı olmalarını istiyor, birini
bırakmak onları görünür şekilde ayırırdı.

**Bağımlılık:** Yok.

**Bitti sayılır:** İki panelin de altında açıklama yok.

## Sonraki koşuya kalanlar

Galeri karolarının küçük önizlemeleri ve başarısız karede hover karartması — ikisi de tasarım kararı
bekliyor. Bir de kullanıcının Colab turundan çıkacak yeni maddeler.
