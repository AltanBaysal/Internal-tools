# Madde 77 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m77-secici-proje-ekraninda-uygulama-design.md](../specs/2026-08-26-queenagent-m77-secici-proje-ekraninda-uygulama-design.md)
**Kırmızı testler:** `d08d2f5` — ön yüzde 11.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `ProjectScreen.jsx` — yazma kutusu bir `foot` alır

İki seçici içe aktarılır ve `Composer`'a `foot` olarak verilir: `SkillPicker`, sonra `ModelPicker`.
Sıra `ChatScreen`'inkiyle aynı.

Bileşen altı yeni prop alır ve hiçbirini kendi tutmaz: `skill`, `model`, `picker`, `onPicker`,
`onSkillChange`, `onModelChange`.

*Yeşile döner:* `ProjectScreen.test.jsx`'in dört kırmızısı.

### 2. `App.jsx` — fork proje ekranına döner

Açılış etkisi `/p/${landing}/c/new` yerine `/p/${landing}`'e yönlendirir. `replace` kalır. 65'in
oraya koyduğu gerekçe yorumu silinir — artık geçerli değil, ve duran bir yanlış gerekçe bir sonraki
okuyanı yanıltır. Yerine bu maddenin gerekçesi yazılır.

*Yeşile döner:* `App.test.jsx`'in beş çevrilen testi ve tersine dönen sidebar testi.

### 3. `App.jsx` — prop'lar bağlanır

`ProjectScreen`'e altı prop geçirilir. Hepsinin karşılığı zaten var ve taslak sohbetin `drafting`
dalının kullandığıyla aynı: `lastSkill` / `lastModel`, `setLastSkill` / `setLastModel`, `picker` /
`togglePicker`.

*Yeşile döner:* seçilen skill'in başlayan sohbete geçtiğini söyleyen yeni test. `startChat` bugün
de ikisini `startChatInProject`'e geçiriyor, yani bağlanacak fazladan bir şey yok — bu adım o yolu
**açıyor**, kurmuyor.

### 4. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**. FOUNDATION 3. karar ve
`test_dist_is_committed.py`.

## Beklenen yeşil

Ön yüzde **493**, hepsi yeşil. Arka uçta **2 failed, 432 passed** — ikisi defterin dalı, bu
maddenin değil.

Başka bir dosyanın düşmesi beklenmiyor. `ChatScreen`, `Composer` ve iki seçici bileşen
değişmiyor; `App`'in silme testleri kendi adreslerini itiyor.

**Koşuda çıkan iki şey, ikisi de test turunun kendi hataları:**

- Sidebar'ın düğmesinin erişilebilir adı `+New chat` — artının kendisi de ada giriyor. Test tam
  eşleşme arıyordu; içerene çevrildi.
- Yeni testin sahte sunucusu sohbetin GET'ine boş **liste** döndürüyordu. Ekran ona `messages`
  diye baktı ve konsola bir `TypeError` düştü. Test yine de geçiyordu — yani hatayı sessizce
  taşıyordu. Sahte sunucu artık gerçek bir sohbet döndürüyor.

**Vitest bu makinede yük altında zaman aşımına düşüyor.** Arka uç suite'iyle aynı anda koşturulduğu
bir turda on dört test kırmızı göründü, hepsi kendi dosyasının ilk testi ve hiçbiri bu maddeyle
ilgili değildi; tek başına koşulduğunda hepsi yeşil. **Ders:** iki suite'i paralel koşturup çıkan
kırmızıyı okumak, olmayan bir kırılmayı kovalamak demek.

## Bilerek yapılmayanlar

- **Taslak sohbet ekranı kaldırılmıyor.** Duruyor, seçicileri duruyor, sidebar'ın `New chat`
  düğmesi kapısı — ve bir test onu koruyor.
- **Seçim diske yazılmıyor.** Proje ekranında henüz sohbet yok; sohbetin kendi kaydı sunucuda
  doğduğu anda oluşuyor. Bu yalnız oturumun başlangıç değeri.
- **`workspace.css`'e dokunulmuyor.** `composer__foot` zaten var ve iki ekran onu paylaşıyor.
