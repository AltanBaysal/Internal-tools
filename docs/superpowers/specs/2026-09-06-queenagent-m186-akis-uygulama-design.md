# Madde 186 · uygulama turu — altı adım, ve devir yerine derleme

**Kaynağı:** [test turu](2026-09-06-queenagent-m186-akis-testler-design.md), `b685a28` ve
`f85ba7b`'de 28 kırmızı *(ön yüzde 23)*.

---

## Değişen dört yer

`prompt.py`'nin iki metni, `skills.py`'nin haritası, ön yüzün `skills.js`'i, ve `dist`. Kod
mantığı hiç değişmiyor — bu madde baştan sona **metin ve ad**.

## Akış: kazandığı adım, kaybettiği adım

Öne **bağlam** giriyor, sondaki **devir paragrafı** çıkıyor. Tavan bu yüzden 450'de duruyor: bir
adım geldi, bir adım gitti.

`start_scenario` 2. adıma iniyor. Dosyanın adını veren şey zaten bağlam, ve erken açılınca sonraki
her adım **hazır bir dosyaya** yazıyor. Bedeli kabul edildi *(kullanıcı kararı)*: bağlamı söyleyip
vazgeçen bir kullanıcı ardında boş bir `.json` bırakır.

6. adım iki çağrı: `write_missing_actions`, sonra `build_prompts`. Kapanış mesajı iki şey — dosyanın
adı, ve hazır olduğu. Devir cümlesi yok, çünkü gidilecek yer yok.

## *Edit prompts*: arızanın yerine göre bölünmüş bir tarif

`superpowers:writing-skills`'in geçen kuralı: çıktının şekli yanlışsa doğru biçim **tarif**, yasak
listesi değil. Burada asıl risk *"hangi aracı çağıracağım"* — ve metin o soruyu üç satırda
cevaplıyor, her biri **arızanın nerede yaşadığına** göre:

| Arıza | Araç |
|---|---|
| bir karenin cümlesi | `write_frame_prompt`, notla |
| bir kişi ya da yer, göründüğü her yerde | `update_character` · `update_outfit` · `update_location` |
| karenin kadrosu, kıyafeti ya da yeri | `update_frame` |

Sonra her hâlde `build_prompts`. Model *"neyi düzelteceğim"* sorusunu metnin **şeklinden** okuyor,
bir yasak listesinden değil.

## `pov_` kuralı burada kalıyor

*"Bunu POV yap"* bir düzeltme turunda geliyor — akışın değil, bu skill'in turunda. Madde 182'nin
kuralının iki yarısı iki metinde: girişin **açılması** akışta, kadroda **kullanılması** burada.

## Adın iki tarafı

`edit-prompts` hem `INSTRUCTIONS`'ta hem `skills.js`'te. İkisi ayrı yerde ve ayrılırlarsa skill
hiç metin taşımaz; `test_skills.py`'nin ilk satırı bunu elle pinliyor, çünkü Python `skills.js`'i
okuyamaz.

Eski id hiçbir yerde yaşamıyor ama **hiçbir yerde de kırılmıyor**: `instruction_for` bilmediği adı
boş geçiyor, `skillName` bilmediği id'yi ekrana kendisi olarak yazıyor. Dünden kalan bir sohbet
açılıyor, yalnız talimatsız koşuyor.

## `dist` aynı commit'te

Defter bu depoyu klonluyor ve hiç derlemiyor, yani derlenmemiş bir ön yüz değişikliği bitmiş
değil. `npm run build --prefix queen-agent/frontend`, ve çıkan `dist` kaynakla **aynı commit'te**.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 28 + 23 kırmızı kapanıyor; `queen-editor` kımıldamıyor.
