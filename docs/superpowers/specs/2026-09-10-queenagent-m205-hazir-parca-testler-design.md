# Madde 205 — hazır parça aracı kalkar · test turu

**Kaynak:** [yol haritasının Madde 205'i](../plans/2026-09-06-queenagent-v8-roadmap.md).

## Ne kanıtlanacak

Madde `read_prompt_piece` aracını **ve** `PROMPT_PIECES` kütüphanesini kaldırıyor. Bu turun işi,
ikisinin de gittiğini gösteren testleri yazmak — kod hâlâ yerinde olduğu için hepsi **kırmızı**
verecek.

Kaldırma testinin deponun kendi kalıbı var: `test_the_schema_tool_is_gone`. Aynı iki iddiayı
taşıyor, ve ikincisi kolay atlanan taraf:

1. Araç `TOOL_SPECS`'te **yok**.
2. Adı taşıyan **eski bir kayıt** hâlâ gelebilir — `run_tool` çökmek yerine cevap veriyor.

## Yazılacak testler

### `test_tools.py` — aracın ve kütüphanenin yokluğu

- **`test_the_ready_piece_tool_is_gone`** — ad `TOOL_SPECS`'te geçmiyor, ve o adla yapılan bir
  çağrı `no tool called` diyor. Şema aracının kalıbının aynısı.
- **`test_the_ready_piece_library_is_gone`** — `prompt` modülünde `PROMPT_PIECES` diye bir şey
  yok. Ayrı bir test, çünkü ayrı bir karar: araç gidince kütüphaneyi **duruyor bırakmak** da bir
  seçenekti ve reddedildi. Aracın yokluğu bunu kanıtlamıyor.

### `test_modes.py` — kipin okuma listesi

- **`test_reading_a_file_is_the_only_call_no_mode_asks_about`** — `READS` tam olarak
  `("read_file",)`. Bugün iki girdisi var; 187 ikinciyi eklemişti, 205 geri alıyor.

  Eşitlik olarak yazılıyor, `not in` olarak değil: `needs_permission` tanımadığı bir araca `False`
  dönüyor, yani var olmayan bir ad üzerinden kurulan bir döngü hiçbir şey iddia etmeden yeşil
  geçer. Bu tuzağı `test_looking_up_a_ready_piece_asks_nobody`'nin kendi yorumu yazmış: *"bu koşu
  on iki testin kırmızıyken yeşil geçtiğini gördü."*

## Bu turda yazılmayanlar

- **Ölecek testler silinmiyor.** `test_tools.py`'deki Madde 187 bölümü *(yedi test)* ve
  `test_modes.py`'deki `test_looking_up_a_ready_piece_asks_nobody` bugün **yeşil**, çünkü kod
  yerinde. Onları silmek uygulama turunun işi; şimdi silmek, kırmızıyı görmeden yeşile boyamak olur.
- **`_frame_seen` ve yazarın sistem mesajı** bu maddenin dışında: `write_missing_actions` onları
  kullanmaya devam ediyor.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
```

Üç yeni test kırmızı, geri kalan süit yeşil. Kırmızı hâliyle commit edilir.
