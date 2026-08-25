# v14 · Görev 23 — Proje adı değiştirme · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-23-proje-adi-testler-design.md) ·
kırmızı commit `70aab25` (motorda 12, ön yüzde 8 kırmızı).

## 1 · Tutamak işçinin üstünde duruyor

Kırmızı turda tutamak ayrı bir nesne olarak tarif edilmişti; sorusu şuydu: koşan işe nasıl
ulaşacak? Her yol `run_queue`'ya çıkıyor, ve oraya giden altı kullanım da `main.py`'de ayrı ayrı
bağlanmış — hepsine yeni bir argüman eklemek altı imza, altı bağlama ve bir sürü test demekti.

**Zaten paylaşılan bir nesne var: `PhotoRunner`.** İşçinin hangi klasöre yazdığı işçinin kendi
bilgisi, ve `make_job` runner'ı elinde tutuyor. Tutamak runner'ın üstünde duruyor:

```
PhotoRunner.named  →  RunningName
make_job(..., named=None)  →  named = named or runner.named
```

Böylece `run_queue`, `start_batch`, `queue_layer`, `regenerate`, `retry_frame`, `retry_failed`,
`resume_batch` ve `main.py`'deki altı bağlama **hiç değişmiyor**. `named` parametresi yalnız testin
sahte tutamağı için duruyor.

## 2 · `RunningName`

```python
took(name)          # bir koşu bu projede başladı
now()               # adın şu anki hâli — turun başında okunuyor
steady()            # ad, çağıran yazdığı sürece kıpırdamıyor (context manager)
moved(old, new, do) # do() kilidin altında koşuyor ve ad onu takip ediyor
```

Kilit **yeniden girilebilir** (`RLock`): yazan taraf `steady()`'nin içindeyken adı bir kez daha
sorabiliyor ve bu kendi kendini kilitlememeli.

`moved` adı yalnız **o proje** koşuyorsa takip ediyor: kimsenin üretmediği bir projeyi yeniden
adlandırmak işçiyi başka bir yere bakar hâle getirmemeli.

## 3 · Döngü

`make_job` içinde üç yer:

- `snapshot()` ve `summary()` adı `named.now()`'dan alıyor — kapanıştaki dizgeden değil.
- Turun başında `project = named.now()`.
- Yazma bloğu `with named.steady() as project:` — kaydedilen dosya ve kaydın satırı birlikte,
  bölünmeden.

Turun **okuma** kısmı kilidin dışında kalıyor. Sebebi ölçü: okumalar turun ilk milisaniyelerinde
oluyor, render uzun kuyruk, yazma da kilitli. Taşınma render sırasında gelirse — gerçekçi olan bu —
her şey yerli yerinde. İlk milisaniyelere denk gelen kıl payı bir yarışın en kötü sonucu bir karenin
hataya düşmesi, ki döngü onu zaten kaydediyor ve kullanıcı tekrar deneyebiliyor.

## 4 · `follow_rename`

Projelerin aldığı liman, `halt` gibi:

```python
def follow_rename(runner, old, new, move):
    answer = runner.named.moved(old, new, move)
    runner.rename(old, new)
    return answer
```

`PhotoRunner.rename(old, new)` yalnız durumdaki damgayı düzeltiyor — ekran `job.project === project`
diye karşılaştırdığı için bayat bir damga koşuyu kendi sayfasından gizlerdi.

## 5 · Kural ve depo

```python
def rename_project(store, move, old, new):
    error = name_rules.validate(new)          # depoya dokunmadan önce
    if error: raise InvalidName(error)
    if new == old: return                     # kendi adı hata değil, taşınacak bir şey de yok
    answer = move(old, new, lambda: store.rename(old, new))
    if answer is None: raise NameTaken(...)
    if answer is False: raise ProjectMissing(...)
```

`is None` / `is False` — `if not` değil: bir mtime `0.0` olabilir.

`DriveStorage.rename_dir` üç cevap veriyor: başarıda mtime, hedef doluysa `None`, kaynak yoksa
`False`. İki başarısızlığın ayrı gelmesinin sebebi çağıranın onlar için iki ayrı cümlesi olması.

## 6 · Yol

```python
@bp.post("/api/projects/<project>/rename")
```

`InvalidName` → 400, `NameTaken` → 409, `ProjectMissing` → 404, `OSError` → 500 ve işletim
sisteminin kendi cümlesi. Cevap `{"name": <yeni ad>}`: ekranın listeyi yeniden okumaktan başka bir
şeye ihtiyacı yok.

`rename_project` parametresi `delete_project`'in yanına taşınıyor ve varsayılanı kalkıyor.

## 7 · Pencere ikiye bölünmüyor

`NewProjectModal` → **`NameModal`**: bir projenin adını soran pencere. Başlık, açılış değeri, düğme
yazıları ve genişlik çağırandan geliyor. Test dosyası da adıyla birlikte taşınıyor — içeriği aynı,
yalnız bileşenin adı ve prop'ları değişiyor.

Açılışta değer varsa alan **seçili** geliyor: bir tuşa basmak adı baştan yazmaya başlıyor.

Yeni proje penceresi bugünkü **400** pikselinde kalıyor; 380'e inmesi 24. maddenin işi (fark 6).
Yeniden adlandırma penceresi **380** açılıyor.

## 8 · Kart ve ekran

Kartın sağ üstündeki tek düğme iki düğmeye dönüyor: solda nötr kalem, sağda kırmızı çöp, aralarında
4 piksel. **Çöpün rengi bu maddede değişmiyor** — fark 5 tasarımın kendi içinde çeliştiği yer ve
24. maddenin kararı.

Ekran silme durumunun ikizini tutuyor: `renamingName`. Kaydettikten sonra liste yeniden okunuyor —
Drive tek doğru kaynak.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 709 / 527. `dist` aynı commit'te derleniyor.
