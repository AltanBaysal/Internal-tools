# Madde 144 — CONFIG formu iki grubu ayırır · Tur 1 (test) — Tasarım

**Kaynak:** kullanıcı isteği, 2 Eylül — *"photo modeli ile photo seçimi kısmı iç içe girmiş"*
**Dal:** `feat/v6`
**Bu tur yalnız test yazar.**

## Problem

Madde 140 CONFIG'e üç model kutusu ekledi. Colab bunları üç üretici kutusunun hemen altına çiziyor
ve **aralarında hiçbir şey yok** — formu açan kişi altı kutu görüyor, ikisinin ayrı sorular olduğunu
söyleyen bir işaret yok.

İkinci ve daha büyük yarısı: kutuların ne olduğunu anlatan cümleler `#` yorumu, ve **Colab `#`
yorumlarını forma çizmiyor.** Yani `PHOTO_NOVAANIME` kutusunu işaretleyecek kişi o kutunun ne
indirdiğini okuyamıyor; elindeki tek bilgi değişkenin adı.

## Çözüm: `#@markdown`

Colab `#@param` satırlarını forma çizerken `#@markdown` ile yazılanı da aynı panele koyuyor.
`#@markdown ---` yatay çizgi, `#@markdown ###` başlık veriyor.

Yani ayraç ve başlıklar **kullanıcının gördüğü yere** giriyor, kaynakta kalan bir yoruma değil.

## Metin kopyalanmıyor, taşınıyor

Bugünkü `#` yorumları iki iş birden yapıyor: kullanıcıya *ne seçeceğini*, geliştiriciye *neden öyle*
olduğunu anlatıyor. Bu turdan sonra ikisi ayrılıyor:

| Nereye | Ne | Kim okuyor |
|---|---|---|
| `#@markdown` | ne seçileceği, ne kadar yer kaplayacağı, hangi model ne | formu açan |
| `#` | neden kapalı geldikleri, `/content`'in runtime ile ölmesi | kaynağı okuyan |

Aynı cümleyi ikisine birden yazmak, CLAUDE.md'nin *"bir kopya bayatlayacak olan şeydir"* kuralına
çarpardı. O yüzden kullanıcıya bakan cümleler `#`'ten **çıkıyor**.

## Kırmızıya dönecek üç iddia

1. **İki grup arasında bir ayraç ve bir başlık var, ve ikisi de model kutularının önünde.**
   Konumla ölçülüyor, kelimeyle değil: başlığın metni serbestçe değişebilir, yapı sessizce
   kaybolamaz.
2. **Üretici kutularının da kendi başlığı var.** Birini adlandırıp ötekini adlandırmamak,
   adlandırılmayanı ötekinin parçası gibi gösterirdi — düzeltilen karışıklığın bir satır yukarı
   taşınmış hâli.
3. **Hangi kutunun hangi model olduğu formda yazıyor.** İddia `#@markdown` satırlarının **üzerinde**
   ölçülüyor: adın hücrede geçmesi yetmiyor, çizilen kısımda geçmesi gerekiyor. Bugün geçmiyor,
   çünkü o cümle bir `#` yorumu.

## Testlerin ölçmediği, ve bunun kaydı

**Görüntüyü test söyleyemez.** Takım `#@markdown` satırlarının doğru yerde durduğunu doğruluyor;
Colab'ın onları nasıl çizdiğini yalnız Colab söylüyor. Doğrulaması kullanıcının ekranı, ve bu bir
eksiklik değil — defterin hiçbir hücresi burada koşmuyor.

## Kapsam dışı

- **Ayrı bir hücre.** Görsel ayrımı daha net verirdi ama iki testi birden kırar
  *(kutu-satır eşleşmesi ve hiç-model-seçilmedi kontrolü, ikisi de kutuları CONFIG hücresinde
  arıyor)*, ve tek CONFIG hücresi defterin kendi düzeni.
- **`#@title`.** Hücre başına bir tane, ve hücrenin zaten bir adı var.
- **Kutu adları.** `PHOTO_NOVA3DCG` kod tarafında okunuyor ve üç test onu isimle tutuyor;
  formda okunur olması `#@markdown`'ın işi.
- **Kodun davranışı.** Hiçbir `assert`, liste ya da indirme değişmiyor.
