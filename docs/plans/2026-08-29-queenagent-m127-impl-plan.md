# Madde 127 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m127-dosya-adlari-uygulama-design.md](../specs/2026-08-29-queenagent-m127-dosya-adlari-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `stream_answer.py`: `_named` ve `_asked`'ın yeni sırası; liste her raundda tazelenir.

## B. `tools.py`: `list_files` spec'i ve dalı silinir; `MAX_ROUNDS` yorumu güncellenir.

## C. `modes.py`: `READS` kısalır.

## D. `prompt.py` ve `skills.py`: tasarımdaki cümleler; akış tavanı korunur.

## E. İki komut koşulur; beklenen yeşil: on yeni test dahil tamamı, defter çifti bilinen kırmızı.

## F. Yeşil commit.

## Bilerek yapılmayanlar: dosya içerikleri gömülmez; ön yüz ve `dist` ellenmez.
