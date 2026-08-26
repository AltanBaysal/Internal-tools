// The one model this app offers. Grok Build since Madde 72: it costs less than what came before
// ($1/$2 per 1M against grok-4.3's $1.25/$2.50) and the run stands on one model rather than on a
// choice nobody was making. Its window is 256k -- a quarter of grok-4.3's, named and accepted when
// the row was chosen. Which model a chat that picked nothing answers with is still the server's
// setting and arrives from GET /api/model; the name and the price are text, and text lives here.
//
// The row says what it costs rather than what it is for. The design wrote a sentence under each
// name, but those names -- Grok 4 Fast, Heavy, Code -- do not exist, and the documentation
// describes only one of the real models.
//
// Price is per million tokens, input / output, for a prompt under 200k. Above that it doubles.
export const MODELS = [{ id: "grok-build-0.1", name: "Grok Build", detail: "$1 / $2 per 1M · 256k" }];

// A chat may carry an id this list does not know -- every chat opened before Madde 72 does, and
// XAI_MODEL can be set to anything at all. It is shown as it is: a button saying nothing would be
// worse, and a display name for a model the menu no longer offers would imply it can still be
// picked.
export function modelName(id) {
  if (!id) return "Model";
  return MODELS.find((model) => model.id === id)?.name ?? id;
}
