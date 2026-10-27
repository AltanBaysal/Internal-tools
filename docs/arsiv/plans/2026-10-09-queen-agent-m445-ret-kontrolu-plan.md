# Madde 445 — Ret kontrolü, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım, **commit'lenmeden** — kontrolün metnini kullanıcı
> Changes'te okuyup onaylar, commit ana agent'ındır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** sözlü cevap DeepSeek'e kontrol ettirilir; ret ise istek aynen yeniden gider; çağrı
kontrolsüz geçer; beş denemeden sonra son deneme retse sohbette *"The model returned an error. Try
asking another way."* düz cevap, düğmesiz, yalnız saatle; teknikse 440'ın kartı.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m445](../specs/2026-10-09-queen-agent-m445-ret-kontrolu-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- queen-editor'e dokunulmaz; iki aracın metnini bağlayan test yazılmaz.
- `git add`, commit, stash yok.

---

## Görev 1: `Engine.stream_alone` — kontrolün yolu

- [ ] `test_model_engine.py`: `stream_alone("the instruction", "the answer")` client'a
  `[system, user]` olarak yalnız ikisini gönderir, QueenAgent'ın system prompt'u yok, araç yok; kesme
  yolunu geçirir. `test_ports.py`: imza testi `stream_alone`'u da ölçer. Kırmızı.
- [ ] `ports.py`: `Engine.stream_alone`, belgesiyle. `model_engine.py`: `stream_alone`. Yeşil.

## Görev 2: `prompt.py` — kontrolün metni

- [ ] `APPROVED` ve `CHECK`, belge dizeleriyle, modülün öbür metinleri gibi. (Metnin sözlerini tutan
  test yok: kullanıcı onu okuyup onaylayacak; kutunun testleri adlarıyla kullanır.)

## Görev 3: `black_box.py` — kontrol, ret, son deneme

- [ ] `test_black_box.py`: sahte `Tries` kontrolleri de senaryoyla cevaplar (varsayılan onay) ve
  neyin kontrole gittiğini tutar. Spec'in *Kutu* testleri. `test_a_good_answer…` sözlü+çağrılı
  cevabın kontrolsüz geçtiğini söyler. Kırmızı.
- [ ] `black_box.py`: `REFUSED`, `REFUSED_SAID`; deneme başına `Answer`; çağrı ve sessizlik
  kontrolsüz; sözler `_approved`'dan geçer; her başarısız denemede `stopped()`. Yorumlar. Yeşil.

## Görev 4: döngü ve kapı — sahteler ve ret testleri

- [ ] Tur koşan sahte engine'lere `stream_alone` (onay, `APPROVED` `prompt.py`'den):
  `test_stream_answer.py`, `test_chats_api.py` (üç sahte), `test_last_activity.py`,
  `test_pin_archive.py`.
- [ ] `test_stream_answer.py`: beş ret — mesaj `failed="refused"`, ret mesajı, adımlar kalır, başka
  istek yok; retli cevap sonraki turda gönderilmez. `test_chats_api.py`: beş ret kayıtta, `done`,
  `error` yok, doluluğa sayılmaz. Yeşil olmalılar (kod 3'te); kırmızıyı görmek için önce 3'ten önce
  koşulur.
- [ ] Yorumlar: `chat.py`'nin `failed`'ı, `stream_answer.py`'nin başarısız cevabı, `routes.py`'nin
  `failed` alanı.

## Görev 5: ekran — retli cevap

- [ ] `ChatScreen.test.jsx`: retli cevap `msg__text`'te ret mesajı, kart yok, Try again yok,
  `msg--failed`, damgası yalnız `11:05`. Kırmızı (damga ve sınıf).
- [ ] `ChatScreen.jsx`: `msg--failed` her başarısız cevapta; damganın `usage`'ı başarısız cevapta
  yok. Yorum. Yeşil.

## Görev 6: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
  `test_dist_is_committed` commit'e kadar kırmızı — beklenen.
