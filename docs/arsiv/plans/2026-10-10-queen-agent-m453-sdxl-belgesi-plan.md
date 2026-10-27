# Madde 453 — SDXL belgesi, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden — belgeyi ve tool açıklamalarını kullanıcı Changes'te okuyup onaylar, commit ana
> agent'ındır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** SDXL kuralları tek bir belgede, her istekte system prompt'tan hemen sonra kendi sabit
mesajında; içinde bugünkü kurallar, skill'lerdeki görüntü modeli kurallarının kopyası, ayna kuralı, ve
fotoğrafın boyutu. Altı tool açıklaması kuralları taşımaz.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m453](../specs/2026-10-10-queen-agent-m453-sdxl-belgesi-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce; spec ve plan Türkçe.
- `IMPROVE`, `EDIT_PROMPTS`, `SYSTEM_PROMPT`, `SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND`, tool adları,
  frontend ve queen-editor'e dokunulmaz; `START_A_SCENARIO`'da yalnız Step 3'ün ayna cümlesi değişir.
- Yeni kural yazılmaz.
- `git add`, commit, stash yok. Geçici dosyalar `tmp/m453/`'te.

---

## Görev 0: Ölçüm

- [ ] `tmp/m453/measure.py`: system mesajı, belge ve `TOOL_SPECS`'in JSON'u kaç karakter; altı
  açıklamanın ve action tarifinin metni. Bugünkü hâli `before.json`.

## Görev 1: Belge ve tool açıklamaları — `prompt.py`

- [ ] `test_tools.py`: `_rules()` `SDXL_DOCUMENT`'ı döner; kuralları altı tool'da arayan iki test,
  hiçbir tool metninde belgenin ve kural satırlarının olmadığını söyleyen testle değişir; `TAG_TOOLS`
  kalkar; `SDXL_PROMPT_RULES`'u doğrudan okuyan testler `_rules()`'a bakar; anatomi testi belgeyi
  açıklamada aramaz. Yeni: `SDXL_PROMPT_RULES` yok; belge modeli ve boyutu söylüyor; ayna yalnız
  istenince; action'ın tarifi belgenin başlığını anıyor.
- [ ] `test_prompt.py`: `MUST_BE_FULL`'da `SDXL_DOCUMENT`. `test_skills.py`: skill'ler belgeyi
  taşımıyor. Kırmızı.
- [ ] `prompt.py`: `SDXL_PROMPT_RULES` → `SDXL_DOCUMENT`, spec'teki metin; altı açıklamadan
  `"\n" + SDXL_PROMPT_RULES` çıkar; `UPDATE_FRAME_ACTION` belgeyi anar; bölüm yorumu ve modülün
  belgesi yeni yeri söyler. Yeşil.

## Görev 2: İstekteki yer — `model_engine.py`

- [ ] `test_model_engine.py`: belge `seen[1]`'de, system mesajının hemen arkasında; iki istek aynı iki
  mesajla başlar; roller `system, system, user, assistant`; sahibin eki belgeye değmez (`seen[1:]`
  belge ve konuşma). Kırmızı.
- [ ] `model_engine.py`: `_for_model` ikinci mesaj olarak `SDXL_DOCUMENT`'ı koyar, nedenini söyleyen
  yorumla. Yeşil.

## Görev 2b: Kullanıcının 10 Ekim kararları ve review düzeltmeleri

- [ ] Belge: skill'lerdeki görüntü modeli kuralları — zayıf model, frame'in prompt'u, kamera açısı,
  Rule 1 – 6, negatif listenin bağlamı — kelimesi kelimesine iki yeni bölümde; skill'lerde de kalır
  ("Evet, kopyası belgeye de girsin"). Model adı çıkar, boyut kalır ("Model adı olmasın").
- [ ] Start a scenario'nun Step 3'ü: *"Do not add a mirror to a place unless the user asks for
  one."* `test_skills.py`: Step 3 aynayı ve kullanıcının istemesini anıyor. Kelime tavanı kırmızıysa
  yazılı kararla yükselir (yeşil kaldı: 1806 ≤ 1830).
- [ ] Testler sabit cümle değil anahtar kelime arar; `test_the_rules_are_one_document_now` kalkar;
  hiçbir tool'un belgeyi taşımadığını söyleyen test `test_prompt.py`'ye, `_descriptions_in`'in
  yanına taşınır; anatomi testi `said.strip()`'e bakar; alana özgü kural testi o kuralların kendisine
  bakar.
- [ ] `ports.py`: `stream_alone`'un belge dizesi sabit başın hiçbirini almadığını söyler.

## Görev 3: Ölçüm ve spec

- [ ] `measure.py after`; spec'in token tablosu ölçülen sayılarla.

## Görev 4: Dört suite

- [ ] `python -m pytest queen-agent -q`; `npm test --prefix queen-agent/frontend`;
  `python -m pytest queen-editor -q`; `npm test --prefix queen-editor/frontend` — birer birer.
- [ ] `git status`: yalnız spec, plan, `prompt.py`, `model_engine.py`, `ports.py` ve dört test
  dosyası.
