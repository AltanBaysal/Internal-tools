# Madde 57 · Tur 1 (test) — Tasarım

**Madde:** [v4 yol haritası Madde 57](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** sunucu hücresini **ne tutacak**.

---

## Hücrenin işi

Uygulamayı arka planda başlatmak, kalktığını doğrulamak, dışarıya bir adres açmak, ve o adresi
neyin arkasında olduğuna dair doğru cümleyle birlikte basmak.

## Tutulacak kurallar

**1. Kök ortamla geçer.** Uygulama nereye yazacağını `QUEENAGENT_ROOT`'tan öğreniyor
([config.py](../../../queen-agent/backend/config.py)), ve defter onu Drive'a bakan yola ayarlıyor.
Bu bağlanmazsa uygulama sessizce ev dizinine yazar — Colab'ın yerel diskine, yani runtime ile ölen
bir yere. Kullanıcı çalıştığını sanar.

**2. Arka planda başlar.** `Popen`, `run` değil: `run` hücreyi sunucu ölene kadar bloklar ve
sonraki hiçbir satır çalışmaz.

**3. Kalktığı doğrulanır, ve düşerse sunucunun kendi log'u basılır.** Sebep uydurulmaz. Bir Flask
süreci onlarca sebeple ölür ve defter hiçbirini bilmiyor; bildiği tek şey `/api/health`'in cevap
verip vermediği.

**4. Adres cloudflared'den gelir.** Colab'ın kendi proxy'si POST taşımıyor (araştırma, yol
haritası), ve bu uygulama POST'suz hiçbir şey yapamıyor.

**5. Link, parolasız olduğu söylenerek basılır.** Uygulamada giriş yok — bu **kullanıcı kararı**,
ve kararın bedeli linki eline geçirenin her şeye erişmesi. Bunu söylemeyen bir çıktı, kullanıcıyı
bilmediği bir riske sokar. Uyarı linkin **yanında** durur; başka bir yerde yazılı olması, o an
linki kopyalayan kişiye ulaşmaz.

**6. Hücre açık kalır.** Bitmiş bir hücre Colab'a "burada iş kalmadı" der ve runtime boşta sayılıp
kapatılır — tünelle birlikte. `tail -f` hücreyi açık tutuyor ve aynı anda sunucunun log'unu
gösteriyor.

**7. Yeniden çalıştırmak güvenlidir.** Hücre ikinci kez koşarsa önceki süreçler öldürülür. Yoksa
8100 doluyken ikinci bir sunucu doğar ve hangisinin cevap verdiği belirsizleşir — bu oturumda
gerçekten yaşandı, eski bir sunucu bütün istekleri karşılamaya devam etti.

**8. CONFIG koşmadan koşmaz.** Diğer hücrelerdeki kapının aynısı.

## Sorulmayan

Tünelin gerçekten açıldığı, linkin gerçekten çalıştığı. Ağ yok. Bu testin cevapladığı şey defterin
doğru şeyi söylediği; doğru çalıştığını kullanıcının turu gösterir.
