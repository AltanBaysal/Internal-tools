# Madde 306 — Ok tuşları, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m306 test turu](2026-09-21-queen-editor-m306-ok-tuslari-testler-design.md),
`b2b6918b` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Tek dosya, tek kural

`PhotoDetail.jsx`'in tuş dinleyicisi, olayın **nereden geldiğine** bakıyor:

```
if (typing(e.target)) return;      // the text owns its own keys
```

`typing` küçük bir yardımcı: `input`, `textarea`, ya da `contenteditable`. Üçü de tarayıcının kendi
metin gezinmesini çalıştıran şeyler, ve sayfanın kısayolu onların üstüne binmiyor.

Modal kontrolü olduğu yerde duruyor: o da aynı cümlenin başka bir hâli — klavyenin sahibi o an kim
ise, tuş onun.

**Üç tuş, tek kural.** Escape'e istisna açılmıyor: yazarken kaçmak isteyen önce kutudan çıkar.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; `dist` aynı commit'te.
