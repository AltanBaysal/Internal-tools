# Madde 65 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-25-queenagent-m65-acilis-testler-design.md](../specs/2026-08-25-queenagent-m65-acilis-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/frontend/src/App.test.jsx` — iki test yeniden yazılır, iki testin beklediği adres
değişir, bir test eklenir. Başka dosyaya dokunulmaz.

## Testler

**1. `the app opens on the first project's draft chat`** *(var olan `the app opens on the first
project` yeniden yazılır)*

Tek projeli liste (`p1` / "Thesis"), render. Adres `/p/p1/c/new` olmalı. Sidebar satırında proje
adı hâlâ durmalı (`.sidebar__row-name`), ama proje ekranının başlığı **olmamalı**
(`.screen__title` sorgusu boş dönmeli) — çizilen şey sohbet ekranıdır.

Adı değişiyor çünkü eski iddia artık yanlış; yanına ikinci bir test koymak ikisini çelişkide
bırakırdı.

**2. `a skill can be picked before anything is typed`** *(yeni)*

Aynı liste, render. Hiçbir metin yazılmadan **Skills** düğmesine tıklanır, açılan menüden
**Create scenario** seçilir. Düğmenin yazısı artık "Create scenario" olmalı.

Bu, maddenin kabul kriteri: adresin doğru olması yetmez, o adreste seçicinin gerçekten çalışması
gerekir.

**3. `the project screen is still reached from the sidebar`** *(yeni)*

Render edilip taslak sohbete düşülür, sonra sidebar'daki proje satırına (`.sidebar__row-open`)
tıklanır. Adres `/p/p1` olmalı ve proje başlığı `.screen__title` içinde "Thesis" yazmalı.

**4. `/settings is an address like any other unknown one`** *(var olan test, beklenen adres
değişir)*

Testin kendisi aynı kalır — tanınmayan adres çatala düşer. Yalnız beklenen sonuç `/p/p1` yerine
`/p/p1/c/new` olur, ve `.screen__title` iddiası düşer çünkü artık proje ekranı çizilmiyor.

**5. `the fork is not written into the history`** *(var olan test, yalnız beklenen adres değişir)*

`replaceState` çağrıldı, `pushState` çağrılmadı iddiaları **aynen durur**. Beklenen adres
`/p/p1/c/new` olur.

## Beklenen kırmızı

**Beşi de kırmızı**, ve hepsi tek sebepten: çatal hâlâ `/p/p1` diyor. 1 ve 4 adresi doğrudan iddia
ediyor, 5'in `waitFor`'ı yeni adresi hiç görmediği için zaman aşımına düşüyor.

**3, önkoşulu yüzünden kırmızı.** İlk satırı taslak sohbete inildiğini bekliyor; inilmediği için
sidebar'a hiç tıklanamıyor. Yani kırmızılığı sidebar'ın bozukluğunu göstermiyor — sidebar bugün de
çalışıyor. İkinci turdan sonra bu test bir gerileme kalkanına dönüşür: kırılırsa, kırılan şey
açılış değil proje ekranının kapısıdır.

*(Bu satır önce "3 bugün yeşil geçer" diyordu. Test yeni açılışın üstüne kurulduğu için yanlıştı;
tahmin düzeltildi, test değil.)*

`python -m pytest queen-agent -q` yeşil kalır — bu madde arka uca dokunmuyor.

## Bu turda yapılmayan

`App.jsx`'e dokunulmaz — çatalın hedefi ikinci turda değişir. `dist` derlenmez: ön yüz kaynağı
değişmiyor, yalnız testler değişiyor.
