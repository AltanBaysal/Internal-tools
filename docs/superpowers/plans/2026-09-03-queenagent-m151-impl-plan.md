# Madde 151 — Uygulama turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m151-kapi-uygulama-design.md) ·
**Tur:** uygulama *(yeşile götürür)*

Yalnız kod, hepsi `tools.py`'de. Hiçbir teste dokunulmuyor.

---

## 1. Soru ve cevap, tek yerde

- `is_structure(name)` — temizlenmiş ada bakar, `.lower()` ile uzantıyı sorar.
- `_NOT_AS_TEXT` — ret cümlesi, dosya adını alan tek bir şablon.
- İkisi de modül seviyesinde, `safe_name`'in yanında: aynı soruyu iki araç soruyor ve iki kopya ilk
  değişiklikte ayrışır.

## 2. `create_file`

- Ret, **ad kontrolünden önce** giriyor: temizle → yapı dosyası mı → ad dolu mu → yaz.
- `ToolResult(_NOT_AS_TEXT.format(...), None, wanted, "Refused")`.

## 3. `_edit`

- Dosya okunduktan **sonra**, `old` kontrolünden önce tek bir adım:
  yapı dosyası **ve** içeriği `json.loads` ile okunuyorsa → ret.
- Parse denemesi bir kontrol; sonucu kullanılmıyor, yalnız düşüp düşmediğine bakılıyor.

## 4. `create_file`'ın açıklaması

- Bugün *".md bir belge için, .json bir yapı dosyası için"* diyor. `.json` çıkıyor — araç artık onu
  yazamıyor, ve yazamadığı bir şeyi öneren açıklama modeli kapalı kapıya gönderir.

## 5. Koş ve yeşili gör

```
python -m pytest queen-agent -q
```

698 olmalı. Üç testin — okuma, tamir, `add_frames` — yeşil kalması kapının fazla kapanmadığının
kanıtı; biri kırmızıya dönerse kapı geniş kapanmış demektir.

Diğer üç satır ardışık koşulur.

## 6. Yeşil commit'lenir

`feat(m151): …`
