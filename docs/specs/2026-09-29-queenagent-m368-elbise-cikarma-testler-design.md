# Madde 368 (v9-9) — Elbise çıkarma sahnesi senaryoya, aksi söylenmedikçe eklenmez: testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 368 · v9-9.

**Kullanıcıdan gereken:** yok. Madde `ALIGNED`, kullanıcının sözleri satırda; karar, dosya ya da ölçüm
beklenmiyor.

## Ne değişiyor

Start a scenario'nun sahneleri yazdığı adım *(Step 4 -- the scenes)* bugün kıyafetin değişmesi
hakkında hiçbir şey söylemiyor. Kıyafeti farklı iki sahne arasında model, elbisenin çıkarıldığı ya da
değiştirildiği ara kareleri yazmaya çalışıyor, ve zayıf model o kareleri çizemiyor *(kullanıcı, 29
Eylül)*.

O adım bundan sonra iki şeyi söyler:

1. **Kıyafet bir sahneden ötekine değişebilir** — bir sahnede bir elbise, sonrakinde başka biri.
2. **Elbisenin çıkarıldığı ya da değiştirildiği an sahne olarak yazılmaz, kullanıcı istemedikçe.**
   Kullanıcı açıkça isterse o sahne yazılır.

Kural yalnız bu adımda durur *(kullanıcı, 29 Eylül — "senrayoda olsa yeter")*: Edit prompts'a, kare
yazarına ya da araç tariflerine girmez.

## Kararlar (subagent'ın, kullanıcısız)

1. **Test, kuralın yerini tutar:** metin Step 4'ün başlığıyla Step 5'in başlığı arasında kesilir, ve
   kural o dilimde aranır. Başka bir adımda duran kural, sahneleri yazarken okunmaz.
2. **Test olguyu üç parçayla tutar**, cümlenin tamamını değil — nasıl yazılacağı uygulama spec'inin
   işi:
   - `from one scene to the next` — kıyafetin sahneler arasında değişebildiği;
   - `taken off` — yazılmayan anın ne olduğu;
   - `unless the user asks` — istisna.
   Hepsi küçük harfe çevrilmiş dilimde aranır, cümlenin başına düşen bir kelime büyük harfle
   başlayabilsin diye.
3. **"Yalnız orada" aynı testte tutulur:** `taken off` Step 4 diliminin dışında, Start a scenario'nun
   geri kalanında ve Edit prompts'ta geçmez. Ayrı bir yokluk testi, metin hiç okunmadan da yeşil olurdu
   *(test_skills.py bu tuzağı zaten anlatıyor)*; burada önce varlık istenir, sonra yokluk.
4. **Kare yazarı ve araç tarifleri teste girmez.** `WRITE_FRAME_SYSTEM_PROMPT`'ın "take it off"
   cümlesi başka bir kural — aksiyon satırı bir kıyafeti çıkarmasın — ve bu madde ona dokunmaz.
5. **Kelime tavanı değişmez** *(1000, Madde 367)*: kural bir cümle, tavanın bıraktığı yerin içinde.

## Testler

`queen-agent/backend/tests/test_skills.py`:

- Sahneler adımı kıyafetin sahneden sahneye değişebildiğini, çıkarıldığı anın kullanıcı istemedikçe
  yazılmadığını söyler; bu kural o adımın dışında ve Edit prompts'ta geçmez. — **kırmızı**

Frontend'e ve queen-editor'e dokunulmaz.
