# Madde 133 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m133-tavan-uygulama-design.md](../specs/2026-08-29-queenagent-m133-tavan-uygulama-design.md)

## A. `chat.py`: `Usage.context` doğar; `last_sent` → `last_context` ve son raundu okur.

## B. `stream_answer.py`: dördüncü sayı toplanmıyor, yerine konuyor.

## C. `file_chat_store.py`: alan yazılıyor ve okunuyor; alansız kayıt sıfır dönüyor.

## D. `routes.py`: çağrı yeni ada geçiyor, JSON şekli aynı kalıyor.

## E. İki komut koşuldu: on kırmızı döndü, iki test daha kırıldı.

`test_counts_repeated_inside_one_round_are_not_added_twice` ve
`test_a_stopped_answer_still_says_what_it_spent` `Usage`'ı dört alanıyla değil üçüyle kuruyorlardı.
İkisinin de kendi cümlesi değişmedi — biri aynı raundun tekrarlanan bildirimlerinin toplanmadığını,
öteki durdurulan bir turun harcadığını söylediğini tutuyor. Dördüncü sayı eklendi ve ikisi de o
sayı hakkında bir şey daha söylüyor artık: tekrarlanan bildirim onu da çoğaltmıyor, ve durdurulan
bir turda istek gerçekten o boyda gitmişti.

**Bu ikisi test turunda görülmeliydi**, tıpkı 131'in üç testi gibi, ve sebep aynı: tur davranışı
değişen yerleri aradı, `Usage`'ı tam hâliyle kuran yerleri taramadı. İkinci kez olduğu için kayda
geçiyor.

## F. İki komut yeniden koşuldu: **638 yeşil**, frontend 568 yeşil, defter çifti bilinen kırmızı.

## G. Yeşil commit.

## Bilerek yapılmayanlar: göç, ön yüz, `dist`, mesajın `usage` JSON'una yeni alan.
