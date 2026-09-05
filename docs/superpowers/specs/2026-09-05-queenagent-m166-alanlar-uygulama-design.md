# Madde 166 · uygulama turu — iki satır, ve yalan söylemeye başlayan üç yorum

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m166-alanlar-testler-design.md) ve
[v7 yol haritası, Madde 166](../plans/2026-09-05-queenagent-v7-roadmap.md).
Commit `3d7a10d` üç kırmızıyı çiviledi; bu tur onları yeşile çevirir ve başka hiçbir şeyi kırmızıya
düşürmez.

---

## Kod — `build_prompts.py`, iki satır

**Satır 51** *(`build_prompts` içinde)*

```python
lead = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]
```
→
```python
lead = [DEFAULT_QUALITY]
```

**Satır 97** *(`build_character_prompts` içinde)*

```python
quality = structure.get("quality") or DEFAULT_QUALITY
```
→ değişken kalkar, `DEFAULT_QUALITY` doğrudan kullanılır. İki satırlık bir isim, tek yerde
okunuyorsa isim olmayı hak etmiyor.

**Dokunulmayan:** satır 60'ın `lead.append(frame.get("camera", ""))`'ı. `camera` okunmaya devam
ediyor; onu **yazan** araç 173'te gidiyor, okuyan taraf eski dosyalar için duruyor — `shots`
fallback'inin kuralı.

## Yorumlar — üç tanesi bugünden sonra yalan

Kod satırı değişince yanındaki gerekçe de değişir; CLAUDE.md'nin kuralı bu
*(**bir yorum NEDEN'i söyler, ve yalnız bugün doğru olanı**)*.

| Nerede | Bugün ne diyor | Neden yalan olacak |
|---|---|---|
| `DEFAULT_QUALITY`'nin yorumu | *"A scenario that needs a different one writes quality in its own file and this steps aside."* | O kapı kapanıyor. Yerine **neden** kapandığı yazılır: iki yer bir zincir üstünde anlaşmazlığa düşebilir, ve dosyaya yazılan zincir şema örneğinden kopyalanmış zincirdi |
| `build_prompts`'un sıra yorumu | *"The count is placed, never worked out: the code knows who entered the frame but not what they are, and no field says so."* | Yerleştirilecek sayı kalmadı. Sayının **karakterin kendi girdisinde** durduğu yazılır |
| `build_character_prompts`'un docstring'i | *"No count: how many people are in a picture is a frame's own field, and there is no frame here."* | Karenin böyle bir alanı yok. Sayı karakterin girdisinde olduğu için bu yolda da **kendiliğinden** doğru geliyor — cümle tersine döner |

`_worn`'un ve `_block`'un yorumları duruyor: kadro okuma ve komşuluk kuralı değişmedi.

## Şema açılmıyor

Test turu spec'inin kapsam düzeltmesi burada da geçerli. `schema.py` modele hâlâ `people` ve
`quality` yazmasını söylüyor, kod artık okumuyor — **pencere bilerek açık**, 172'de şemayla birlikte
kapanıyor. Deneme Dilim 1'in sonunda koşuluyor, yani dışarı çıkmıyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: üç kırmızının üçü de yeşil**, ve `queen-agent` tarafında **690 yeşil**
   *(3d7a10d'de 687 + 3)*. Yeni kırmızı çıkarsa yayılma alanı ölçümü eksikti.
3. Öteki üç takım *(`queen-agent/frontend` 586, `queen-editor` 739, `queen-editor/frontend` 591)*
   rakamlarını korur — bu madde bir domain modülünün okuduğu alanları değiştiriyor, başka hiçbir
   yere dokunmuyor.
4. `dist` derlenmez: ön yüz açılmadı.
