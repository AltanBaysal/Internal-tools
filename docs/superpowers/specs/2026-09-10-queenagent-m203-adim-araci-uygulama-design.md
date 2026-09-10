# Madde 203 — adımı işaretleyen araç kalkar · uygulama turu

**Kaynak:** [test turunun tasarımı](2026-09-10-queenagent-m203-adim-araci-testler-design.md).
**Test turu:** `0e631bf` — altı kırmızı.

## Ne yapılacak

Altı kırmızı kapanır: araç, şeması, dalı, `_ticked`, üç metni, kip satırı, kaldırma kuyruğu
`plan_name`, ve akışın kapatma maddesi.

Kaldırma bu koşunun dördüncüsü *(205, 206, 207, 208)* ve aynı biçimde iner. Farkı: ötekiler
**kullanılmayan** bir araç kaldırdı; bu, kullanılan ama **okuyucusu kalmamış** bir yazma kaldırıyor.
Kutu doluyordu; onu okuyan tur 11 numaradan sonra yok.

## Kalkanlar

| Nerede | Ne |
|---|---|
| `prompt.py` | `MARK_STEP_DONE`, `MARK_STEP_DONE_NAME`, `MARK_STEP_DONE_STEP` |
| `prompt.py` | `START_A_SCENARIO`'nun döngü listesindeki dördüncü madde |
| `tools.py` | `TOOL_SPECS` girdisi, `run_tool` dalı, `_ticked`, `plan_name` |
| `modes.py` | `EDIT`'in listesindeki `mark_step_done` ve üç satırlık 198 yorumu |

## İki yorum düzelir

**`run_tool`'un docstring'i** *"the other eighteen"* diyor ve bugün doğru — 19 araç, motoru alan
bir tane. Araç kalkınca 18 kalır, yani cümle **on yediye** iner. Test tarafındaki ikizi test turunda
düzeldi.

**`scenario_name`'in docstring'i** `plan_name`'i *"kardeşim, aynı yerde koşuyor"* diye anıyor.
Kardeş gidiyor; cümle `safe_name`'den sonra koştuğunu kendi başına söyler.

## Kip kapısı değişmiyor

Araç yalnız EDIT'te sormadan koşuyordu; `edit_file` de öyle. Yani hiçbir kipin yetkisi bu
kaldırmayla genişlemiyor ya da daralmıyor. `ends_the_turn` de dokunulmadan kalır — o çift PLAN ile
`create_file`.

## Belgeler

**Okuma kopyası kodun aynası, ve öyle kalmalı** *(190'ın kapanışı)*:

- §3'ün akış metni dördüncü maddeyi bırakır.
- §6'nın `mark_step_done` bölümü kalkar, ve *"35 numara bu aracın metnine dokunmadı"* notu artık
  sebebi gerçekleşmiş bir not: bölüm gider, araç sayısı **19 → 18** olur.

**Düzeltme log'u tarih, yeniden yazılmaz.** 7 ve 10 numara döngünün dördüncü maddesini yazmıştı ve
10 numara *"onu `edit_file`'a çevirmek 203'ün işi"* diyordu. İkisine birer satır eklenir: 203 maddeyi
çevirmedi, **geri çekti**. Kayıtların gövdesine dokunulmaz.

**Yol haritası** 203'ü kapatır, ve sapmayı yazar: maddenin kendi *"Ne çalışır"*ı
*"kapanış maddesi `edit_file`'ı anar"* diyordu; kullanıcı 10 Eylül'de maddenin tümüyle düşmesini
seçti, gerekçesi 11 numara.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Süitin tamamı yeşil**, ve araç sayısı 19'dan 18'e iner. Ön uç 648'de kalır: bu madde ön uca
dokunmuyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-10-queenagent-m203-impl-plan.md).
