# Madde 164 — ölü `complete` yolu · **test turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [v7 yol haritası, Madde
164](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır. Silme işi ikinci turun.

## Bir silmenin test turu neye benzer

Ölü kod silmenin doğal bir kırmızısı yoktur: yerine geçen bir davranış yok, yalnız eksilen bir isim
var. Testlerin çoğu bu turda **taşınıyor** — ölü metot üzerinden ölçtükleri şeyi canlı metot
üzerinden ölçmeye — ve taşındıkları gün de yeşiller.

Kırmızıyı veren tek şey **bekçi**: silinen adın geri gelemeyeceğini söyleyen test. Emsali bu
dosyanın kendisinde duruyor — `test_the_port_no_longer_hands_a_model_to_the_call`, Madde 82'nin
kaldırdığı parametre için yazılmış ve *"watched rather than simply deleted, so it cannot come back"*
diyor. Madde 163'ün `test_no_tool_asks_for_a_kind`'ı da aynı kalıp.

## Yeni testler — iki bekçi

1. **`test_ports.py::test_neither_the_port_nor_its_adapter_still_offers_complete`** — `Engine` ve
   `XaiEngine` üstünde `complete` diye bir ad yok. Bugün ikisinde de var.
2. **`test_xai_client.py::test_the_client_has_one_road_that_is_not_a_stream`** — `XaiClient` üstünde
   `complete_once` var, `complete` yok. Bugün ikisi de var.

## Taşınan testler — `test_ports.py`

3. **İmza testinin listesi `["complete", "stream"]` → `["write_once", "stream"]`.** Bu maddenin en
   somut kazancı: bugün port ile uyarlayıcının imzası **ölü** metot üzerinde karşılaştırılıyor, ve
   Madde 155'in her kare için attığı `write_once` hiç ölçülmüyor. Bugün de yeşil — ölçtüğü iki imza
   zaten uyuşuyor — ama yarın doğru yeri ölçüyor.
4. **`test_the_port_no_longer_hands_a_model_to_the_call` `stream`'e bakar.** Madde 82'nin yasakladığı
   cümle *("travels with the call")* `complete`'in docstring'inde aranıyordu; o docstring gidince
   bekçi bakacak yer bulamaz. Korunan şey cümleydi, durduğu metot değil — sohbetin canlı yolu
   `stream`, ve cümle orada da olmamalı.

## Taşınan testler — `test_xai_client.py`

Sekiz `complete` çağrısı `complete_once`'a döner. Ölçtükleri şey `complete` değil, altındaki
`_answered`: anahtarın her istekte okunması, adres, gövde, `Authorization`, hata çevirisi, ve akış
seçeneğinin akış olmayan isteğe konmaması. `complete_once` aynı `_answered`'ı çağırıyor, dolayısıyla
kapsam düşmüyor — **artıyor**: `complete_once`'ın bugün istemci düzeyinde tek bir testi yok, ve
Madde 155'in kare istekleri o yoldan gidiyor.

5. **`test_the_answer_is_the_assistant_message`**, yerine
   **`test_the_answer_and_what_it_cost_come_back_together`** — `complete_once`'ın kendi şekli:
   `{"text": "hi", "usage": …}`. `complete`'in döndürdüğü ham `message` sözlüğü kimsenin
   beklemediği bir şekle dönüşüyor, ve o şeklin testi bugün yok.
6. **`test_tools_are_sent_when_given` `stream`'e taşınır.** Tek geçemeyen o: `complete_once` araç
   göndermiyor, ve `complete` gidince akış dışında araç gönderen yol kalmıyor. `_request` araçları
   hâlâ gönderiyor ve testin sorusu bu — yalnız sorduğu kapı değişiyor.

## Taşınan testler — `test_xai_engine.py`

7. **İki ikiz teste iniyor.** `test_the_system_prompt_leads_and_the_roles_are_translated` ile
   `test_streaming_is_prepared_the_same_way` aynı `_for_xai`'yi aynı iki assertion'la ölçüyordu,
   biri ölü yoldan biri canlısından. Kalan **birincinin adı**, ikincinin gövdesi: *"the same way"*
   neyle aynı olduğunu ölü metottan alıyordu, ve referansı gidince ad `CRAFT`'ın düştüğü yere
   düşüyor.
8. **`test_the_fixed_part_leads_and_the_last_word_stays_last` `stream`'e taşınır.** Madde 93'ün
   şekli — önde sabit olan, arkada değişen — ve ölçtüğü şey yine `_for_xai`.
9. **`FakeClient.complete` gider.** Onu çağıran kalmıyor.

## `test_chats_api.py`

10. **`FakeEngine.complete` gider.** Rota `stream` kullanıyor; bu metot sahte motorda duran, hiç
    çağrılmayan bir daldı.

## Bu turda dokunulmayanlar

- **`complete_once`, `stream`, `_request`, `_answered`'ın gövdesi.** Bu madde davranış
  değiştirmiyor; `_answered`'ın öksüz kalan `tools` parametresi uygulama turunun işi.
- **Ön yüz.** Hiçbir `.tsx` açılmıyor.

## Nasıl kırmızı olacak

İki bekçi, iki `assert`. Geri kalan her şey taşındığı gün yeşil — ve **yeşil kalmaları taşımanın
kanıtı**: bir test taşındıktan sonra kırmızıya dönerse ölçtüğü şey sandığım şey değilmiş demektir,
ve o zaman silinen yol ölü değildir.

**Koşulan sonuç: 3 kırmızı, 782 yeşil**, artı defterin bilinen 2'si. Üç, çünkü port bekçisi iki
katman üzerinde parametreli. Yeşil sayısı 783'ten 782'ye indi: 7 numaranın sildiği ikiz.

Taşınan on testin hepsi taşındığı gün yeşil — bu turun asıl ölçüsü o. Biri kırmızıya dönseydi
ölçtüğü şey `_answered` ya da `_for_xai` değil `complete`'in kendisiymiş, yani yol ölü değilmiş
olurdu.
