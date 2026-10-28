# Madde 504 · Düzenleme kutusu büyür — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-1),
504 · v12-1 · **Dal:** `feat/queenagent-v12` · **Sonraki:** 505 · v12-2 (yazma kutusu) aynı parçayı
kullanır · **Kurallar:** [FOUNDATION](../../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Bir soru düzenlenmeye açılınca kutu bugün her mesajda yaklaşık 200 × 76 px, yani 2 satır açılıyor;
480 × 569 px'lik bir balon da o küçük kutuya dönüyor ve yazdıkça büyümüyor. Kullanıcının kararları
*(27 Ekim)*: genişlik sohbetin genişliği, ChatGPT'deki gibi — *"genişlmeninde süt snırı olması alzım
yoksa chate geçmişini göremeyiz"*; üst sınır *"Ekranın %40'ı, yaklaşık 11 satır. ChatGPT'ye yakın."*

**Kabul:** kutu sohbetin genişliğinde açılıyor ve yazının tamamını gösteriyor; yazdıkça büyüyor;
ekranın %40'ına gelince büyümesi duruyor ve yazı kutunun içinde kayıyor.

## Bugün neden küçük

- `.msg` bir sütun ve sorunun tarafında `align-items: flex-end`; çocukları içerikleri kadar geniş.
  `.msg__editing`'in yalnız `max-width: 78%`'i var, genişliği yok. İçindeki `<textarea>`'nın kendi
  genişliği tarayıcının varsayılan `cols`'u (~20 karakter): ~200 px.
- Yükseklik `rows={2}`: iki satır, yazı ne kadar uzun olursa olsun.
- `frontend/src`'de bir `textarea`'yı boyutlayan bir şey yok (`scrollHeight` yalnız `ChatScreen`'in
  liste kaydırmasında okunuyor). Yani yeniden kullanılacak bir parça yok; ilk kez yazılıyor.

## Genişlik

`.msg__editing { width: 100% }` — `max-width: 78%` yerine. Sütun (`.chat__column`, en çok 720 px)
sohbetin genişliği; kutu onun tamamını alıyor. İçindeki `textarea` sütun yönlü flex'in varsayılan
`stretch`'iyle aynı genişliğe uzuyor, `cols` artık bir şey belirlemiyor.

Madde 197'nin kuralı "kutu balonun ölçüsünde" idi (`workspace.css.test.js`'teki *"the field that
corrects a message is the width the message was"*); kullanıcının 27 Ekim kararı onun yerini alıyor, test
yeni kararı tutacak şekilde değişiyor.

## Yükseklik: büyüme parçası

Büyüme tek bir hook: `frontend/src/shared/useGrowingField.js`.

```js
useGrowingField(field, value)
```

- `field` textarea'nın ref'i, `value` içindeki yazı. Ref dışarıdan veriliyor, çünkü yazma kutusu
  (`Composer`) kendi ref'ini zaten tutuyor (`focus` için); 505'te aynı ref'i verir, ikinci bir ref
  açmaz.
- Her `value` değişiminde (ve açılışta) `useLayoutEffect` içinde, ekran çizilmeden: yüksekliği
  `auto`'ya bırakır (kutu `rows` kadar, yani en az 2 satır), `scrollHeight`'i okur, yüksekliği
  `scrollHeight + kenarlıklar` yapar. Kenarlık `offsetHeight − clientHeight` — `app.css`'te her şey
  `box-sizing: border-box`, yani yükseklik kenarlığı da sayar.
- **Ölçerken kaydırma çubuğu yok:** `rows` boyundaki kutuda uzun yazı `app.css`'in 10 px'lik çubuğunu
  gösterir; satırlar daralır, `scrollHeight` bir satır fazla sayar (reviewer Chrome'da ölçtü, ölçümlerin
  ~%8'i). Hook ölçerken `overflowY = "hidden"` yapar, okuduktan sonra `""`'ya döndürür (autosize.js de
  böyle); sınırın ötesinde çubuk yine görünür.
- **Üst sınır CSS'te:** `.msg__editing-input { max-height: 40vh }`. Satır içi yükseklik sınırı geçerse
  `max-height` kazanıyor; `textarea`'nın varsayılan `overflow: auto`'su yazıyı içinde kaydırıyor.
  Sınır JS'te değil, çünkü pencere yüksekliği değişince CSS kendiliğinden doğru kalır, JS'teki bir
  hesap ise yeniden ölçmek ister. 40vh: "ekran" pencerenin görünen alanı; bir çerçeve içinde de
  çerçevenin alanı, yani ekran neyse o.
- **En alt sınır `rows`:** `auto`'da kutu `rows` kadar; yazı kısaysa `scrollHeight` o yüksekliktir. Düzenleme
  kutusu `rows={2}` kalıyor. 505'te yazma kutusunun gönderimden sonra 2 satıra dönmesi de buradan
  geliyor: yazı boşalınca hook yeniden ölçer.
- **Çizilmeyen kutu:** `hidden` bir kutunun `scrollHeight`'i 0. Hook o zaman yüksekliği `auto`'da
  bırakır (rows kadar), 0 px yapmaz. Düzenleme kutusu hiç gizlenmiyor; yazma kutusu `hidden` alabiliyor,
  505 için.

`shared/`'da, çünkü projeyi, sohbeti, mesajı bilmiyor ve bir şey çizmiyor; bir `textarea`'nın
yüksekliğini yazısına uyduruyor, `useShellWidth` gibi. CODE-STANDARD: *"shared/ for what no single
feature owns … nothing in it renders"*.

Neden CSS'teki `field-sizing: content` değil: tek satır CSS, ama Firefox'ta yok; kutu orada bugünkü
gibi 2 satırda kalırdı. Neden gizli bir ayna (grid + `::after`) değil: ölçüm okuması yok ama her kutunun
yazı tipi, dolgusu ve kenarlığı aynada bir kez daha yazılmalı ve iki kutu için iki ayna gerekir; hook bir
dosya ve kutu başına bir satır.

## Ne değişmiyor

- Yazma kutusu (`Composer`) bu maddede değişmiyor; 505 hook'u alır.
- Tuşlar, onay, vazgeçme, boş taslağın onaylanamaması aynı.
- Balon (`.msg__bubble`) aynı: `max-width: 78%`.

## Sınırlar

- Kutu açıkken sohbetin genişliği değişirse (pencere daralır, dosya rayı açılır) hook onu 505'ten beri
  yeniden ölçüyor: QA dar pencerede ilk yüklemede yazma kutusunu 202 px buldu, ve hook kutunun
  genişliğini bir `ResizeObserver` ile izlemeye başladı
  ([505](2026-10-27-queen-agent-m505-yazma-kutusu-design.md#genişlik-değişince-yeniden-ölç)).
- Ölçmek için kutu bir an `rows` boyuna iniyor; sohbet dibe kaydırılmışsa bu, kaydırma konumunu
  kırpabilir. Reviewer Chrome ve Edge'de ölçtü: yükseklik yazılınca tarayıcı konumu kendisi geri
  koyuyor, sohbet zıplamıyor. Bu yüzden hook ataların `scrollTop`'unu saklayıp geri yazmıyor. Firefox
  denenmedi; orada sohbet zıplarsa geri yazma eklenir.
- Ölçüm tarayıcıda: jsdom bir şey yerleştirmez. Testler boyutları bildirir ve hook'un kararını sınar;
  ekranda görünüş QA'nın Playwright denemesi.

## Maliyet

Disk ve ağ: yok. Her tuş vuruşunda ve açılışta: tarayıcıya bir kez yerleşim yaptırır (`scrollHeight`,
`offsetHeight` ve `clientHeight` aynı yerleşimden okunur), ekran çizilmeden.

## Testler

- **Yeni `shared/useGrowingField.test.jsx`** (boyutlar `Element.prototype`/`HTMLElement.prototype`
  üzerinde bildirilir):
  - kutu yazısı kadar uzun, kenarlıklar dahil (`scrollHeight` 120, kenarlık 2 → `122px`);
  - yazı uzayınca uzuyor, kısalınca kısalıyor;
  - çizilmeyen kutu (`scrollHeight` 0) `rows`'unda kalıyor, 0 px olmuyor;
  - `scrollHeight` okunurken `overflowY` `"hidden"`, sonra yine `""`.
- **`EditMessage.test.jsx`:** düzenleme kutusu açılışta yazısının boyunda (hook gerçekten bağlı).
- **`workspace.css.test.js`:** `.msg__editing` `width: 100%` (78% değil); `.msg__editing-input`
  `max-height: 40vh`.

## Bitti sayılır

- Testler yeşil: `npm test --prefix queen-agent/frontend`; `python -m pytest queen-agent -q` (dist testi
  commit'e kadar kırmızı, beklenen).
- `dist` yeniden kuruldu.
- Kabul ekranda (QA, Playwright): kutu sohbetin genişliğinde ve yazının tamamını gösteriyor; yazdıkça
  büyüyor; pencerenin %40'ında duruyor ve içinde kayıyor.
