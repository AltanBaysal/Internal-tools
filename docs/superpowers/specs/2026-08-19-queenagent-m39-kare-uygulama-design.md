# Madde 39 — Shot düşer, frame gelir · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 39](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m39-kare-testler-design.md](2026-08-19-queenagent-m39-kare-testler-design.md) — kırmızı commit `486906a`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Listeyi okuma kuralı

```
frames = structure.get("frames") or structure.get("shots") or []
```

Sıra kuralı taşıyor: yeni ad kazanır, eskisi geri düşüştür. Boş bir `frames` listesi eskiye
düşüyor — teoride ikisini birden taşıyan bir dosyada garip, pratikte böyle bir dosya yok ve
sonucu zararsız: liste boşsa zaten "kare yok" denecek.

`"shots"` desteği **kalıcı değil, geçiş**. Ne zaman kalkacağını bugün söylemek dürüst olmaz —
kullanıcının diskindeki dosyaların ne zaman biteceğini bilmiyoruz. Koda bunun bir geçiş olduğu
yorumla yazılır; kalkması ayrı bir madde olur.

## 2 · Denetleyen beceri neden kare adı taşımıyor

`verify-shots` → `verify-prompts`. Beceri karelere değil, **promptların malzemesine** bakıyor:
haritalar, kalite etiketleri, kopyalar. Adının içindeki birim adı zaten yanlıştı; yeniden
adlandırma bunu düzeltmek için doğal an.

Menü satırı da düzeliyor: "Check the structure against the rules." → **"Check the structure files
against the rules."** Çoğul, çünkü bir projede birden çok yapı dosyası yaşıyor ve kural 3 tam da
ikisi arasındaki kaymayı arıyor.

## 3 · "medium shot" kalıyor

Kamera alanının örnek değeri `"medium shot, from slightly above"`. Buradaki "shot" **çerçeveleme**
demek — SDXL'in okuduğu standart bir etiket — ve birim adıyla ilgisi yok. Değiştirmek prompt dilini
bozardı.

Süpürge testi bunu biliyor ve yalnız bu ifadeyi dışarıda tutuyor. Kuralın tek cümlelik hâli: *birim
adı olarak "shot" gitti, kamera dili olarak kaldı.*

## 4 · Eski kayıtlar

Kimlikleri değiştirmek, kaydında eski adı taşıyan sohbetleri "tanınmayan beceri" durumuna düşürür.
Bu **zaten tasarlanmış** bir durum:

- `instruction_for` tanımadığı ada boş dize veriyor — o tur yönergesiz koşar, çalışmaya devam eder.
- `skillName` tanımadığı kimliği ham hâliyle gösteriyor — düğme `verify-shots` yazar.

Madde 46 modelde aynı deseni kullanacak. Yeni bir koruma yazılmıyor.

## 5 · Değişen dosyalar

| Dosya | Ne |
|---|---|
| `domain/build_prompts.py` | Liste okuma, hata satırları, `BadStructure` cümleleri, docstring ve yorumlar |
| `domain/skills.py` | `SPLIT_INTO_SHOTS` → `SPLIT_INTO_FRAMES`, `VERIFY_SHOTS` → `VERIFY_PROMPTS`, `RULEBOOK`, bütün metinlerdeki kelime, `INSTRUCTIONS` anahtarları, `intro-frames.json` |
| `domain/tools.py` | `build_prompts` tarifi, `MAX_ROUNDS` yorumu |
| `frontend/features/workspace/skills.js` | İki kimlik, iki ad, iki açıklama |

Başka hiçbir yer değişmiyor. Depo genelinde `shot` yalnız iki yerde kalır: `"medium shot"` kamera
örneği ve `docs/superpowers/` altındaki tarihli kayıtlar.

## 6 · Kabul ölçütü

1. Test turunun bütün testleri yeşil.
2. `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend` yeşil.
3. Kaynak dosyalarda birim adı olarak "shot" kalmadı.
4. Listesi `"shots"` altında olan eski bir dosya hâlâ prompt üretiyor.

## 7 · Bu maddenin kapsamadığı

Kare açıklamasının uzunluğu (Madde 43) ve dili (Madde 44) aynı yönergeyi yeniden yazacak; burada
yalnız kelime değişiyor. `docs/superpowers/` altındaki eski spec ve planlara dokunulmuyor: onlar
yazıldıkları günün kaydı.
