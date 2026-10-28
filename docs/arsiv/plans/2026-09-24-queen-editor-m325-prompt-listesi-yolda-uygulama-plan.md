# Madde 325 — Referanstan'ın prompt listesi sunucuya ulaşıyor, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Yan panelin `onQueue` bağlantısı panelin verdiği her argümanı `onQueueLayer`'a geçiriyor.

**Yaklaşım:** Tek satır: argümanlar adlandırılmadan, olduğu gibi geçiyor.

**Spec:** [m325 uygulama turu](../specs/2026-09-24-queen-editor-m325-prompt-listesi-yolda-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**; yalnız bugün doğru olanı söyler.
- Kaynakla `dist/` aynı commit'te.

---

## Görev 1: Bağlantı

**Dosya:** Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx:177-185`

- [ ] **Adım 1: Bağlantıyı değiştir.**

```jsx
        {/* One panel, two layers: the design asks for the same screen twice, so only the words and
            the scope rule differ (see LayerPanel). The panel's call goes through whole, with the
            layer in front: a list of named arguments here would drop whatever the panel adds -- the
            pool's prompts ride fourth (madde 325). */}
        {(open === "video" || open === "audio") && (
          <LayerPanel layer={open} frames={frames} selected={selected}
                      job={job} busyElsewhere={busyElsewhere} error={error}
                      producer={(producers?.producers || []).find((p) => p.id === open)}
                      onQueue={(...asked) => onQueueLayer(open, ...asked)}
                      onInstall={producers?.install} />
        )}
```

## Görev 2: Koşu, dist ve yeşil commit

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Dist** — `npm run build --prefix queen-editor/frontend`.
- [ ] **Adım 3: Yeşil commit** — `SidePanel.jsx`, `dist/`, spec ve bu plan: `feat(m325): …`.
