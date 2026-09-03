# Madde 161 — test turu planı

**Spec:** [m161 yeniden adlandırma testler design](../specs/2026-09-04-queenagent-m161-yeniden-adlandirma-testler-design.md)

Bu tur yalnız test yazar.

## 1. Fikstür

`CROWDED` olduğu gibi. İki karakterli kare, iki kıyafetli liste, eski liste biçimi ve tek string
kıyafet değeri **testin içinde** `json.loads(CROWDED)` üstünden kurulur — ikinci bir sabit yok.

## 2. Yeniden adlandırma testleri

Spec'in 1–13'ü. Sıra testi *(2)* ikinci karakteri seçer; naif bir `pop` + atama onu sona atar ve
test tam olarak onu yakalar.

## 3. Kısmi güncelleme testleri

Spec'in 14–20'si. OR kuralı *(16)* üç araçta parametrize.

## 4. Şema testleri

Spec'in 21–22'si, üç araçta parametrize.

## 5. Koşulur ve kırmızı görülür

CLAUDE.md'nin dört satırı. İki vitest aynı anda koşmaz *(m150'nin bulgusu)*; pytest ile vitest yan
yana koşabilir.

## 6. Kırmızı commit'lenir

`test(m161): …` — mesajda çift tırnak yok.
