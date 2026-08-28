# Madde 127 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 127
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Adlar hiçbir istekte hazır değil. Sonucu altıncı denemede iki türlü görüldü: model her turu
`list_files` ile açtı, ve bir kez de olmayan bir ad uydurdu — `read_file(plan.md)`, dosyanın
gerçek adı `milf-cheating-hentai-plan.md` iken. İkisi de bilgi eksikliğinin değil, bilginin
yerinin sorunu: proje dosyalarının adı her turda doğru olan bir şeydir, yani her isteğin
taşıyabileceği bir şeydir.

## Yol

`stream_answer` her raundda `file_store.list_names` çağırır ve isteğin sonuna, **skill metninin
hemen önüne** bir system satırı koyar:

- dosyalar varken: `The project's files right now: bar-scene.json, bar-scene-scenes.md`
- boş projede: `This project holds no files yet.`

Sona binmesi Madde 93'ün kalıbı: başa binse her dosya doğumu konuşmanın prefix cache'ini
öldürürdü. Skill metni en sonda kalır — 93'ün *"what changes trails"* sırası bozulmaz, ve liste
konuşmadan sonra geldiği için tur ortasında doğan dosya bir sonraki raundda görünür.

`list_files` **aracı** tamamen kalkar: `TOOL_SPECS`'ten, `run_tool`'dan ve `modes.READS`'ten.
Ekranın kullandığı `usecases/list_files.py` ve `FileStore.list_names` kalır — biri dosya paneli
içindir, öteki bu maddenin kendi kaynağı.

## Bu turun yeni testleri (hepsi kırmızı doğar)

`test_stream_answer.py`:

- `test_the_request_carries_the_names_the_project_holds`
- `test_an_empty_project_says_it_holds_nothing`
- `test_the_names_are_fresh_in_every_round` — 1. raundda doğan dosya 2. raundun listesinde.
- `test_the_names_ride_behind_the_conversation_and_before_the_instruction` — 93'ün sırası.

`test_tools.py` · `test_the_listing_tool_is_gone`: `TOOL_SPECS`'te yok, `run_tool` onu tanımıyor.

`test_prompt.py` · `test_the_base_is_handed_the_names_rather_than_asking_for_them`:
tabanda `listed for you in every request` geçer, `list_files` geçmez.

`test_skills.py` · `test_no_instruction_reaches_for_the_listing_tool`: iki skill metninde de
`list_files` geçmez; akışın 1. adımı `first turn opens with write_plan` der.

## Bu turda uyarlanan mevcut testler

- `test_every_tool_is_declared_to_the_model` ve `test_modes.py`'nin `READS` tuple'ı: `list_files`
  çıkar — ikisi de bu turda kırmızıya döner.
- `test_tools.py`'nin `list_files` davranış testleri *(boş proje, adları sayma, target, outcome)*
  silinir; aracı **yardımcı** olarak kullanan satırlar `file_store.list_names`'e çevrilir.
- `test_stream_answer.py` ve `test_chats_api.py`'de `list_files` jenerik bir araç çağrısı örneği:
  argümansız kardeşi `read_prompt_structure_schema` ile değiştirilir; içerik iddiası olan tek test
  `read_file`'a geçer *(kısa ve net bir cevabı var)*.

## Bilerek dokunulmayanlar

`test_file_chat_store.py` ve `ChatScreen.test.jsx` `list_files`'ı kayıt içeriği olarak taşıyor:
kaldırılan bir aracın adını taşıyan eski sohbet hâlâ çizilebilmeli, ve bu testler tam olarak onu
söylüyor.

## Ayakta kalması gerekenler

Madde 93'ün sırası *(skill metni en sonda)*, 107'nin `A chat's first turn` pini, izin/kip
davranışı, `read_file`'ın kendisi *(içerik JIT kalır — kullanıcı kararı, 29 Ağustos)*.
