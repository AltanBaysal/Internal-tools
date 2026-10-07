# Madde 82 — Model seçme sistemi sökülür · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m82-model-secimi-sokulur-testler-design.md) ·
**Testler:** `0643b00` — arka uçta 8 kırmızı, ön yüzde birkaç.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Arka uç: alan gider, zincir gider

**Domain.** `Chat.model` siliniyor. `start_chat` `model` parametresini bırakıyor.
`set_chat_choices` → **`set_chat_skill`**: tek alan kalınca `UNCHANGED` nöbetçisi de gereksiz —
o nöbetçi *"verilmedi"* ile *"boş verildi"*yi ayırmak içindi, ve tek alanlı bir çağrıda alan hep
veriliyor.

**Veri.** `file_chat_store` `model`'i ne yazıyor ne okuyor. Diskteki eski anahtar öylece duruyor ve
görülmüyor; sohbet bir daha yazıldığında düşüyor.

**Sunum.** `GET /api/model` gidiyor. `default_model` `make_workspace_bp`'den, `_sse`'den,
`_chat_json`'dan ve `_chat_summary`'den çıkıyor — dört imza sadeleşiyor. POST artık `model`
okumuyor; PATCH yalnız `skill` kabul ediyor ve hata cümlesi de öyle diyor.

**Motor yolu.** `stream_answer` `engine.stream(conversation, tools=TOOL_SPECS)` diyor.
`XaiEngine` ve `XaiClient` `model` parametresini bırakıyor; istek `{"model": self._model, ...}`
oluyor. `main.py` bir argüman az geçiyor.

`config.XAI_MODEL` **kalıyor** ve modelin adının geçtiği tek yer oluyor.

## Ön yüz: seçici gider, etiket gelir

`ModelPicker.jsx` ve `models.js` siliniyor. Yerine `ModelLabel.jsx` — prop'suz, durumsuz, tek
`<span>`:

```jsx
export default function ModelLabel() {
  return <span className="model-label">Grok Build</span>;
}
```

Adı burada yazılı. `config.py` id'yi tutuyor, bu dosya insan okuyan hâlini; Python ile JS
birbirini okuyamıyor, ve bu sınır 72'den önce de aynen buradaydı — orada da bir test *sözle*
eşleştiriyordu. **Bedeli:** ortamdan `XAI_MODEL` ezilirse etiket bunu söylemez. Geliştirici işi, ve
geliştirici kendi ezdiğini bilir.

`App.jsx`'ten `lastModel`, `/api/model` çağrısı ve `chooseModel` gidiyor. İki ekrandan `model` ve
`onModelChange` prop'ları gidiyor. `startChatInProject` `model` parametresini bırakıyor.

## Yanında gelen iki sadeleşme

**`picker` → `skillsOpen`.** Geriye tek menü kaldı; `"model" | "skills" | null` üçlüsü bir
boolean'a iniyor. `onPicker` → `onToggleSkills`.

**Escape sırası dörde iniyor.** `fark 67` beş şey sıralamıştı: proje menüsü → onay kutusu → Skills →
model → açık panel. Model adımı kapatacak bir şey bulamıyor artık, ve çevresindekiler yerinde
kalıyor.

## Neden adlandırmalar bu turda

Test turu bunları denedi ve geri aldı — ikisi de aynı dersi verdi:

- Olmayan bir modülü import eden test dosyası **pytest'in toplama aşamasını** düşürüyor, ve o zaman
  turun hiçbir kırmızısı görünmüyor.
- Paylaşılan bir fixture'ın imzasını daraltmak, o dosyadaki **her testi** tek bir çağrının imzası
  yüzünden düşürüyor — kırılma gibi okunuyor, tur gibi değil.

İkisi de kodun şeklini takip eden şeyler. Davranış zaten test turunda çivilendi; burada yalnız
adlar yerine oturuyor, ve bunu yaparken **testlerin de adı düzeliyor** — `test_set_chat_choices.py`
→ `test_set_chat_skill.py`, ve iki ekranın `picker` geçen testleri.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `config.XAI_MODEL` | Modelin adının geçtiği tek yer |
| `SkillPicker`, `Menu` | Orada gerçekten bir seçim var |
| `.picker` CSS kuralı | Skills düğmesi kullanıyor |
| Mesaj kayıtları | Model mesajda değil sohbette duruyordu |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** İkisi de yeşil; arka uçta yalnız defterin iki kırmızısı kalır. Toplam sayı
koşulunca yazılır — bu turda hem silinen hem eklenen test var.

**Düşmemesi gerekenler:** skill seçiminin bütün testleri, `Menu` ve `SkillPicker`, ve
`test_config.py`. Biri düşerse sökülen şey sökülmemesi gereken bir yere dokunmuş demektir.

`dist` **kaynağıyla aynı commit'te** derleniyor.
