# Madde 190 — okumanın kod geçişi · test turu

**Kaynak:** [yol haritasının Madde 190'ı](../plans/2026-09-06-queenagent-v8-roadmap.md),
[düzeltme log'u](../../2026-09-09-queenagent-metin-duzeltmeleri.md) *(35 kayıt)* ve
[okuma kopyası](../../2026-09-09-queenagent-modele-giden-metinler.md) *(metinlerin yeni hâli)*.

## Ne kanıtlanacak

Okuma 10 Eylül'de kapandı: 35 düzeltme, bekleyen karar yok. Düzeltilen cümleler **belgede** yeni
hâliyle duruyor, kodda hâlâ eskisi. Bu iki tur o farkı kapatıyor.

**Belge, kodun ne demesi gerektiğinin tanımıdır.** Uygulama turunun işi `prompt.py`'yi §1, §3, §4,
§5 ve §6'ya eşitlemek; bu turun işi o eşitliği tutan testleri yazmak.

## Kapsam: altı blok

| Blok | Metin | Log'da | Bugün kodda |
|---|---|---|---|
| A | `SYSTEM_PROMPT` | 1–6 | 2. ve 4. paragraf eski |
| B | `START_A_SCENARIO` | 7–18 | numaralı adımlar, eski döngü kuralları |
| C | `EDIT_PROMPTS` | 19–24 | tek paragraflık arıza listesi |
| D | `WRITE_FRAME_SYSTEM_PROMPT` | 25–28, 33 | dört paragraf |
| E | `SDXL_PROMPT_RULES` | 16, 30, 34 | dört paragraf, örnekli |
| F | §6'nın 18 araç metni | 30, 35 | eski tarifler |

**205–208 bu geçişin işini küçülttü:** dört aracın metni hiç inmeyecek, ve 10, 18, 29, 31, 32
numaralı düzeltmeler o maddelerle birlikte zaten indi.

## Testlerin nasıl değişeceği

Kaydın kendi cümlesi: *"`test_prompt.py`'nin cümle tutan testleri **kuralı tutacak** şekilde
gevşetilecek — silinmeyecek, çünkü her biri bir denemenin dersi."*

Yani hiçbir test silinmiyor. Bir testin tuttuğu **dizge** değişiyorsa, iddiası yeni metnin aynı
kuralı söylediği yere taşınıyor. Üç kalıp çıktı:

1. **Dizge değişti, kural aynı.** *"the first step whose box is empty"* → *"where the work
   stopped"*. Test yeni cümleyi tutar.
2. **Kural başka metne taşındı.** Sayı ve `pov_` kuralı ortak SDXL metninden `add_character`'ın
   `tags` alanına indi *(34)*. Test bakacağı yeri değiştirir, iddiasını değil.
3. **Kural artık kodun kendisinde.** Akışın 4. adımı kadroyu sormayı bıraktı *(14)*, çünkü
   `add_scene`'in imzası zaten soruyor. Test aracın alan metnine bakar.

## Kırılan testler

**A — `SYSTEM_PROMPT`** *(5)*: taze okumanın kimin için olduğu *(2, 3)*, okumanın sınırı *(2)*,
açık dosyaların hep güncel olduğu *(4)*, değişikliğin hangi araçtan geçtiği *(5)*, ve düzeltmenin
dosyaya yazılması *(6)*.

**B — `START_A_SCENARIO`** *(19)*: adım başlıkları `1. The plan` → `Step 1 -- the plan` olduğu
için sırayı indeksle ölçen **altı** test; döngü kurallarının beş cümlesi *(7, 8)*; planın nereden
devam ettiği *(11)*; ilk turun cümlesi *(10)*; sahne listesinin dili *(15)*; kapanış cümlesi *(15)*;
kadronun sorulduğu yer *(14)*; ve iki **yeni** iddia — nerede kalındığını dosyalar söyler *(11)*,
karaktere isim uydurulmaz *(17)*.

**C — `EDIT_PROMPTS`** *(1)*: elle prompt yazma **yasağı** tarife döndü *(24)*.

**D — `WRITE_FRAME_SYSTEM_PROMPT`** *(0)*: 33 numara metnin tamamını yeniden yazdı ama tutulan her
dizgeyi korudu. Bu blokta kırmızı yok — ve bu, okumanın testleri gözeterek yazıldığının kanıtı.

**E — `SDXL_PROMPT_RULES` ve alan metinleri** *(9)*: sayı, `solo`, `pov_`, kıyafet ve mekân
kuralları ortak metinden **alanlarına indi** *(34)*, ve etiket örnekleri kalktı *(30)*. Dokuz test
bakacağı yeri değiştiriyor, iddiasını değil.

**İki bekçi, bugün yeşil:** editör metninin kelime tavanı 200'den **260**'a çıkar *(20)*, ve her
skill'in ne için yazdığını söylediğini tutan test tek bir cümlenin lafzını değil **SDXL**'i tutar
*(22 rol paragrafını kısalttı)*.

## Bu turda yazılmayanlar

- **Kod açılmıyor.** `prompt.py` uygulama turunda değişir.
- **Yeni kural için yeni test yazılmıyor**, iki istisna dışında: 17 numara karaktere **isim
  uydurmayı** yasakladı ve bunu tutan test yok; 11 numara *"nerede kalındığını dosyalar söyler"*
  dedi ve bu, kutuya bakan eski testin yerine geçen yeni bir iddia.
- **Araçların cevap cümleleri** kapsam dışı: onlar `tools.py`'de, modele *söylenen* değil *geri
  söylenen* metinler.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Otuz dört test kırmızı**, iki bekçi yeşil, geri kalan süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-10-queenagent-m190-test-plan.md).
