# Madde 38 — Sessiz tur meşru · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m38-sessiz-tur-testler-design.md](../specs/2026-08-19-queenagent-m38-sessiz-tur-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Bu plan **yalnız testleri** yazar. Kod bu turda değişmez; tur, doğru kırmızıyı commitleyerek biter.
Madde tek uçlu — ön yüz sınanmıyor (tasarım belgesi §4).

---

## Adım 1 — `test_stream_answer.py`

Dosya `ScriptedEngine` ile sessiz turu zaten kurabiliyor: tool çağıran bir tur, ardından boş bir tur.
Yeni sahte gerekmiyor.

Beş test eklenir:

1. **`test_a_silent_turn_that_made_a_file_is_still_an_answer`** — `create_file` çağıran sessiz tur;
   üretecin son parçası `Chat`, istisna yok.
2. **`test_the_silent_answer_keeps_the_file_and_no_words`** — kaydedilen son mesajın metni `""`,
   `files` `("plan.md",)`.
3. **`test_the_silent_answer_is_still_one_reply_in_the_chat`** — sohbette `["user", "ai"]`; tool
   trafiği yazılmamış.
4. **`test_a_turn_that_said_nothing_and_made_nothing_is_not_an_answer`** — yalnız `read_file`
   çağıran sessiz tur; `EmptyMessage` yükselir *(bugün de geçer, sınırı tutar)*.
5. **`test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either`** — `MAX_ROUNDS` boyunca
   susup `list_files` çağıran motor; `EmptyMessage` *(bugün de geçer, sınırı tutar)*.

## Adım 2 — `test_chats_api.py`

`FakeEngine` tek metin parçası veriyor ve tool çağıramıyor. Uçtan sessiz turu görebilmek için
**betiklenebilir bir motor** gerekiyor: turları hazır liste olarak taşıyan küçük bir sınıf
(`ScriptedEngine`, bu dosyanın kendi kopyası — iki test dosyası birbirinden import etmez).

Dört test eklenir:

6. **`test_a_silent_turn_that_made_a_file_closes_the_stream_cleanly`** — gövdede `event: file` ve
   `event: done` var, `event: error` yok.
7. **`test_the_record_keeps_the_silent_answer`** — `GET`'le okunan sohbette iki mesaj; ikincisinin
   metni boş, `files` dosyayı taşıyor.
8. **`test_a_turn_that_produced_nothing_says_so_inside_the_stream`** — gövdede `event: error` ve
   içinde **"The model returned nothing."**; akış kopmadan biter.
9. **`test_a_turn_that_produced_nothing_writes_nothing`** — sohbette yalnız kullanıcının mesajı.

## Adım 3 — Kırmızıyı gör

İki komut da koşulur. Beklenen tablo:

| Test | Bugün | Sebep |
|---|---|---|
| 1, 2, 3 | **düşer** | `EmptyMessage` |
| 4, 5 | geçer | bugünkü davranış zaten bu |
| 6, 7 | **düşer** | istisna akışı koparıyor |
| 8, 9 | **düşer** | `error` çerçevesi hiç doğmuyor |

Başka hiçbir test düşmemeli; vitest tamamen yeşil kalmalı. Düşen bir test bu listede yoksa sebebi
anlaşılmadan devam edilmez.

## Adım 4 — Kırmızı commit

`skip` yok, `xfail` yok. Commit mesajı testlerin ne beklediğini söyler, çift tırnak taşımaz.

---

## Kapanış denetimi

- Düşen testlerin hepsi yukarıdaki tabloda.
- Hiçbir kaynak dosyaya dokunulmadı: `git status` yalnız iki test dosyasını gösteriyor.
