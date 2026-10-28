# Madde 177 · uygulama turu — Queen Flash ve Queen Pro

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m177-besteci-testler-design.md).
Commit `eba8366` 30 kırmızı bıraktı.

---

## Değişen üç yer

**`models.js`** — iki satır, Queen adlarıyla; `DEFAULT_MODEL` Flash. Dosyanın başındaki yorum artık
adların **yalnız bu dosyanın** olduğunu söylüyor, ve neden: id sağlayıcıya giden ad, `client.py`
onu `model` alanı olarak gönderiyor.

**`ModelPicker.jsx`** — tek satır:

```js
const selected = model || DEFAULT_MODEL;     // was: MODELS.find(...)?.id ?? DEFAULT_MODEL
```

Eskisi tanımadığı id'yi varsayılana çeviriyordu. Bugüne kadar görünmezdi; Grok listeden çıkınca
görünür oluyordu: düğme *"grok-build-0.1"* yazarken menü Queen Flash'ı işaretlerdi. Modülün kendi
ilkesi *"işaret ile düğme aynı şeyi söyler"*, ve satır şimdi onu tutuyor.

**`config.py`** — `DEFAULT_MODEL` Flash. `MODELS`'in Grok satırı **duruyor**: 175 onu prompt yazıcı
olarak bağlıyor, ve menüde olmamak ile bağlı olmamak iki ayrı şey.

## `dist`

Ön yüz değişti, dolayısıyla `dist` **bu commit'te** derlendi. Defterin tarafında görünmesi için
başka yol yok: notebook depoyu klonluyor ve hiç derlemiyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **801 · 589 · 739 · 591**, hepsi yeşil. 30 kırmızının hepsi döndü; ön yüz 586'dan 589'a çıktı,
   üç yeni test *(menü iki satır, yalnız-rol modelin kimliği, işaretlenmeyen satır)*.
3. `npm run build --prefix queen-agent/frontend` koşuldu ve `dist` aynı commit'te.
