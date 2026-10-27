# Madde 352 — Dolan sohbette *burada devam et* · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m352-dolu-sohbet-testler-design.md) ve
kırmızı testleri (`5a9779c1`). Bu tur o testlerin söylediğini yazar, fazlasını değil.

## Sunucu

`routes.py`'nin `_chat_json`'u `"full": is_full(chat)` taşır, `trimmed`'ın yanında. `is_full` zaten
içeri alınmış; kural `chat.py`'de kalır, route yalnız aktarır (CODE-STANDARD: presentation iş kuralı
taşımaz). Yeni dosya, yeni alan diskte yok — kayıt diskten her okunuşta hesaplanır, ve CODE-STANDARD'ın
tablosu değişmez.

## Ön uç

**`FullNotice.jsx`, yeni** — bildirimin kendisi, 344'ün bölüşüyle: mesajın parçaları gibi, ekranın
bir parçası kendi dosyasında. Aldıkları: `gauge` (çizilmiş çember, Composer'ın aldığı gibi),
`onNewChat`, `onContinue`. Çizdiği, tasarımın `fullNotice`'i:

```
div.full
  div.full__text › p.full__line "This chat is full." · p.full__detail "Continue here sends only …"
  div.full__actions › div.composer__gauge {gauge} · button.ghost.full__new "New chat" · button.ghost.full__continue "Continue here"
```

**`ChatScreen.jsx`:** iki yeni özellik, `onNewChat` ve `onContinue`. `.chat__composer` içinde
`chat.full` ise önce `FullNotice`; Composer her zaman çizilir, `hidden={chat.full}` ile. Composer
`hidden`'ı kendi kök `div`'ine koyar — sarmal bir `div` yerine: kutunun bütün bloğunu bir kademe içeri
almak, aynı dalgada kutuya dokunan 355'le çakışırdı. Çember bir kez kurulur ve ikisine de verilir. Neden gizli, kaldırılmış değil: test spec'inin
1. kararı — taslak ve 349'un kutuya bağlı Try again'i.

**`useChat.js`:** `trim()` — `POST /api/projects/<p>/chats/<c>/trim` gövdesiz, sonra kaydı yeniden
okur (`version`'ın yolu), ve `refused`'ı temizler; ret "sohbet dolu" diyordu. Kapının reddi
`setError(failure.message)`, `version` gibi. `error` temizlenmez: cevap gelmediyse soru hâlâ cevapsız,
ve kartın Try again'i kırpmadan sonra işe yarar.

**`App.jsx`:** `onNewChat={openDraft}` — kenar çubuğunun aynısı; `onContinue={chat.trim}`.

**`workspace.css`:** `.full`, `.full__line`, `.full__detail`, `.full__actions` — tasarımın `kit.css`'inden,
`.composer`'ın arkasına. `.full` kutunun kendi şekli (`surface`, `line` çerçeve, 14 köşe,
`14px 16px 10px`, aynı gölge) ve `.chat__composer .composer`'ın 720 genişliği; `.full__actions` sağa
dayalı, 8 aralıklı, `6px` üst boşluk — çemberi sola `composer__gauge`'in `margin-right: auto`'su iter.
Yeni renk yok: `#6b6259` dosyada zaten var (seçicilerin ve çemberin sözünün rengi).

## Dokunulmayanlar

- `ContextGauge.jsx` değişmez: çember dolu sohbette zaten `This chat is full` diyor
  ve yanına söz koymuyor (343).
- Odak `Continue here`'den sonra kutuya verilmez (test spec'inin 3. kararı).
- `dist` bu turda derlenmez; conductor'ın işi.

## Nasıl görülür

Dört satır, paralel: dördü yeşil.
