# Madde 112 — Cevabın sonuna seçenek listesi eklenmez · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m112-secenek-listesi-testler-design.md) —
bir kırmızı `a4d9a2b`'de.

## Değişen tek yer: taban yönergenin kapanış paragrafı

*"End by saying what you did…"* cümlesinin ardına iki cümle:

> Bir tur ya kararı belirleyen **tek soruyla** biter ya da hiç soru olmadan. Yapılabileceklerin
> listesi bir bitiş değildir — işi kullanıcıya geri vermektir.

Emir kipinde ve davranış olarak yazılıyor: *"ask the one question that decides what happens, or
stop"*. Zayıf modelde *"kısa tut"* gibi bir ölçü işe yaramıyor; yasaklanan şeyin adı konuyor.

## Neden taban, neden akış değil

Menü koşuda yalnız akış adımlarının sonunda değil, kurulum ve kapanış turlarında da çıktı. Her
skill'in üstünde duran davranış taban yönergenin işi *(Madde 73)*, ve akışın kendi onay döngüsü
zaten tek soru soruyor — sorun onun **üstüne** eklenen listeydi.

## Değişmeyen

*"Ask rather than invent"* paragrafı: eksik bir isim, sayı ya da iki anlama gelen bir seçim hâlâ
sorulacak. Kalkan şey, cevabı bitirdikten sonra dizilen yapılabilecekler listesi.

## Görülür hâli

Bir kırmızı yeşerir; taban yönergenin öteki pinleri *(sıra pinleri dâhil)* yerinde kalır. Ön yüz
değişmiyor.
