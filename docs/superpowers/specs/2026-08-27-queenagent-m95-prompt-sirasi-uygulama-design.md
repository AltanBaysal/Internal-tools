# Madde 95 — Promptun sırası düzelir, kişi sayısı yerine oturur · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 95 ·
**Turun birincisi:** [test turu](2026-08-27-queenagent-m95-prompt-sirasi-testler-design.md) —
dokuz kırmızı commit'lendi *(`397cb77`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder; testler yerinde ve değişmiyor.

---

## Değişen tek dosya

`build_prompts.py`, ve içinde tek bir yer: bir karenin parçalarının dizildiği döngü. Uçlar, araçlar,
skill metinleri, ön yüz — hiçbiri bu maddede açılmıyor.

## Bugünkü diziliş

```
quality → her karakter + kıyafetleri → mekân → action → camera
```

Karakterler tek bir döngüde, hepsi mekândan önce.

## Yeni diziliş

```
quality → people → ilk karakter + kıyafetleri → mekân → action → camera → kalanlar + kıyafetleri
```

Karakter listesi **başından bir tane** ayrılıyor: ilk yazılan öne, geri kalanların hepsi sona.
Ayıran şey bir alan değil, listenin kendi sırası *(K1)* — yani kod bir isim aramıyor, yalnız
bölüyor.

## Karakter bloğu bir yardımcıya çıkıyor

Bir karakter ile kıyafetlerini yazan üç satır artık iki yerde lazım: bir başta, bir sonda. Kopya
yerine kendi yardımcısına çıkıyor, ve komşuluk kuralı — kimlik ile kıyafetin yan yana durması —
tek bir yerde yazılı kalıyor.

## Sayı nereden geliyor

Karenin `people` alanından, doğrudan. Kod onu **okumuyor, saymıyor, doğrulamıyor** — kalite
etiketlerinin hemen ardına koyuyor, o kadar *(K7, K8)*. Alan yoksa boş geçiyor ve `_tags` onu zaten
düşürüyor; `quality` yokken olan neyse bu da o.

## Eksik ad hatalarının sırası

Bir karede hem sondaki karakter hem mekân bilinmiyorsa, hata cümleleri artık promptun sırasıyla
diziliyor — önce mekân, sonra sondaki karakter. Bugün ikisi de karakterlerin arkasından geliyordu.
Kimse bu sıraya bağlı değil: hata bir kare numarası, bir ad ve bilinenlerin listesini taşıyor, ve
hepsi tek seferde çıkıyor. Değişen yalnız iki cümlenin hangisinin önce okunduğu.

## Yorum koda uyduruluyor

Döngünün başındaki yorum bugün *"sıra dosyada değil burada sabit"* diyor ve sebebini söylüyor. Sebep
büyüyor: sıra artık ana karakteri de koruyor — ikinci kişi kameranın ötesine geçtiği için iki tarif
birbirine bulaşmıyor. Yorum bunu söyleyecek hâle geliyor; eski cümle silinmiyor, doğru olduğu kadarı
duruyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `_worn` | İki biçimi okuyan yer; bölme ondan **sonra** oluyor, yani eski düz liste de bölünüyor |
| `_looked_up`, `_tags`, `_quoted` | Arama, birleştirme ve kaçış aynen duruyor |
| `render_module`, `prompts_name` | Çıktının biçimi ve adı bu maddenin işi değil |
| `shots` yedeği | Eski dosyalar listelerini oradan okumaya devam ediyor |
| Karakter tanımındaki `1girl` / `solo` | Kod ayıklamıyor *(K27)*; kural kitabının işi, ve o **Madde 96** |
| Şema metni | `people`'ı anlatan cümle skill metninde değil, **Madde 96**'nın taşıdığı şemada olacak |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

Dokuz kırmızı yeşile döner, var olan yirmi sekiz test yeşil kalır. **İki kırmızı bu maddenin
değildir:** `test_notebook`'un ikisi.

Ön yüz değişmiyor, yani `dist` bu maddede derlenmiyor.
