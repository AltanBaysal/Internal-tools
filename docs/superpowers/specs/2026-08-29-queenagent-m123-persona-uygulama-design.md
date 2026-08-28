# Madde 123 — Skill metinleri persona ile açılır ve kısalır · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 123 ve
[tur 1'in tasarımı](2026-08-29-queenagent-m123-persona-testler-design.md). Testler kırmızı
commit'te — akış 848 kelimeden 450'nin, prompt+ 300'ün altına iner.

## Biçim kararları

- **Persona açılışı** *(kullanıcının cümlesi)*: akış "uzman senaryo yazarı", prompt+ "uzman SDXL
  prompt yazarı"; ikisi de kime çalıştığını ve birbirine devrini rolün içinde söylüyor.
- **Yasak listesi değil tarif** *(writing-skills: match the form to the failure)*: kapanış mesajı
  "üç şeydir" diye tarif ediliyor; kalan yasaklar yalnız koşularda delinen üç tanesi.
- **Davranış envanteri:** 101'in döngüsü ve beş adımı, 108'in numaralı devri, 113'ün düzenleme
  yolu, 117'nin devir kapsamı, 118'in çağrılmayan kurucusu, 120'nin bağlamı — hepsi mevcut pin
  testlerinin cümleleriyle yeni metinde aynen duruyor; koruyucu o testler.

## Yeni metinler — `skills.py`

*(Aynen bu; pin cümleleri değiştirilmeden taşınmak zorunda.)*

**START_A_SCENARIO:** persona + döngü paragrafı *(dört geliş yolu: etiket, tarif, hiç, devir)* +
beş numaralı adım. Tam metin tur commit'inde; iskeleti: You are an expert scenario writer... →
Every step runs one loop... → 1. The plan ... 5. The handoff.

**GENERATE_PROMPTS_PLUS:** persona + kurucu ilkesi *(maps + build_prompts, elle asla)* + şema →
çift dosyayı bulma / iskelet → brief-craft kuralları → beşli parti + kurucu → düzenleme yolu.

Modül docstring'ine bir cümle: Madde 123'ten beri her metin persona ile açılır ve kelime tavanı
testte durur.

## Bilerek yapılmayanlar

- **Taban yönerge, şema, kural defteri ellenmez.**
- **Türkçe yok** — metinler İngilizce; persona da öyle.
- **`dist` derlenmez.**

## Beklenen yeşil

`test_skills.py`'ın tamamı — üç yeni pin ve korunmuş ~25 eski pin birlikte; defter çifti bilinen
kırmızı.
