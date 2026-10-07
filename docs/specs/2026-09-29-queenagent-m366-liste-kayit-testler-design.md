# Madde 366 (v9-7a) — Liste yeni biçimde çıkar: testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 366 · v9-7a. *Kararları: v9-7*
— 29 Eylül paragrafı 28 Eylül metnini geçersiz kılar.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor; biçim roadmap'te yazılı, ve
okuyan taraf — Queen Editor v8-3a — henüz yazılmadı, o yüzden biçimi bu madde koyar ve v8-3a onu okur.

## Ne değişiyor

`build_prompts` bugün `PROMPTS = [ """…""", ]` biçiminde bir string listesi yazıyor. Olacak: her kare
iki alanlı bir kayıt — `scene` ve `photo`.

- `scene`: yapı dosyasında karenin `scene` alanı, yazıldığı gibi — `add_scene`'in yazdığı tek cümle.
- `photo`: bugünkü prompt, hiç değişmeden.
- Başka alan yok: `video` 29 Eylül'de düştü, negatif liste listeye girmez *(v9-8e'nin işi, ayrı dosya)*.
- Kopyala-yapıştır akışı aynı: dosya yine Python, yine `PROMPTS = [`, değerler yine üç tırnak içinde
  ve sonda virgülle. Queen Editor'ün bugünkü okuyucusu `PROMPTS =`'yi atıp `ast.literal_eval`
  yapıyor; sözlükler de literal, o yüzden v8-3a aynı yoldan okuyabilir.

Beklenen dosya:

```python
PROMPTS = [
    {
        "scene": """Aylin yatakta uyanıyor.""",
        "photo": """score_9_up, …, 1girl, long teal hair BREAK waking up, …, sunlit bedroom""",
    },
]
```

## Kararlar (subagent'ın, kullanıcısız)

1. **Kayıtları `build_prompts` döndürür**, `render_module` yalnız yazar. Karelerin listesini
   (`frames`, eski dosyada `shots`) okuyan tek yer `build_prompts`; sahneyi başka yerde okumak ikinci
   bir okuma olurdu. Bugünkü prompt testleri bir `_photos` yardımcısıyla `photo` alanını okur —
   iddiaları değişmez.
2. **Sahnesi olmayan kare boş sahneyle çıkar**, reddedilmez. `write_missing_actions` sahnesiz kareyi
   zaten tanıyor, ve eski dosyaların karelerinde sahne olmayabilir; bir liste sahne yüzünden
   kurulamaz olmamalı.
3. **Alanların sırası `scene`, sonra `photo`** — okuyan önce ne istendiğini, sonra prompt'u görür.
4. **Aracın cevabı değişmez:** `Wrote N prompts to x.py.` Kare sayısı yine prompt sayısı.
5. **Modele giden tek değişiklik `build_prompts` aracının tarifi:** ilk satırı listede her karenin
   sahne cümlesiyle prompt'unun birlikte gittiğini söyler. Skill metinlerine dokunulmaz; kelime
   tavanları değişmez.

## Testler

`queen-agent/backend/tests/test_build_prompts.py`:

- Her kare bir kayıt: sahnesi ve prompt'u, `{"scene": …, "photo": …}`.
- Kaydın alanları yalnız `scene` ve `photo` — `video`, negatif yok.
- Sahnesi olmayan kare `scene: ""` ile çıkar.
- İki karenin sahneleri kendi karelerinde, sırasıyla.
- `render_module` kayıtları yukarıdaki biçimde yazar — tam metin sabitlenir.
- Yazılan dosya parse edilince kayıtlar geri gelir; tırnak, ters bölü ve Türkçe harf iki alanda da
  bozulmadan döner.
- Bugünkü prompt iddiaları `_photos` üstünden aynen kalır; string listesi yazan eski iki render testi
  kayıtlı hâline döner.

`queen-agent/backend/tests/test_tools.py`:

- `build_prompts` aracının yazdığı dosya parse edilince her karenin sahnesi ve prompt'u kendi kaydında.
- Aracın tarifi sahneyi anıyor.

Frontend'e dokunulmaz: dosya panelinin `Copy`'si dosyanın tamamını kopyalıyor *(Madde 193)*, biçimi
okumuyor.
