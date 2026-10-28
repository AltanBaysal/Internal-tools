# Madde 171 · uygulama turu — kapı

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m171-kapi-testler-design.md).
Commit `a35ef84` beş vak'ayı çiviledi.

---

## Bir bekçi, iki çağrı yeri

```python
def _shut(wanted):
    """The refusal a structure file gets, or None when the name is not one."""
    if not wanted.lower().endswith(".json"):
        return None
    return ToolResult(
        f"{wanted} is a structure file; it is not written or changed as text. Use "
        "start_scenario to open one, and the add_, update_ and remove_ tools to change it.",
        None,
        wanted,
        "Not as text",
    )
```

`create_file` ve `_edit` `safe_name`'den **hemen sonra** soruyor: adı temizlemek onun işi, kapı
temiz ad üstünde duruyor. Ve **her şeyden önce** — dosyanın var olup olmadığından, metnin bulunup
bulunmadığından önce. Bir yapı dosyasına metin olarak dokunmanın reddi, o dosya hakkında başka bir
şey öğrenmeye bağlı değil.

`.lower()` uzantı üstünde: Windows `BAR.JSON` ile `bar.json`'u tek dosya açıyor, ve büyük harfi
görmeyen bir kapı kendi çerçevesinin yanında durur.

## Araç açıklamaları da değişiyor

`create_file`'ın *"A short file name: .md for a document, .json for a structure file"* diyen
parametre metni artık **yanlış** — o yolu kapattık. Yerine: belge yazar, senaryo `start_scenario`'nun.

`edit_file`'ın açıklaması da bir cümle alıyor: yapı dosyaları bu araçla değişmiyor.

**Bunlar yorum değil, modele giden metin** — ve modele artık yapamayacağı bir şeyi söylemek, m127'nin
`list_files` hatasının aynısı.

## `WRITES_FILES` ve kipler değişmiyor

`create_file` hâlâ dosya doğurabiliyor *(belge)*, hâlâ edit kipinde sormadan koşuyor. Kapı **hangi
adı** yazabildiğini daraltıyor, aracın yetkisini değil.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: beş kırmızının beşi de yeşil**, `queen-agent` tarafında **765 yeşil** *(760 + 5)*.
3. `.md` yolunu ölçen iki test yeşil kalmalı. Düşerse kapı fazla geniş kapanmıştır.
4. Öteki üç takım rakamlarını korur. `dist` derlenmez.

## Koşarken çıkan iki kırmızı — ikisi de test turunda görülmeliydi

Yayılma alanı taraması kapının **kimi kestiğine** baktı, **kimin ona dayandığına** bakmadı. İki
bekçi eski davranışı çiviliyormuş:

**`test_create_file_names_both_formats_a_file_can_take`** parametre metninin *".json for a structure
file"* dediğini çiviliyordu. O iddia kapıyla birlikte öldü, ve tersine döndü:
`test_create_file_no_longer_offers_to_write_a_structure` — artık `.json` **geçmemeli**, ve çıkış
aracın kendi açıklamasında olmalı. Modele yapamayacağı bir çağrıyı önermek m127'nin `list_files`
hatası, ve o hata bir denemeye mal olmuştu.

**`test_building_again_writes_over_its_own_output`** yapıyı değiştirmek için `edit_file`'ı
kullanıyordu — kapanan kapının ta kendisi. Testin iddiası *("yeniden derlemek kendi çıktısının
üstüne yazar")* değişmedi; değişen, bir karakteri değiştirmenin tek yolunun artık
`update_character` olması.

**Ders, 167'nin dersinin aynısı ve bu sefer daha pahalıya:** bir şeyi kapatan madde, o şeyi
kullanan testleri de aramak zorunda. Aranan şey aracın adı, yalnız değiştirilen fonksiyon değil.
