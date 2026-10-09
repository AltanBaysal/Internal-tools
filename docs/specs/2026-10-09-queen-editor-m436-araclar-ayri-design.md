# Madde 436 · Queen Editor'ün testleri QueenAgent'ı okumaz — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
436 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 9 Ekim'de hizalandı *(kullanıcı, 8 Ekim — "abi iki aracı tutan bir test olamsın
bunu istemiorum bunalr tammaen ayrı bir proje"; 9 Ekim, Claude'un "Bunları kaldırmak için yeni bir
madde açayım mı?"sına — "aç")*.

## Ne, neden

İki araç ayrı projeler. Bugün Queen Editor'ün iki testi QueenAgent'ın
`queen-agent/backend/features/workspace/domain/prompt.py`'sini yükleyip `SYSTEM_PROMPT_SUFFIX`'ini
Queen Editor'ün kopyalarıyla karşılaştırıyor; QueenAgent'ın sahibi kendi suffix'ini değiştirdiği gün
Queen Editor'ün paketi kırmızıya düşüyor. **QueenAgent'ı okuyan kısım gider; Queen Editor'ün kendi
kuralı — her yazıcının ve agent'ın talimatı Queen Editor'ün suffix'iyle biter — Queen Editor'ün
içinde sınanır.** İki aracın suffix'i artık bir testle bağlı değil.

Madde bir bağı kaldırıyor, davranış eklemiyor: kaldırılan bir testi gösterecek bir kırmızı test yok,
ve yazılmıyor *(madde 431 gibi)*. Kanıt, aşağıdaki listenin diff'le karşılaştırılması, `queen-editor/`
altında `queen-agent`'tan bir şey okuyan bir satır kalmaması, ve dört satırın, kaldırılan test sayısı
kadar eksikle yeşil olması.

## Tarama

`queen-editor/`'ün bütün dosyalarında (testler, kod, `pytest.ini`, frontend'in ayarları, notebook;
`node_modules` ve `dist` hariç) `queen-agent`, `queen_agent`, `QueenAgent` ve deponun köküne çıkan
yollar arandı.

- **Okuyan iki yer, ikisi de yukarıdaki:** `test_video_prompt_writer.py` ve `test_agent_answer.py`,
  `os.path.dirname(TOOL)` üstünden `queen-agent/…/prompt.py`'yi `importlib` ile yüklüyor.
- **Okumayan, yalnız anan yerler kalır:** QueenAgent'ın liste biçimini metin olarak taşıyan
  `test_prompt_list.py` ve `test_photo_routes.py` (`QUEEN_AGENT_LIST` — dosya açmıyor);
  `test_frontend_toolchain.py`, `test_requirements.py`, `viteConfig.test.js`'in "queen-agent'ınkiyle
  aynı dosya, bilerek kopya" yorumları; `test_notebook_clones_its_branch.py`'nin QueenAgent'taki
  eşini anması; kodun ve README'nin, notebook'un QueenAgent'ı anan cümleleri. Bunların hiçbiri bir
  dosya açmıyor ve hiçbir test onları birbirine bağlamıyor.
- `pytest.ini`'de, `package.json`'da, `vite.config.js`'te ve notebook'ta `queen-agent`'a giden bir yol
  yok. Öteki testlerin `ROOT`'u `queen-editor`'ün kendisi.

## Ne değişir

**1. `queen-editor/backend/tests/test_video_prompt_writer.py`**

- `test_the_suffix_is_queen_agent_s_word_for_word` **gider** — yalnız QueenAgent'ın metnine eşitliği
  soruyordu.
- `test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix` **kalır, adı ve sorusu Queen
  Editor'ün olur:** H3 ve ses yazıcısı, üç modda, Queen AI'a verdiği sistem mesajı
  `prompt_writer.SYSTEM_PROMPT_SUFFIX` ile biter.
- `_queen_agent_suffix`, `QUEEN_AGENT_PROMPT`, `TOOL` ve artık kullanılmayan `importlib`, `os`
  içe aktarmaları gider.

**2. `queen-editor/backend/tests/test_agent_answer.py`**

- `test_the_instruction_ends_with_queen_agent_s_suffix` **kalır, sorusu Queen Editor'ün olur:** agent'ın
  talimatı, Queen Editor'ün prompt yazıcılarının bittiği suffix'le
  (`photo_generation.data.prompt_writer.SYSTEM_PROMPT_SUFFIX`) biter. Queen Editor'de suffix'in iki
  kopyası var — agent'ınki ve yazıcılarınki; bugüne kadar ikisi QueenAgent'ınkine eşitlenerek
  dolaylı olarak aynı tutuluyordu, bu soru o eşitliği Queen Editor'ün içinde tutar.
- `_queen_agent_suffix`, `QUEEN_AGENT_PROMPT`, `TOOL` ve artık kullanılmayan `importlib`, `os`
  içe aktarmaları gider.

**3. Kopyaları anlatan iki yorum** — `features/photo_generation/data/prompt_writer.py` ve
`features/agent/domain/prompt.py`'deki `SYSTEM_PROMPT_SUFFIX` yorumları, bir testin kopyayı
QueenAgent'ınkine bağladığını söylüyor. Bugün doğru olanı söyleyecek: metin QueenAgent'ınkinden
alındı, iki araç birbirine dokunmuyor, ve hangi Queen Editor testinin onu tuttuğu.

## Sınırlar

- `queen-agent/`'a, yol haritasına, belgelere ve kural dosyalarına dokunulmaz — FOUNDATION ve
  CODE-STANDARD suffix'ten ya da bu testlerden söz etmiyor.
- Suffix'in metni değişmez; davranış değişmez; frontend ve `dist` değişmez.

## Bitti sayılır

- `queen-editor/`'ün hiçbir testi `queen-agent` klasöründen bir şey okumuyor.
- Dört satır yeşil; `python -m pytest queen-editor -q` bugünkü 1555'ten **1554**'e iner (bir test, 1),
  öteki üç satırın sayısı değişmez.
