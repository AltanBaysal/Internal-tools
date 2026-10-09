# Madde 193 · uygulama turu — kopyala düğmesi

**Kaynağı:** [test turu](2026-09-06-queenagent-m193-kopyala-testler-design.md), `fb21811`'de 7
kırmızı.

---

## İki dosya

`FilePanel.jsx` ve `workspace.css`. Artı `dist`, aynı commit'te.

## Düğme `FilePanel`'in içinde, kendi bileşeni olarak

`Refresh` ile `Download` arasına giriyor — okuma sırası **tazele, kopyala, indir**: en hafiften en
ağıra, ve üçü de aynı dosya hakkında.

Kendi bileşeni, çünkü kendi durumu var: ne dediği *(`said`)* ve onu geri alacak sayaç. `FilePanel`'in
gövdesine konsaydı `preparing` ve `failed`'ın yanına üçüncü bir çift `useState` daha girecekti, ve
`Download`'un bekleme durumuyla hiçbir ilgisi yok.

## Yazma basışın kendisinden gidiyor

```
let landing;
try { landing = navigator.clipboard.writeText(text); }
catch (absent) { landing = Promise.reject(absent); }
```

`await` yok, çünkü **pano bir kullanıcı hareketine veriliyor** ve bir tık geç gelen yazma
reddedilebilir. `try` öteki yarısı için: pano nesnesi hiç yoksa çağrı olduğu yerde fırlatıyor,
izin reddedildiyse söz reddediyor — kullanıcının ikisinde de aynı cevaba ihtiyacı var.

Emsal queen-editor'ün `RawOutput`'u ve `PhotoDetail`'in `CopyButton`'ı; iki tool ayrı olduğu için
kod paylaşılmıyor, gerekçe paylaşılıyor.

## Adı cevabı taşıyor

`aria-label` `Copy` → `Copied` / `Could not copy`, ve `SAID_MS` *(2500)* sonra geri. Okunacak kadar
uzun, bir dahaki sefere kadar düğme yine düğme olacak kadar kısa.

Panele **satır eklemiyor**: cevap ikonun adında ve renginde. Başlığın yanında beliren bir kelime
altındaki gövdeyi aşağı iter — okuyucunun altından sayfayı çekmek olur.

Sayaç bileşen sökülürken temizleniyor *(`useEffect`'in dönüş işlevi)*, yoksa kapatılmış bir panelde
`setSaid` çağrılır.

## Metin yokken kapalı, ama duruyor

`disabled={!text}` ve sönük. Gelip giden bir ikon dosya yüklenirken başlığı seğirtir; hiçbir şey
kopyalamayıp kopyaladım diyen bir düğme ise aynı yalanın öteki yarısı.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 7 kırmızı kapanır, `queen-agent` ön yüzü 612 olur; arka
uçlar ve `queen-editor` kımıldamaz. Sonra `npm run build --prefix queen-agent/frontend`, ve `dist`
bu commit'e girer.
