import { describe, it, expect } from "vitest";
import { nextId, createChat, deleteChat, replaceMessages, setDraft, titleOf } from "./storage.js";

const chat = (id, messages = [], draft = "") => ({ id, messages, draft });

describe("nextId", () => {
  it("gives 1 for an empty list", () => {
    expect(nextId([])).toBe(1);
  });

  it("gives one more than the largest", () => {
    expect(nextId([chat(1), chat(4), chat(2)])).toBe(5);
  });
});

describe("createChat", () => {
  it("appends an empty chat and reports its id", () => {
    const { chats, id } = createChat([chat(1)]);
    expect(id).toBe(2);
    expect(chats).toHaveLength(2);
    expect(chats[1]).toEqual({ id: 2, messages: [], draft: "" });
  });

  it("does not mutate the list it was given", () => {
    const before = [chat(1)];
    createChat(before);
    expect(before).toHaveLength(1);
  });
});

describe("deleteChat", () => {
  it("removes only that chat", () => {
    const after = deleteChat([chat(1), chat(2), chat(3)], 2);
    expect(after.map((c) => c.id)).toEqual([1, 3]);
  });

  it("does not mutate the list it was given", () => {
    const before = [chat(1), chat(2)];
    deleteChat(before, 1);
    expect(before).toHaveLength(2);
  });
});

describe("replaceMessages", () => {
  it("changes only the target chat's messages", () => {
    const after = replaceMessages([chat(1), chat(2)], 2, [{ role: "user", content: "selam" }]);
    expect(after[0].messages).toEqual([]);
    expect(after[1].messages).toEqual([{ role: "user", content: "selam" }]);
  });

  it("leaves the draft alone", () => {
    const after = replaceMessages([chat(1, [], "yarım")], 1, [{ role: "user", content: "a" }]);
    expect(after[0].draft).toBe("yarım");
  });
});

describe("setDraft", () => {
  it("changes only the target chat's draft", () => {
    const after = setDraft([chat(1, [], "a"), chat(2, [], "b")], 2, "yeni");
    expect(after[0].draft).toBe("a");
    expect(after[1].draft).toBe("yeni");
  });

  it("leaves the messages alone", () => {
    const msgs = [{ role: "user", content: "selam" }];
    const after = setDraft([chat(1, msgs)], 1, "yarım");
    expect(after[0].messages).toBe(msgs);
  });
});

describe("titleOf", () => {
  it("says Yeni sohbet when there are no messages", () => {
    expect(titleOf([])).toBe("Yeni sohbet");
  });

  it("says Yeni sohbet when only a reply exists", () => {
    expect(titleOf([{ role: "assistant", content: "merhaba" }])).toBe("Yeni sohbet");
  });

  it("returns a short message unchanged", () => {
    expect(titleOf([{ role: "user", content: "kanlı dövüş" }])).toBe("kanlı dövüş");
  });

  it("cuts a long message at 40 characters and appends …", () => {
    const uzun = "a".repeat(60);
    const title = titleOf([{ role: "user", content: uzun }]);
    expect(title).toBe("a".repeat(40) + "…");
  });

  it("turns line breaks into spaces", () => {
    expect(titleOf([{ role: "user", content: "birinci\nikinci" }])).toBe("birinci ikinci");
  });

  it("takes the first user message, not a later one", () => {
    const title = titleOf([
      { role: "user", content: "ilk" },
      { role: "assistant", content: "cevap" },
      { role: "user", content: "ikinci" },
    ]);
    expect(title).toBe("ilk");
  });
});
