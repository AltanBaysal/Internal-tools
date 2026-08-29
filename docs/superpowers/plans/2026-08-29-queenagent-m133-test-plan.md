# Madde 133 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m133-tavan-testler-design.md](../specs/2026-08-29-queenagent-m133-tavan-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_chat.py`: yardımcı ikinci sayıyı alır, iki yeni kırmızı, iki çağrı yeni ada geçer.

## B. `test_stream_answer.py`: iki mevcut test dördüncü sayıyı bekler, bir yeni kırmızı.

## C. `test_file_chat_store.py`: yeni alan diskte yaşar; alansız eski kayıt sıfır okur.

## D. İki komut koşuldu: **10 kırmızı**, frontend 568 yeşil, defter çifti bilinen kırmızı.

`test_chat.py`'de beş, `test_stream_answer.py`'de üç, `test_file_chat_store.py`'de iki.

**Biri tasarımda bekçi yazılmıştı ve kırmızı çıktı:**
`test_a_chat_is_full_at_the_ceiling_and_not_before` kendi cümlesini değiştirmedi, ama `_answered`
yardımcısı artık `Usage`'a dördüncü bir sayı veriyor ve o alan henüz yok — bugünkü kırmızısı bir
`TypeError`. Uygulama turunda yeşile dönmesi bir şey kanıtlıyor: tavanın eşiği kaymadı.

**Gerçek bekçiler yeşil kaldı:** `test_the_ceiling_is_fifty_thousand` *(sayı değişmiyor)* ve
`test_chats_api.py`'deki `test_the_record_says_how_much_of_the_ceiling_it_has_used` — tek
raundluk bir turda toplam ile son raunt aynı olduğu için uç aynı sayıyı veriyor, ve vermeye devam
etmeli.

## E. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; ön yüz ve `dist` ellenmez.
