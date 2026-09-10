# Madde 205 — hazır parça aracı kalkar · uygulama turu

**Kaynak:** [yol haritasının Madde 205'i](../plans/2026-09-06-queenagent-v8-roadmap.md).
**Testler:** [test turunun spec'i](2026-09-10-queenagent-m205-hazir-parca-testler-design.md), üç
kırmızı commitlendi.

## Ne kalkıyor

| Dosya | Ne |
|---|---|
| `prompt.py` | Madde 187'nin yorum bloğu, `PROMPT_PIECES`, `READ_PROMPT_PIECE`, `READ_PROMPT_PIECE_NAME` |
| `tools.py` | Araç şeması, `run_tool` dalı, `_read_prompt_piece`, ve **`folded` import'u** |
| `modes.py` | `READS` tek girdiye iner, yorumu 187'yi anmayı bırakır |

**`folded` import'u da gidiyor**, ve bu kolay atlanan taraf: `naming.folded` `tools.py`'de yalnız
`_read_prompt_piece` içinde çağrılıyordu. Fonksiyon gidince import kullanılmayan bir isim olarak
kalırdı. *(`folded` kelimesi dosyada iki yorumda daha geçiyor ama çağrı değil.)*

## Ölen testler

Bunlar bugün **yeşil**, çünkü kod hâlâ yerinde. Kod gidince kırmızıya dönerler, o yüzden bu turda
silinirler:

- `test_modes.py` — `test_looking_up_a_ready_piece_asks_nobody`. Yerini test turunun yazdığı
  `test_reading_a_file_is_the_only_call_no_mode_asks_about` alıyor.
- `test_tools.py` — Madde 187 bölümünün tamamı: başlık yorumu, `_looked_up` ve `_pieces`
  yardımcıları, ve yedi test *(kütüphanenin boş olmaması, bilinen ad, bilinmeyen ad, adsız çağrı,
  büyük harf, dosyaya dokunmaması, sayı ve `quality` yasakları, tek parametre)*.
- `test_tools.py` — var olan araçları sayan listedeki `read_prompt_piece` satırı ve yorumu.

**Silinen testlerin dersi kayboluyor mu:** hayır, ikisi zaten başka yerde tutuluyor. *"Sayı
karakterin girdisinde"* ve *"quality etiketini kod yazar"* `SDXL_PROMPT_RULES`'un kendi testlerinde
duruyor; burada yalnız o kuralların **kütüphaneye** uygulanışı sınanıyordu, ve kütüphane gidiyor.

## Dokunulmayanlar

- **`_frame_seen` ve `write_frame_system_prompt()`** — `write_missing_actions` ikisini de
  kullanıyor.
- **`naming.folded`** — kendi modülünde kalıyor, başka çağıranları var.
- **Belgenin §6 ve §7'si** — okumanın kod geçişi metinleri toptan indirdiğinde güncellenecek; bu
  tur kodun turu.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Üç kırmızı yeşile döner, silinen testlerle birlikte toplam sayı düşer, ve başka hiçbir test
kırılmaz. Frontend'e dokunulmadığı için o süit değişmeden yeşil kalır.
