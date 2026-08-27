# Madde 102 — Ekran sorar · **test turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [izin tasarımı](2026-08-28-queenagent-izin-tasarimi-design.md) — ve onun kaynağı
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 102 ·
**Şartı:** 99 — arka yüz soruyor ve bekliyor *(`d6d6cf4`)*.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod bir sonraki turda.

---

## Kartın ne dediği

Testler metni sabitleyecek, o yüzden metin burada duruyor. QueenAgent'ın arayüzü bilerek İngilizce.

```
QueenAgent wants to run create_file
{"name": "plan.md", "content": "# Plan"}
[ Allow ]  [ Deny ]   Why not? (optional)
```

Argümanlar modelden geldiği hâliyle. Kod onları ayrıştırmıyor — `run_tool` tek ayrıştırıcı, ve
ikincisi ilk değişiklikte ondan ayrışır.

Sebep kutusu **Deny'ın işi**. Onaylarken söylenecek bir şey yok, ve onayın sebebi diye bir şey
modele gitmiyor.

## Neyin adı ne

| Ad | Nerede | Ne |
|---|---|---|
| `PermissionCard` | `features/workspace/PermissionCard.jsx` | Kartın kendisi |
| `permission` | `useChat`'in döndürdüğü | Bekleyen soru: `{tool, args}` ya da null |
| `answer(allowed, reason)` | `useChat`'in döndürdüğü | Kapıya cevabı gönderir, kartı kaldırır |
| `EDIT` | `features/workspace/modes.js` | `"edit"`, ve `DEFAULT_MODE` artık ondan türüyor |

Kare `arguments` diyor, kart `args`. Sebep dilin kendisi: `arguments` bir modülün içinde
değişken adı olamıyor, ve prop'u ayrıştırırken tam olarak o oluyor.

## Kip nerede değişiyor

Seçicinin değeri App'in oturum durumu *(Madde 86)*. Yani onayı `useChat` gönderiyor, kipi App
kaydırıyor — ikisi tek düğmenin altında, App'in bağladığı yerde. `useChat`'in kip diye bir şeyden
haberi yok, ve olması da gerekmiyor.

## Kırmızılar

### A · `PermissionCard.test.jsx` — kart *(yeni dosya)*

1. Aracın adını söylüyor.
2. Argümanları geldiği gibi gösteriyor.
3. Allow `onAllow`'u çağırıyor.
4. Deny kutudaki cümleyi taşıyor.
5. Kutu boşsa Deny yine reddediyor — sebep isteğe bağlı.

### B · `App.test.jsx` — akan turun içinde

1. İzin karesi gelince kart çıkıyor, ve tur hâlâ akıyor.
2. Allow sohbetin izin kapısına `allowed: true` gönderiyor.
3. Allow'dan sonra kip seçicisi **Edit** diyor.
4. Deny kapıya `allowed: false` ve kutudaki sebebi gönderiyor.
5. Cevap verilince kart iniyor.
6. Kart dururken gönder düğmesi hâlâ Stop — bekleyişin çıkış kapısı orada.
7. Cevaplanmadan biten tur kartı da götürüyor. Yoksa kart bir sonraki turun üstünde asılı kalır.

### C · `ModePicker.test.jsx` — Ask'ın satırı

8. Ask'ın açıklaması artık *"hiçbir şey yazılmaz"* demiyor. Madde 99'dan sonra yazılabiliyor —
   sorarak. Bugünkü cümle kullanıcıya yanlış bir şey söylüyor.

## Bekleyen turun testi nasıl kuruluyor

`gatedSse` zaten var: ilk kareleri veriyor, sonra bırakılmayı bekliyor. İzin sorusu birinci
parçanın son karesi oluyor; düğmeye basılıyor; kapıya giden POST'u karşılayan sahte `fetch`
akışı bırakıyor. Durdurma testinin kalıbının aynısı, ve zamanlamaya bağlı bir yeri yok.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Arka yüz | 99'da bitti; bu turda tek satırı değişmiyor |
| `Composer` | Kart dururken `thinking` zaten doğru, yani düğme zaten Stop |
| Nabız karesi | `parseFrame` onu bugün de düşürüyor; yazılacak satır yok |
| `sse.js` | İzin karesi ötekiler gibi bir kare |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Ön yüzde on üç kırmızı. Arka yüz bu turdan etkilenmiyor — oradaki iki kırmızı yine
`test_notebook`'un, ve defterin `BRANCH`'i koşu bitince `main`'e dönecek.
