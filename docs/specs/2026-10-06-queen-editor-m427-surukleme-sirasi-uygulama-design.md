# Madde 427 — Bir satırı sürüklemek öteki satırların sırasını silmesin, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 427 · **Tur:** 2/2 — kod, takım yeşile döner.
**Testler:** [m427 test turu](2026-10-06-queen-editor-m427-surukleme-sirasi-testler-design.md),
`8fcfb1e5` ile kırmızı commit'lendi — kurallar ve sebebin izi orada.

**Kullanıcıdan gereken:** yok.

## Sebep — kanıtlandı

**`save_reference_order` sıra belgesini yalnız gönderilen satırlardan kurulan yeni bir sözlükle
baştan yazıyor, belgede kayıtlı olanı okumadan
*([save_reference_order.py:24-25](../../queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py))*;
ekran ise yalnız sürüklenen satırı gönderiyor:** öteki satırlar belgeden düşüyor, ve `placed` onları
ad sırasıyla diziyor.

**Kanıt:** test turunun iki testi kullanıcının yolunu gerçek kapıdan ve sahte portlardan yürüdü, ve
ikisi de tam bu yerden kırmızı döndü — başka hiçbir test kırmızı değil: kapıda videolar
sürüklenince `('ayse.png', 1)`, use case'te belgede yalnız `{'video': ['bir.mp4', 'iki.mp4']}` —
`picture` ve `audio` satırları yok.

## Yaklaşımlar

1. **Seçilen — sunucu belgeyi okur, yalnız gönderilen satırları değiştirir.** Gönderilen her satır
   bugünkü süzgeçten geçer *(havuzda duran adlar, tekrar edenin ilki)*; gönderilmeyen satırlar
   belgede olduğu gibi kalır. `add_references`'ın ve `remove_reference`'ın zaten yaptığı: belgeyi
   oku, kendi işini yap, yaz. Ekran ve kapı değişmez.
2. *Elendi —* ekranın üç satırı birden göndermesi: kural tarayıcıya girer *(FOUNDATION 4)*; eski
   bir sekme başka bir sekmenin yüklediği dosyaları öteki satırların eski hâliyle ezerdi; ve sunucu
   gönderilmeyeni yine silerdi — sıra gönderen her yeni çağıran aynı hatayı tekrar ederdi.
3. *Elendi —* sürüklemede bütün satırları havuzda o an durduğu gibi yazmak: kimsenin yazmadığı
   satırların ad sırasını belgeye dondururdu — 414'ün uygulama spec'inin ikinci yaklaşımında elenen
   yol.
4. *Elendi —* öteki satırların belgedeki ölü adlarını da süzmek: `placed` onları saymıyor
   *(madde 321)*, o satırın kendi yüklemesi ya da silmesi temizliyor *(madde 414)*; bir parça daha,
   görünen bir fark yok.

## Dosyalar

### `domain/usecases/save_reference_order.py`

`known` hesaplandıktan sonra, yazma:

```python
order_now = orders.read(project)
# dict.fromkeys keeps the first of any repeated name, and the order they came in.
order_now.update({kind: [name for name in dict.fromkeys(names) if name in known]
                  for kind, names in order.items()})
orders.write(project, order_now)
```

- **Okunan belge bozuksa** `read` boş döner *(DriveReferenceOrderStore'un kuralı)*, ve yazılan
  yalnız gönderilen satır olur — bugünkü davranış.
- Modülün belgesi yeni kuralı ve sebebini söyler *(madde 427)*: ekran yalnız sürüklenen satırı
  gönderiyor, ve gönderilmeyen satır kayıtlı sırasında kalır.

### Doğruluğunu yitiren belgeler

Yok. `reference_order_store.py` *("A drag writes it")*, `remove_reference.py` *("the way a dragged
one does")*, `references.placed`, `api.js`'in ve `ReferencePanel.jsx`'in *"the whole row goes
down"*'u bugün de doğru.

## Bilinçli olarak yapılmayan

- Ekran, kapı, `placed` ve sıra deposu değişmiyor.
- `dist` kurulmaz — kaynak kodda frontend değişmiyor; yol haritasına dokunulmaz.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
