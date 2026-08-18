# Madde 26 — Model seçici · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 26](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 32, 34, **35** · karar **1** · `HANDOFF.md` §3, §5
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Tasarımın dört modeli yok

Tasarım dört satır çiziyor — Grok 4, Grok 4 Fast, Grok 4 Heavy, Grok Code — ve her birine bir cümle
yazıyor. **Bu adların hiçbiri gerçek değil**; prototipin yer tutucuları. xAI'nin kendi belgesinden
(18 Ağustos 2026'da okundu, `docs.x.ai/docs/models`) çıkan metin modelleri ve fiyatları:

| Kimlik | Bağlam | Girdi /1M | Çıktı /1M |
|---|---|---|---|
| `grok-4.6` | 500k | $2.00 | $6.00 |
| `grok-4.5` | 500k | $2.00 | $6.00 |
| `grok-4.3` | 1M | $1.25 | $2.50 |
| `grok-4.20-0309-reasoning` | 1M | $1.25 | $2.50 |
| `grok-4.20-0309-non-reasoning` | 1M | $1.25 | $2.50 |
| `grok-4.20-multi-agent-0309` | 1M | $1.25 | $2.50 |
| `grok-build-0.1` | 256k | $1.00 | $2.00 |

İstem 200k tokenı geçtiğinde her satır ikiye katlanıyor.

**Kullanıcı kararı: yedisi de menüde.** Gerekçesi kendi cümlesi — ucuz ama zayıf modeller var ve
denge ancak hepsi görünürse kurulur.

**Sapma, bilerek:** tasarımın açıklama cümleleri düşüyor, yerine satırın **fiyatı ve bağlamı**
geçiyor. Belgenin yalnız `grok-4.6` için bir tavsiyesi var ("the most intelligent and fastest model
we've built"), gerisi için tek cümle yok — kalan altısına cümle yazmak uydurmak olurdu. Fiyat ise
hem doğru hem seçimin asıl konusu.

---

## 2 · Varsayılan sunucunun ayarıdır

**Kullanıcı kararı:** varsayılan "şu an kullandığımız" olur, yani `config.XAI_MODEL` — bugün
`grok-4.5`.

Bunun bir sonucu var: `XAI_MODEL`'in anlamı değişiyor. Bugüne kadar **tek model**di, bundan sonra
**yeni bir sohbetin varsayılanı**. Ayar değişince menüdeki seçim değil, seçilmemişin karşılığı
değişir. Yorumu buna göre düzeltilir.

Bu tek şeyi yalnız sunucu bilir, o yüzden `GET /api/model` → `{"default": "<kimlik>"}` diye küçük bir
uç nokta açılıyor. Etiketler ve fiyatlar arayüzde kalıyor — onlar metin, ve metin arayüzün işidir.

**Liste doğrulanmıyor.** Arka uç kendisine verilen kimliği saklar ve gönderir; yanlış bir kimlik
xAI'nin kendi hata gövdesiyle döner ve Madde 16'nın dürüst hata kartında görünür. Uydurma bir sebep
yazmamak zaten bu deponun kuralı; ikinci bir liste tutmak da kaymaya davetiye olurdu.

---

## 3 · Seçim sohbete yapışır (fark 34)

| Nerede | Ne |
|---|---|
| `Chat.model` | sohbetin kendi seçimi; **boş olabilir** |
| boşsa | sunucunun varsayılanı kullanılır |
| API cevabı | boşluk **çözülmüş** hâliyle döner, yani istemci hep bir ad görür |

Boş bırakılabilmesi bir göç olmaması içindir: diskte bugün duran sohbet kayıtlarında böyle bir alan
yok, onlar olduğu gibi okunmaya devam eder ve varsayılanla cevaplanır.

Değiştirme: `PATCH /api/projects/<pid>/chats/<cid>` → `{"model": "<kimlik>"}`. Konuşmanın ortasında
çalışır; bir sonraki cevap yeni modelle üretilir, geçmiş mesajlar olduğu gibi kalır.

Model **çağrı başına** taşınır: `Engine.stream(messages, tools, model)` ve `XaiClient` verilmemişse
kendi ayarını kullanır. Sohbet başına ayrı bir istemci kurmak, tek fark bir dize iken üç nesne
üretirdi.

---

## 4 · Düğme nerede (fark 35, karar 1)

Sözleşmenin iki hâli çelişiyordu — markdown hâli sol alt, sayfa hâli sağ alt. **karar 1 sağ altı
seçti:** composer'ın alt satırında sırayla **Skills · model · Send**. Skills henüz doğmadı; bu
maddede model düğmesi Send'in solunda durur, Madde 27 Skills'i onun soluna ekler.

**Yalnız sohbet composer'ında.** `HANDOFF.md` §5 böyle diyor ("Bottom-left of the chat composer") ve
Home ile proje ekranındaki kutular sohbet başlatır: orada seçilecek model, doğacak sohbetin modeli
olurdu ve tasarım oraya bir seçici koymuyor. Yeni sohbet **son seçimle** doğar (fark 34).

**Son seçim oturumda durur** (App'in durumunda), diske yeni bir tercih dosyası açılmaz. Yeniden
başlatınca yeni bir sohbet sunucunun varsayılanıyla doğar; sohbetlerin kendi seçimleri diskte olduğu
için yerinde kalır — yol haritasının ölçütü bu. Küçük ve geri alınabilir seçim, o yüzden sorulmadı.

Kapalıyken: model adı + küçük şevron, hover'da soluk dolgu. Açıkken Madde 25'in kutusu: mono `MODEL`
başlığı, satırlar, seçilinin yanında `✓`. Genişlik **296px** (fark 32) — kutuya değil bu çağırana
ait, Madde 25 böyle kurdu.

---

## 5 · Katman denetimi

**Arka uç:** `domain/chat.py` (`model` alanı), `domain/ports.py` (`Engine.stream` imzası,
`ChatStore` değişmiyor), yeni `domain/usecases/set_chat_model.py`, `data/xai_engine.py`,
`services/xai/client.py`, `presentation/routes.py`, `web/app.py` (varsayılanı geçirir), `config.py`
(yorum). Katman yönü korunuyor: domain hâlâ hiçbir şeye bakmıyor, model bir dize olarak geçiyor.

**Ön uç:** yeni `features/workspace/models.js` (yedi satır, metin), yeni `ModelPicker.jsx`,
`Menu.jsx` (başlık + `detail` + `checked` alır), `Composer.jsx` (`foot` yuvası), `ChatScreen.jsx`,
`App.jsx`, `shared/api.js`, `workspace.css`.

`Menu` genişletiliyor, kopyalanmıyor — Madde 25'in maddesi buydu.

---

## 6 · Kabul ölçütü

1. Sohbet composer'ının ayağında, Send'in solunda, o sohbetin modelinin adını taşıyan bir düğme var.
2. Basınca `MODEL` başlıklı menü açılır; yedi satır, her birinde ad ve fiyat, seçilide `✓`.
3. Seçmek sohbete yazılır; başka sohbete gidip dönünce o sohbetin kendi seçimi durur.
4. Yeniden başlatınca sohbetlerin seçimi yerinde kalır.
5. Yeni sohbet, o oturumdaki son seçimle doğar; hiç seçim yapılmadıysa sunucunun varsayılanıyla.
6. Cevap, o sohbetin modeliyle üretilir.
7. Model alanı olmayan eski bir sohbet kaydı okunur ve varsayılanla cevaplanır.

## 7 · Risk

Kimlikler ve fiyatlar 18 Ağustos 2026'da okundu; xAI listesini değiştirirse menü eskir. Yanlış bir
kimlik sessizce değil, servisin kendi sözleriyle patlar. Fiyatların menüde durması tasarımdan gelen
bir şey değil, kullanıcının isteği.
