# Queen Editor v8 · Görev 1 — Ses motoru gerektiğinde kurulsun

**Tarih:** 2026-08-13 · **Yol haritası:** [v8](../plans/2026-08-13-queen-editor-v8-roadmap.md) · Görev 1
**Karar sahibi:** kullanıcı (2026-08-13) — üç soru soruldu, üçü de cevaplandı.

## Problem

Ses motoru MMAudio, ComfyUI grafiği değil; uygulamanın kendi sürecinde çalışan bir **kütüphane**.
Bugün onu defter kuruyor: her Run all'da klonluyor, `pip install -e` ediyor ve bir kere import
ederek doğruluyor. Sesi hiç kullanmayacak bir tur da bu bedeli ödüyor.

Ağırlık dosyası ise v6'dan beri Üreticiler panelinin işi. Yani ses üreticisi bugün **iki yerden**
kuruluyor, ve panelin "kurulu" cevabı bunun yalnız yarısını sayıyor: defter koşmamışsa kütüphane
yokken panel "✓ kurulu" diyebiliyor.

## Karar

Ses üreticisinin kurulumu tek yerden yapılır: **Üreticiler panelindeki "Kur"**. O düğme önce
kütüphaneyi, sonra ağırlıkları kurar. Panelin "kurulu mu" cevabı ikisini birden sayar.

Elenen seçenek: ilk ses işinin kütüphaneyi kendi kurması. Kimse düğmeye basmadığı için kurulum
üretimin ortasında olurdu ve o sırada ekran ilerlemiyormuş gibi görünürdü. Ses artık foto ve
videoyla aynı kuralda: kurmadan iş başlamaz — kuyruk o işi bekletir, bu davranış zaten var.

## Tasarım

### Üreticinin ikinci tür ihtiyacı: kütüphane

Bugün bir üretici yalnız **dosya** istiyor (`GROUPS`: klasör + ad + adres). Ses ikinci bir tür
istiyor: bu sürecin içine kurulan kod. İkisi farklı sorulara cevap verdiği için ayrı kalıyorlar —
biri "diskte şu dosya var mı", öteki "bu süreç şu modülü görüyor mu".

`model_groups.py` içine, `GROUPS`'un yanına:

```
LIBRARIES = {
  "audio": [{"module": "mmaudio",
             "repo":   "https://github.com/hkchengrex/MMAudio.git",
             "folder": "MMAudio"}],
}
```

Foto ve videonun kütüphanesi yok — onların motoru ComfyUI, ve o defterde kalıyor.

### Yeni port: `Libraries`

Domain iki soru soruyor, ikisini de bir port cevaplıyor (`data/` katmanında `PipLibraries`):

- `present(module) -> bool` — bu süreç modülü görüyor mu. Ucuz olmalı: panel bunu her yoklamada
  soruyor. `importlib.util.find_spec` bakar, modülü **çalıştırmaz**.
- `install(repo, folder, module)` — klonlar, kurar, ve kurulanı doğrular. Başarısızlıkta aracın
  kendi çıktısıyla hata fırlatır (uydurma sebep yok — repo kuralı).

Kurulum yöntemi defterinkinin aynısı, kelimesi kelimesine: `git clone --depth 1` + `pip install -e .`
+ ayrı bir süreçte `import mmaudio` denemesi. CODE-STANDARD'ın kuralı bu: defterden gelen kurulum
makinesi **kanıtlanmış olduğu için** birebir kopyalanır. `-e` de aynı sebeple duruyor — paket
klonlandığı yerde kalır, güncellemek için `git pull` yeter.

Klonun kökü `config.py`'de: `LIB_ROOT`, varsayılanı ComfyUI kökünün bir üstü. Colab'da bu `/content`
demek, yani bugün defterin klonladığı yerin aynısı: `/content/MMAudio`. Yeni bir ayar penceresi
açmamak için mevcut bilinen kökten türetiliyor.

### Kurulum sırası

`install_producer` önce kütüphaneleri, sonra dosyaları geçer. Sebep: kütüphane üreticiyi
kullanılabilir yapan şey, ve başarısızlığı dakikalarca sürecek indirmelerden **önce** görülmeli.
Kuyruğun kuralı burada da geçerli: zaten olan tekrar kurulmaz.

Adım adım:

1. Ne kütüphane ne dosya tanımlıysa — bugünkü hata aynen: "… için indirilecek dosya tanımlı değil."
2. Eksik her kütüphane için: ekrana adını yaz → kur → kurulumdan sonra **tekrar sor**.
3. Kurulum bitti ama süreç modülü hâlâ görmüyorsa: dur ve söyle — *"… kuruldu ama bu süreçte
   görünmüyor — uygulamayı yeniden başlat."*
4. Eksik her dosya için: bugünkü davranış (anahtar kontrolü, indirme, ilerleme).

### "Kurulu mu" sorusu

Bir üretici, tanımlı **her** dosyası diskteyse ve tanımlı **her** kütüphanesi bu süreçte
görünüyorsa kuruludur. Hiçbiri tanımlı değilse kurulu değildir — bugünkü kural, kapsamı genişledi.

Ağırlık dosyası yerinde ama kütüphane yoksa ses üreticisi **kurulu değil**: bugün panelin yalan
söylediği tek durum buydu.

### Ekran ne söylüyor

Panelin "şu an ne oluyor" alanı bugün `file` adını taşıyor ve indirilen dosyayı yazıyor. Artık
oraya kütüphane adımı da düşeceği için alan `step` oluyor: kurulmakta olan şeyin adı, dosya ya da
kütüphane. Ön yüz onu olduğu gibi basıyor — kural sunucuda, ekran görüntüleyici
([FOUNDATION 4](../../../queen-editor/FOUNDATION.md)).

Yeniden başlatma cümlesi de yeni bir kutu istemiyor: satırın zaten olan `error` alanından, son
denemenin kendi sözleriyle çıkıyor.

## Ne test edilir, ne edilmez

Kararların hepsi domain'de, sahte portlarla test edilir: sıra, atlama, durma, "kurulu mu" cevabı,
ekrana yazılan adım, yeniden başlatma cümlesi.

`git` ve `pip`'i gerçekten çalıştıran `PipLibraries` test edilmez — ComfyUI istemcisi, ffmpeg
dışa aktarıcısı ve MMAudio örnekleyicisi gibi dış dünya. Sahtesi yalnız sahteyi test ederdi
([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)).

## Kabul edilen bedel

Defterin fail-loud import denemesi kalkıyor. Bozuk bir kurulum artık Run all'da değil, "Kur"a
basıldığında görülüyor — ama aynı denemeyi kurulumun son adımı yaptığı için hata yine kurulum
anında ve aracın kendi sözleriyle çıkıyor, kırk dakika sonraki bir render'da değil. Kullanıcı bu
bedeli bilerek kabul etti: karşılığında defter yalnız uygulamanın koşması için gerekeni kuruyor.

## Dokunulan dosyalar

| Dosya | Ne oluyor |
|---|---|
| `features/producers/domain/model_groups.py` | `LIBRARIES` tablosu |
| `features/producers/domain/ports.py` | `Libraries` portu (yeni dosya) |
| `features/producers/domain/usecases/install_producer.py` | önce kütüphane, sonra dosya; yeniden başlatma cümlesi |
| `features/producers/domain/usecases/list_producers.py` | kurulu mu sorusu kütüphaneyi sayar; `file` → `step` |
| `features/producers/data/pip_libraries.py` | klonlayan/kuran sınıf (yeni dosya) |
| `backend/config.py` | `LIB_ROOT` |
| `backend/main.py` | portu bağla, iki kullanıma da geçir |
| `frontend/.../InstallCard.jsx`, `ProducersPanel.jsx` | `file` → `step` |
