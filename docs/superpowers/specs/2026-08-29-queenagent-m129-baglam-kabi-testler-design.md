# Madde 129 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 129
**Araştırma:** [2026-08-29-queenagent-arac-tasarimi-arastirma.md](../research/2026-08-29-queenagent-arac-tasarimi-arastirma.md)
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

`read_file`'ın sonucu konuşmaya yazıldığı yerde donuyor. Dosya sonra değişse de o mesaj ilk
okunan hâli taşımaya devam ediyor; model bunu bildiği için tekrar okuyor ve ikinci kopya da
yanına ekleniyor. Yedinci denemede aynı dosya üç kez okundu, her kopya tur boyunca her isteğe
bindi — 335k'nın büyük kısmı bu.

## Yol

Okunanlar bir **kapta** toplanır ve kap isteğin sonunda, dosya adları satırının ardından,
**her raundda diskten tazelenerek** gider.

Kap kayıttan türetilir — yeni bir disk alanı yok. `Message.calls` hangi aracın hangi dosyaya
dokunduğunu zaten yazıyor; kap o kayıttan okunan dosya adlarını toplar, içeriği ise her seferinde
diskten alır. İçerik hiçbir yere kopyalanmadığı için bayatlayamaz, ve silinen dosya kaptan
kendiliğinden düşer.

## Kurallar

- **Ne girer:** `read_file` *(target'ı olan)* ve `read_prompt_structure_schema`. Yazma araçları
  girmez — çıktıları zaten tek cümle.
- **Kaç tane:** son 5 dosya, en yenisi başta *(kullanıcı kararı)*. Şema bunun dışında, kendi
  bloğu.
- **Nereden:** kayıttaki mesajların `calls`'ı **artı** bu turun o ana kadarki adımları — tur
  ortasında okunan dosya bir sonraki raundda kapta olmalı.
- **Turlar arası yaşar:** kayıt kalıcı, dolayısıyla ikinci mesaj da kapla açılır.

## Bu turun testleri (hepsi kırmızı doğar)

`test_context_box.py` *(yeni dosya, saf alan mantığı)*:

- `test_a_file_that_was_read_is_in_the_box`
- `test_the_newest_read_leads`
- `test_the_same_file_read_twice_is_one_entry`
- `test_only_the_last_five_survive`
- `test_a_write_alone_does_not_put_a_file_in_the_box`
- `test_the_schema_is_remembered_separately`
- `test_a_chat_that_read_nothing_has_an_empty_box`

`test_stream_answer.py`:

- `test_the_request_carries_the_contents_of_what_was_read` — okunan dosyanın içeriği isteğin
  sonunda.
- `test_the_box_is_refreshed_from_disk_every_round` — turda yazılan yeni hâl bir sonraki raundun
  kabında.
- `test_a_file_read_in_an_earlier_turn_is_still_in_the_box` — turlar arası.
- `test_a_deleted_file_falls_out_of_the_box` — sessizce.
- `test_the_box_rides_between_the_names_and_the_instruction` — sıra: konuşma → adlar → kap →
  skill metni.

## Ayakta kalması gerekenler

Madde 93'ün sırası *(skill metni en sonda)*, 127'nin adlar satırı, 124'ün önbellek anahtarı,
`read_file`'ın kendisi ve turlar arası araç sonucu taşınmaması *(kap sonuç değil, addır)*.

## Bilerek yapılmayanlar

Konuşmadaki `tool` mesajları olduğu gibi kalır — protokol bir `tool_calls` girdisinin karşılığını
şart koşuyor, ve kullanıcının sözü: *"niye karmaşıklaştırıyorsun"*. Disk şeması değişmez.
`add_frames` Madde 128'in.
