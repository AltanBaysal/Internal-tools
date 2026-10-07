# Madde 131 · Tur 2 (uygulama) — Tasarım

**Testler:** [2026-08-29-queenagent-m131-satir-numarasi-testler-design.md](2026-08-29-queenagent-m131-satir-numarasi-testler-design.md)
**Kırmızı commit:** `3b19a0c` · **Dal:** `feat/queenagent-m123-skill-rewrite`.

## Ne yazılıyor

Üç dokunuş, ve üçü de gösterme anına ait — diske hiçbir şey eklenmiyor.

### 1. `numbered()` doğar *(`tools.py`)*

Bir metni `cat -n` biçimine çeviren saf fonksiyon: numara altı karakterlik alana sağa yaslanır,
sekme, satır. `splitlines()` üstünde döndüğü için boş metin boş dönüyor — sıfır satır, sıfır
numara, ve `1` yazan hayalî bir satır doğmuyor.

`tools.py`'de duruyor çünkü biçim aracın cevabının bir parçası, ve `stream_answer` zaten bu
modülden okuyor.

### 2. `read_file` numaralı döner, `outcome` değişmez

`ToolResult`'ın metni `numbered(content)` olur. Sayım ham içeriğin satırlarında kalır: `outcome`
dosyanın kaç satır olduğunu söylüyor, gösterilen metnin ne kadar geniş olduğunu değil.

**Şema branch'i ellenmiyor.** `read_prompt_structure_schema` ham `SCHEMA` döndürmeye devam eder —
numara çapa seçmek için var, ve şemaya çapa yazılmıyor.

### 3. `edit_file`'ın açıklaması köprüyü kurar

Cümle *"match what is on disk now"* ile *"read the file first"* arasına giriyor: **without the
line numbers a read shows it with**. Numaralı okuma ile numarasız eşleşme arasındaki bağ kodda
değil burada — Claude Code'un Edit'i de aynı yere koyuyor.

125'in koşullu cümlesi *(bu turda görmediysen oku)* ve 107'nin kaldırdığı koşulsuz emir
*("so read the file first")* olduğu gibi kalıyor; testleri bekçi.

### 4. Kap aynı biçimi taşır *(`stream_answer.py`)*

`_boxed`'ın dosya blokları `numbered(content)` ile yazılır. Şema bloğu ham kalır. Sebebi tek
biçim kuralı: 129'dan beri model dosyayı kaptan okuyor, ve iki ayrı biçim modele çapasının
hangisine uyacağını seçtirirdi.

## Değişmeyen

`_edit`'in eşleşmesi — diskteki ham içerikte, `content.count(old)` ile. Numaralar diske hiç
ulaşmıyor, dolayısıyla eşleşecek bir şey de değişmiyor. 129'un tazeliği, 127'nin adlar satırı,
93'ün sırası, 124'ün anahtarı, `WRITES_FILES` ve kart mantığı da yerinde.

## Bilerek yapılmayanlar

`offset`/`limit`, okuma tavanı, `replace_all` *(132)*, `add_frames` *(128)*. Ön yüz
değişmiyor — bu maddenin dokunduğu hiçbir şey ekrana çıkmıyor, dolayısıyla `dist` derlenmiyor.
