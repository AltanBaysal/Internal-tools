# Madde 77 — Seçiciler proje ekranına iner, açılış eskiye döner · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m77-secici-proje-ekraninda-testler-design.md) ·
**Testler:** `d08d2f5` — ön yüzde 11 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## İki hareket

### 1. Fork eski yerine döner

`App`'in açılış etkisi `/p/${landing}/c/new` yerine `/p/${landing}`'e yönlendirir. `replace`
kalıyor: fork bir ekran değil, ve tarihe yazılırsa geri düğmesi kullanıcıyı ona atıp tekrar
fırlatır.

65'in oraya koyduğu yorum da gidiyor — sebebi artık geçerli değil, ve geçerli olmayan bir sebep
yorumda durursa bir sonraki okuyan onu doğru sanar.

### 2. Seçiciler proje ekranına iner

`ProjectScreen`'in `Composer`'ı bir `foot` alır: `SkillPicker`, sonra `ModelPicker`.
`ChatScreen`'deki sıranın aynısı — `Skills · model · <eylem>`.

Altı yeni prop geliyor ve hepsi yalnızca aşağı geçiyor: `skill`, `model`, `picker`, `onPicker`,
`onSkillChange`, `onModelChange`. Ekran hiçbirini kendi tutmuyor.

`App` tarafında bağlanacakları **zaten var** ve taslak sohbetin kullandığının aynısı:

| Prop | Nereye bağlanıyor | Neden aynısı |
|---|---|---|
| `skill` / `model` | `lastSkill` / `lastModel` | Henüz sohbet yok, yani yazılacak kayıt yok |
| `onSkillChange` / `onModelChange` | `setLastSkill` / `setLastModel` | Taslak sohbetin `drafting` dalıyla aynı |
| `picker` / `onPicker` | `picker` / `togglePicker` | Escape'i tek dinleyici sahipleniyor |

İkinci bir yol açılmıyor: `startChat` bugün de `lastModel` ile `lastSkill`'i
`startChatInProject`'e geçiriyor. Seçim oraya düştüğü an, başlayan sohbet onunla doğuyor —
bağlanacak fazladan hiçbir şey yok.

## Neden bu, 65'in geri alınması değil de yerine geçmesi

65 bir adres değiştirmişti; bu madde bir ekranın eksiğini kapatıyor. Adres geri geliyor ama
**65'in çözmek istediği şey çözülmüş oluyor** — ilk saniyeden itibaren skill seçilebiliyor, ve
artık gerçekten açılışın kendisinde.

Taslak sohbet ekranı duruyor ve seçicileri de duruyor. Sidebar'ın `New chat` düğmesi onun kapısı,
ve bir test onu koruyor.

## Kapsam dışı

`ChatScreen` · `Composer` · `SkillPicker` ve `ModelPicker`'ın kendileri · `workspace.css`
*(`composer__foot` zaten var ve iki ekranda aynı)* · arka uç · model listesinin sadeleşmesi
*(Madde 72)*.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Ön yüzde **493**, hepsi yeşil. Arka uçta **2 failed, 432 passed** — ikisi defterin dalı, bu
maddenin değil.

`dist` **kaynağıyla aynı commit'te** derleniyor: iki ön yüz dosyası değişiyor.
