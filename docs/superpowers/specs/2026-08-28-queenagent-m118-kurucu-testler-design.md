# Madde 118 — Akış kurucuyu çağırmaz · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 118.
**Gözlenen** *(28 Ağustos, beşinci deneme)*: sahne listesi yazıldıktan sonra akış kullanıcıyı
prompt+'a göndermedi; kapanışı *"şimdi build_prompts aracını çalıştır... istersen önce bir
karakter önizlemesi de yapabilirim. Onaylıyor musun, yoksa bir değişiklik var mı?"* oldu.

## Kök neden

108'in yasağı adıyla **frame yazmayı** söylüyor *("Frames are never written here")* ve model adı
konmuş yasağın etrafından dolaştı: frame yazmadı, **kurmayı** teklif etti. Kurucudan metinde hiç
söz edilmiyor; araç listesi ise her istekte tam gidiyor, yani çağırabilirdi — ve akışın bıraktığı
dosyada frames bilerek boş olduğu için boş bir prompt listesi üretirdi. Kapanışın soruya dönmesini
taban yönergenin *"ask the one question that decides what happens next"* cümlesi de besliyor;
devir adımında o soru yok, çünkü sıradaki hamle kullanıcının skill menüsündeki seçimi.

## Kural

İki cümle, devir adımına *(5. adım, frame yasağının ardına)*:

1. `build_prompts` burada asla çağrılmaz — kurucu da o skill'indir, ve bu akışın bıraktığı
   dosyada kuracağı frame yok.
2. Devir mesajı bir şey önermez ve bir şey sormaz — ayakta duranı ve işin nerede sürdüğünü
   bildirir.

## Test — `test_skills.py`, akış bölümüne iki yeni

Sabitlenen parçalar *(tur 2'nin yazacağı cümlelerden)*:

| Test | Aradığı |
|---|---|
| akış kurucuyu çağırmaz | `build_prompts is never called here` |
| devir önermez ve sormaz | `offers nothing and asks nothing` |

`build_character_prompts` metinde duruyor ve `build_prompts`'u alt dizi olarak içermiyor —
birinci pin onu yanlışlıkla yakalayamaz.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2'nin işi.
- **`modes.py` ellenmez** — araçların istekte durması Madde 99'un kararı; iş metnin.
- **Taban yönergenin tek-soru cümlesi ellenmez** — doğru cümle; devir adımı onun istisnası ve
  istisna akışın kendi metnine yazılır.
- **2. adımın önizleme teklifi ellenmez** — *"Offer it"* karakter adımının kendi işi; yasak yalnız
  devir mesajının üstüne binen teklife.
- **`dist` derlenmez.**
