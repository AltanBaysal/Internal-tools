# Madde 369 (v9-11) — Konuşma senaryonun içine yazılır: testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 369 · v9-11.

**Kullanıcıdan gereken:** yok. Madde `ALIGNED`, kullanıcının sözleri satırda; karar, dosya ya da ölçüm
beklenmiyor.

## Ne değişiyor

Start a scenario'nun sahneleri yazdığı adım *(Step 4 -- the scenes)* bugün konuşma hakkında hiçbir şey
söylemiyor. Kullanıcı bir karede birinin konuşmasını isteyince o söz hiçbir yere yazılmıyor, ve
queen-editor'de H3 prompt'unu yazan DeepSeek *(Queen Editor v8-3b)* onu göremiyor. O model her karenin
sahne cümlesini görüyor: 366'dan beri liste her karede `scene`'i `photo`'nun yanında taşıyor.

O adım bundan sonra şunu söyler: **kullanıcı bir karede konuşma isterse söylenen söz o karenin sahne
cümlesinin içine yazılır.** Yalnız konuşma *(kullanıcı — "başka yok gibi")*.

## Sızıntı: aynı cümle fotoğraf prompt'una da gidiyor

Sahne cümlesinin bir okuyucusu daha var. `write_missing_actions` her kareyi kare yazarına sorarken
`_frame_seen` ona sahne cümlesini olduğu gibi gösteriyor (`Scene: ...`), ve yazarın cevabı fotoğraf
prompt'unun aksiyon satırı oluyor. Cümlede bir söz durursa yazar onu satıra taşıyabilir: zayıf model
konuşmayı çizemez, ve tırnak içindeki kelimeler resme yazı olarak çizilebilir. Bu yüzden
`WRITE_FRAME_SYSTEM_PROMPT` da bir kural alır: **sahnede biri konuşuyorsa sözleri aksiyon satırına
girmez.** Bu, maddenin çalışması için gereken parça; ayrı bir istek değil.

## Kararlar (subagent'ın, kullanıcısız)

1. **Test, kuralın yerini tutar** — 368'in şekliyle: metin Step 4'ün başlığıyla Step 5'in başlığı
   arasında kesilir, ve kural o dilimde aranır.
2. **Akışın kuralı iki parçayla tutulur**, cümlenin tamamıyla değil:
   - `speak` — neyin yazıldığı: konuşma;
   - `that frame's scene sentence` — nereye yazıldığı: o karenin sahne cümlesi.
   Küçük harfe çevrilmiş dilimde aranır.
3. **"Yalnız orada":** `speak` Step 4 diliminin dışında, Start a scenario'nun geri kalanında ve Edit
   prompts'ta geçmez. Önce varlık, sonra yokluk — metin hiç okunmadan yeşil olamasın diye.
4. **Kare yazarının kuralı iki parçayla tutulur:** `speaks` — hangi durumda; `leave their words out`
   — ne yapılacağı. Küçük harfe çevrilmiş `WRITE_FRAME_SYSTEM_PROMPT`'ta aranır.
5. **Kare yazarının kuralı `SDXL_PROMPT_RULES`'a girmez:** o metin altı harita aracıyla da gidiyor, ve
   hiçbiri aksiyon yazmıyor. Test `speak`'in onda geçmediğini ister — varlıktan sonra.
6. **İki test tek bölümde, `test_skills.py`'de**, 368'in bölümünün altında: ikisi de aynı cümlenin iki
   okuyucusu, ve bir madde bir yerde okunur.
7. **Edit prompts'a dokunulmaz:** madde yalnız Start a scenario'nun. Edit prompts'ta ajan aksiyonu
   kendisi `update_frame` ile yazıyor; `UPDATE_FRAME_ACTION` onu "as tags" ve "frozen instant" diye
   tarif ediyor. Orada bir sızıntı görülürse ayrı bir madde.
8. **Kelime tavanı değişmez** *(1000, Madde 367)*: kural bir cümle.

## Testler

`queen-agent/backend/tests/test_skills.py`:

- Sahneler adımı, kullanıcının istediği konuşmanın o karenin sahne cümlesine yazıldığını söyler; bu
  kural o adımın dışında ve Edit prompts'ta geçmez. — **kırmızı**
- Kare yazarı, sahnede biri konuşuyorsa sözleri aksiyon satırına yazmaz; kural harita araçlarının
  kurallarına girmez. — **kırmızı**

Frontend'e ve queen-editor'e dokunulmaz.
