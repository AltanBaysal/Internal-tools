# Madde 149 · Tur 1 (test) — Uygulama Planı

**Goal:** İkinci yolu tarif eden testleri yazmak ve kırmızı commit etmek.

**Spec:** [Tur 1 tasarımı](../specs/2026-09-03-queenagent-m149-ikinci-yol-testler-design.md)

## Global Constraints

- **Yalnız test dosyaları.** `config.py`, `client.py`, `main.py`, `models.js` bu turda
  değişmiyor — değişirse tur ikiye karışmış demektir.
- `skip` / `xfail` yok: kırmızı kırmızı commit ediliyor.
- Defterin `BRANCH` kırmızısı bu turun işi değil ve staged edilmiyor.

### Task 1: `backend/tests/test_config.py`

- [ ] `test_the_openrouter_key_comes_from_the_environment` — üçüncü anahtar, ilk ikisinin yolu.
      **Tek test, çünkü en yakın emsal öyle:** *"yoksa boş"* kuralı XAI'de bir kez çivili, DeepSeek
      onu tekrarlamamış, ve üç anahtar da aynı `os.environ.get(ad, "")` satırından geliyor.
- [ ] Bugünkü `test_the_three_models_resolve_to_their_provider` **beşe genişliyor**, adı da
      *(`..._the_five_models_...`)*. İki yeni satır `https://openrouter.ai/api/v1`.
- [ ] `test_each_model_names_the_key_it_spends` iki satır kazanıyor: `OPENROUTER_API_KEY`.
- [ ] `test_the_openrouter_rows_are_pinned_to_deepinfra` — `extra` birebir
      `{"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}`. Yorumu **neden**
      çivilendiğini yazıyor: sabitleme düşerse istek pornografiyi yasaklayan bir sağlayıcıya
      düşebilir.
- [ ] `test_a_direct_row_carries_no_extra` — üç doğrudan satır.
- [ ] `test_engine_for_gives_the_extra_as_its_fourth_thing`
- [ ] Bugünkü `test_a_known_model_resolves_to_its_own_wiring` dört değere açılıyor.
- [ ] `test_an_unknown_or_absent_model_falls_back_to_the_default` **dokunulmuyor** — hâlâ `[0]`
      okuyor ve hâlâ geçerli.

### Task 2: `backend/tests/test_xai_client.py`

- [ ] `test_the_extra_body_fields_reach_the_request` — `complete`.
- [ ] `test_the_extra_reaches_a_streamed_request_too` — asıl kullanım akış.
- [ ] `test_the_clients_own_fields_win_over_the_extra` — `extra` içinde `model` ve `messages`,
      gövdede gerçek değerler.
- [ ] `test_without_an_extra_the_body_is_what_it_has_always_been` — anahtar kümesi bugünküyle
      birebir; Grok yolu değişmiyor.

### Task 3: `backend/tests/test_composition.py`

- [ ] `test_each_client_is_handed_its_own_extra` — main.py metninde `engine_for(model)[3]`.
      Dosyayı okuyarak, bu dosyanın kendi usulünce.

### Task 4: `frontend/src/features/workspace/models.test.js`

- [ ] `three models are offered` → **beş**, id listesi sırasıyla.
- [ ] `every row carries a name and what it costs` → beş satırın adı ve fiyatı.
- [ ] `a known id reads as its name` yanına: `deepseek/deepseek-v4-flash-0731` kendi adını veriyor.
- [ ] `the default is the one the app has always answered with` **dokunulmuyor**.

### Task 5: Kırmızıyı gör ve commit et

- [ ] `python -m pytest queen-agent -q`
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: queen-agent'ın iki takımında yeni kırmızılar, queen-editor'de hiçbiri; defterin
      kendi 2 kırmızısı yerinde.
- [ ] Commit: yalnız test dosyaları + spec + plan + yol haritası.
