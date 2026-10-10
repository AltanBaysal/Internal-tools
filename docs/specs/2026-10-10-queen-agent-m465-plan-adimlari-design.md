# Madde 465 · Planın adımları sırayla — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
465 · **Dal:** `feat/queenagent-v10`, ana klasörde, worktree yok · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m465 planı](../plans/2026-10-10-queen-agent-m465-plan-adimlari-plan.md)

## Ne, neden

**Bugün** `SYSTEM_PROMPT` planı söyleyip aynı turda devam etmeyi söylüyor, ama adımların sırasını
söylemiyor. Model bir adımın kapsadığı her şey bitmeden sonrakine başlıyor *(kullanıcı, 10 Ekim —
"elindeki plan birden fazla step ise bir step bitmeden sonrakine geçme tarzı bir şey ekle, bunu çok
yapıyor çünkü"; "mesela plan 1. karakterleri oluştur 2. mekânları oluştur … karakter oluştur bitmeden
2.'yi yapmaya çalışıyor")*. Kullanıcı satırın Claude Code'un döngüsüne göre yazılmasını istedi
*("şuna göre yaz bence bu maddeyi" —
[How Claude Code works, the agentic loop](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop);
"gather context take action verify result")*.

**Olacak:** Planning bölümüne, *"Do not stop to ask for a yes to your plan"* satırının hemen altına,
kullanıcının onayladığı sözlerle tek satır:

> - Take a plan's steps one at a time, and run each step as its own loop: gather context, take
>   action, verify results. Start the next step only once the results show this step is complete.
>   Each step builds on what the one before it made, so a step left half done carries its gap into
>   every step after it.

Python dizgisi dosyanın üslubuyla satırlara bölünür; modele giden metinde tek satırdır, çünkü
`SYSTEM_PROMPT` her kuralı bir satırda tutar (Madde 455).

## Sınırlar

- Yalnız `prompt.py`'deki `SYSTEM_PROMPT`'a bu satır girer. Modele giden başka hiçbir metin, skill'ler,
  frontend ve queen-editor değişmez.
- Satırda skill'e özgü söz yok (`test_the_base_names_no_task`'ın yasakladığı görev kelimeleri yok):
  her skill'in ve kullanıcının kendi planına uyar.
- Test cümleyi değil anlaşmayı tutar: Planning bölümünün bir satırı adımların tek tek gittiğini ve
  doğrulandığını (*one at a time*, *verify*), bir satırı da sonraki adımın bu adım tamamlanınca
  başladığını (*next step*, *complete*) söyler. Kullanıcı cümleyi yeniden yazarsa test kırılmaz, kuralı
  düşürürse ya da Planning'den çıkarırsa kırılır.

## Maliyet

Disk ve ağ yok: metin modülde sabit.

**Token.** Satır 60 kelime; baştaki tire ve boşlukla 302, onlarsız 300 karakter. Her isteğe kabaca
65–75 token ekler (gerçek tokenizer'la sayılmadı).

**Önbellek.** `SYSTEM_PROMPT` her sohbetin önbelleğe alınan önekinin başında durur. Bu yüzden yeni
metinle devam eden her sohbet bir kez ıskalar ve yalnız yeni token'ları değil, bütün önekini baştan
önbelleğe yazar. Sonraki isteklerde önek yine önbellekten okunur.

**Tur.** Modele giden bir kuralın bedeli, yol açabileceği turları da kapsar: *"verify results"* modeli
her adımdan sonra bir okuma daha yapmaya itebilir. Satır hiçbir tool adı vermiyor. Reading bölümü de
zaten açık dosyaların modelin kendi yazdığını gösterdiğini, kendi yazdığını görmek için bir dosyanın
yeniden okunmayacağını söylüyor. Neyle doğrulanacağı ajanın kendi kararı, ve satır o yüzden yazıldığı
gibi kalıyor *(kullanıcı, 10 Ekim — "abi zaten agentic akış bu, agentın kendisi karar vermesi gerekiyor
ya buna?")*.

## Ne zaman biter

- Modele giden system prompt'un Planning bölümünde bu satır, *"Do not stop to ask for a yes"*
  satırının hemen altında, sözü sözüne var; başka metin değişmedi.
- Yeni test önce kırmızı, sonra yeşil; dört suite yeşil.
