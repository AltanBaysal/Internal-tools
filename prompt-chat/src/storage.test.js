import { describe, it, expect } from "vitest";
import { nextId, createChat, deleteChat, replaceMessages, setDraft, titleOf } from "./storage.js";

const chat = (id, messages = [], draft = "") => ({ id, messages, draft });

describe("nextId", () => {
  it("boş listede 1 verir", () => {
    expect(nextId([])).toBe(1);
  });

  it("en büyüğün bir fazlasını verir", () => {
    expect(nextId([chat(1), chat(4), chat(2)])).toBe(5);
  });
});

describe("createChat", () => {
  it("sonuna boş sohbet ekler ve id'sini söyler", () => {
    const { chats, id } = createChat([chat(1)]);
    expect(id).toBe(2);
    expect(chats).toHaveLength(2);
    expect(chats[1]).toEqual({ id: 2, messages: [], draft: "" });
  });

  it("verilen listeyi değiştirmez", () => {
    const before = [chat(1)];
    createChat(before);
    expect(before).toHaveLength(1);
  });
});

describe("deleteChat", () => {
  it("yalnız o sohbeti çıkarır", () => {
    const after = deleteChat([chat(1), chat(2), chat(3)], 2);
    expect(after.map((c) => c.id)).toEqual([1, 3]);
  });

  it("verilen listeyi değiştirmez", () => {
    const before = [chat(1), chat(2)];
    deleteChat(before, 1);
    expect(before).toHaveLength(2);
  });
});

describe("replaceMessages", () => {
  it("yalnız hedef sohbetin mesajlarını değiştirir", () => {
    const after = replaceMessages([chat(1), chat(2)], 2, [{ role: "user", content: "selam" }]);
    expect(after[0].messages).toEqual([]);
    expect(after[1].messages).toEqual([{ role: "user", content: "selam" }]);
  });

  it("taslağa dokunmaz", () => {
    const after = replaceMessages([chat(1, [], "yarım")], 1, [{ role: "user", content: "a" }]);
    expect(after[0].draft).toBe("yarım");
  });
});

describe("setDraft", () => {
  it("yalnız hedef sohbetin taslağını değiştirir", () => {
    const after = setDraft([chat(1, [], "a"), chat(2, [], "b")], 2, "yeni");
    expect(after[0].draft).toBe("a");
    expect(after[1].draft).toBe("yeni");
  });

  it("mesajlara dokunmaz", () => {
    const msgs = [{ role: "user", content: "selam" }];
    const after = setDraft([chat(1, msgs)], 1, "yarım");
    expect(after[0].messages).toBe(msgs);
  });
});

describe("titleOf", () => {
  it("hiç mesaj yoksa Yeni sohbet der", () => {
    expect(titleOf([])).toBe("Yeni sohbet");
  });

  it("yalnız cevap varsa da Yeni sohbet der", () => {
    expect(titleOf([{ role: "assistant", content: "merhaba" }])).toBe("Yeni sohbet");
  });

  it("kısa mesajı olduğu gibi verir", () => {
    expect(titleOf([{ role: "user", content: "kanlı dövüş" }])).toBe("kanlı dövüş");
  });

  it("uzun mesajı 40 karakterde kırpar ve … ekler", () => {
    const uzun = "a".repeat(60);
    const title = titleOf([{ role: "user", content: uzun }]);
    expect(title).toBe("a".repeat(40) + "…");
  });

  it("satır sonlarını boşluğa çevirir", () => {
    expect(titleOf([{ role: "user", content: "birinci\nikinci" }])).toBe("birinci ikinci");
  });

  it("ilk kullanıcı mesajını alır, sonrakini değil", () => {
    const title = titleOf([
      { role: "user", content: "ilk" },
      { role: "assistant", content: "cevap" },
      { role: "user", content: "ikinci" },
    ]);
    expect(title).toBe("ilk");
  });
});
