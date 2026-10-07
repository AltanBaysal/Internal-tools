# Madde 302 — Üretimin reddi, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m302 test turu](2026-09-21-queen-editor-m302-uretimin-reddi-testler-design.md),
`6c9c919a` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `domain/usecases/queue_references.py`

```
queue_references(store, pool, orders, has_h3, project, prompts, variants) -> kaç iş
```

Sırayla: proje var mı, **H3 kurulu mu**, prompt listesi okunabiliyor mu *(`parse_prompts`)*, varyant
1–26 arası mı *(`start_batch`'in kendi kuralı)*, **havuzda referans var mı**, ve **boşluk var mı**
*(`references.gaps`)*. Hepsi geçerse bugün **sıfır** dönüyor: doğuran taraf **303**'ün.

Kontrol sırası bir kullanıcının bakacağı sıra: kurulum, sonra kendi yazdığı, sonra havuzun hâli.

`has_h3` bayrağı `main.py`'den geliyor — hangi modelin kurulduğu defterin kararı ve domain config
okumaz. Depolarla birlikte bağlanıyor, presle değil: kurulum bir kere seçiliyor.

**Boşluğun cümlesi hangi satırda olduğunu söylüyor**, çünkü kullanıcı gidip onu kapatacak.

## Kapı ve ekran

`POST …/references/produce` — gövdesinde `prompts` ve `variants`, cevabı `{"added": N}` ve **202**,
fotoğraf üretiminin kendi şekli. Reddin kodu 400, cümlesi domain'den.

`api.js`'e `produceFromReferences`, `useGeneration.queueLayer`'a tek dal: kip **referans** ise o
kapıya gidiyor. Panelin kırmızı kartı sunucunun cümlesini zaten basıyor — 301'de öyle yazıldı.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; `dist` aynı commit'te.
