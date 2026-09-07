// Which models a chat can be answered by, and what each one costs. Two since Madde 177: there were
// three, and Grok left the menu rather than the app -- it writes the frames' actions now
// (config.PROMPT_MODEL), which is a role rather than something to pick.
//
// The list lives here rather than in the backend, exactly as the skills' does: what the server
// knows is what an id MEANS -- its address and the key it spends (config.py) -- never which one is
// selected. The selection is the session's and rides on each message.
//
// The names are this file's own, and only this file's. An id is what the provider is told the model
// is called -- client.py sends it as the model field -- so renaming one in config.py would break
// the call, and Queen Flash and Queen Pro are what a person sees instead. Nothing enforces that the
// ids here match config.py's table: Python and JS cannot read each other, and this sentence is the
// whole of what keeps the two in step.
//
// The detail is the price, because choosing between these is a price question -- Madde 146 exists
// because of the bill, and a menu that hid the number would answer a question nobody asked.
// Off-peak rates; the sources are in the roadmap's Madde 146.
export const MODELS = [
  {
    id: "deepseek-v4-flash",
    name: "Queen Flash",
    detail: "$0.22 / $0.66 per 1M",
  },
  {
    id: "deepseek-v4-pro",
    name: "Queen Pro",
    detail: "$0.66 / $1.98 per 1M",
  },
];

// What answers when nothing has been picked. The same id config.py defaults to, and it has to be:
// one answers what an empty button says and the other where a message with no model goes, and the
// two parting would show one name on the screen while calling another on the wire.
export const DEFAULT_MODEL = "deepseek-v4-flash";

// Where this parts from skillName: no skill is an ordinary state and reads as "Skills", but every
// answer is given by some model -- so nothing means the default rather than a gap. A record can
// still name one of the five dropped in Madde 72, or the one Madde 177 took out of the menu, and
// then the button says its id rather than going blank: that message really was answered by it, and
// a name we made up here would misread the record.
export function modelName(id) {
  const wanted = id || DEFAULT_MODEL;
  return MODELS.find((model) => model.id === wanted)?.name ?? wanted;
}
