// Which models a chat can be answered by, and what each one costs. Three since Madde 146: Madde 82
// tore the picking machinery out because a single model left it idle, and two more ended that
// premise rather than overturned it.
//
// The list lives here rather than in the backend, exactly as the skills' does: what the server
// knows is what an id MEANS -- its address and the key it spends (config.py) -- never which one is
// selected. The selection is the session's and rides on each message.
//
// The ids are shared with config.py's table and nothing enforces that: Python and JS cannot read
// each other, so this sentence is the whole of what keeps the two in step. The detail is the price,
// because choosing between these is a price question -- the madde exists because of the bill, and a
// menu that hid the number would answer a question nobody asked. Off-peak rates; the sources are in
// the roadmap's Madde 146.
export const MODELS = [
  {
    id: "grok-build-0.1",
    name: "Grok Build",
    detail: "$1 / $2 per 1M",
  },
  {
    id: "deepseek-v4-flash",
    name: "DeepSeek Flash",
    detail: "$0.22 / $0.66 per 1M",
  },
  {
    id: "deepseek-v4-pro",
    name: "DeepSeek Pro",
    detail: "$0.66 / $1.98 per 1M",
  },
];

// What answers when nothing has been picked, and what the app has always answered with.
export const DEFAULT_MODEL = "grok-build-0.1";

// Where this parts from skillName: no skill is an ordinary state and reads as "Skills", but every
// answer is given by some model -- so nothing means the default rather than a gap. A record can
// still name one of the five dropped in Madde 72, and then the button says its id rather than going
// blank.
export function modelName(id) {
  const wanted = id || DEFAULT_MODEL;
  return MODELS.find((model) => model.id === wanted)?.name ?? wanted;
}
