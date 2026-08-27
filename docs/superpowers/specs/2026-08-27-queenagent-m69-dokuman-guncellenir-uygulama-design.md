# Madde 69 — Doküman güncellenir, yeniden yaratılmaz · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m69-dokuman-guncellenir-testler-design.md) · kırmızı commit `e4659ba`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## İki dosya

`domain/tools.py` ve `features/workspace/useChat.js`. Biri kuralı, öteki onun ekranda bıraktığı izi.

## `tools.py` — `create_file` dolu bir adı reddeder

Dal `unique_name` çağırmayı bırakıyor ve önce adın boş olup olmadığına bakıyor. Dolu ise hiçbir şey
yazmıyor: `created` yok, çünkü doğan bir şey yok; `target` istenen ad, çünkü çağrı onun hakkındaydı;
`outcome` *"Already there"*, çünkü *"Saved"* olmayan bir şeyi söylerdi.

Cevabın metni **modele verilen yönergedir.** Yalnızca *"bu adda bir dosya var"* demek, bir sonraki
adımı modelin tahminine bırakırdı — ve tahmin onu zaten buraya getiren şey.

Varlık `list_names` ile soruluyor, `read` ile değil: sorulan şey adın dolu olup olmadığı, ve dosyanın
tamamını yalnız bunu öğrenmek için okumak fazladan iş olurdu. Dalın eski hâli zaten `list_names`
çağırıyordu.

`unique_name` importu bu dalla birlikte gidiyor — dosyada başka kullanıcısı yok. Fonksiyonun kendisi
`naming.py`'de kalıyor; çöp onu kullanmaya devam ediyor.

### Bir yorum düzeliyor

Bugünkü satır *"The name it got, not the one it asked for"* diyor ve gerekçesi numaralandırmaydı.
Ad hâlâ istenenden farklı olabiliyor — `safe_name` temizliyor — ama sebep değişti, ve yorum yalnız
bugün doğru olanı söyler.

`_edit`'in docstring'i de *"create_file never overwrites, so without this there is no way to change
anything"* diyor. Hâlâ doğru, ama artık eksik: `create_file` üstüne yazmamakla kalmıyor, denemeyi de
reddedip buraya yolluyor.

### Araç tarifi

`create_file`'ın tarifine reddi söyleyen bir cümle giriyor. Kuralı kod garanti ediyor; tarif onu
önceden söyleyince olağan durumda fazladan tur hiç yaşanmıyor. Bu bir özen ricası değil — aracın ne
yaptığının tarifi, ve `write_plan` zaten aynı biçimde konuşuyor.

## `useChat.js` — kesikli kart `call` karesinde iner

`call` kolu kartı da indiriyor. Kesikli kartın ömrü *"model istedi"* ile *"araç cevapladı"* arası, ve
`call` ikincisi. Sıra her zaman `file-start → (file) → call`, yani bu hiçbir durumda erken değil —
dosya doğduğunda `file` zaten indirmiş oluyor ve ikinci kez indirmek bir şeyi bozmuyor.

`file` kolundaki indirme duruyor: kartın yerini alan asıl şey dosya kartı, ve onu bir kare önce
indirmek doğru olan.

## Altı kırmızının karşılığı

| Test | Karşılığı |
|---|---|
| `..._over_a_name_that_is_taken_writes_nothing` | `write` çağrılmıyor |
| `..._points_at_the_tool_that_can_do_it` | cevabın metni `edit_file` diyor |
| `..._brings_no_file_into_being` | `created` yok |
| `..._names_the_file_that_was_in_the_way` | `target` istenen ad |
| `..._does_not_say_it_saved` | `outcome` *"Already there"* |
| `a call frame takes the dashed card down` | `call` kolunda `setCreatingFile(false)` |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` **derleniyor**: `useChat.js` bir ön yüz kaynağı.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`naming.py` açılmaz.**
- **`edit_file`, `write_plan`, `build_prompts` davranışları değişmez** — yalnız `_edit`'in
  docstring'i bugünkü doğruyu söyleyecek şekilde tamamlanıyor.
- **`stream_answer` açılmaz** — `FileStarted` yerinde kalıyor: ad araç koşana kadar belli değil, ve
  kartı indiren şey artık `call`.
- **Diskte duran numaralı kopyalar temizlenmez.**
