// Four rows since Madde 492: a start and an edit for each image model, SDXL and Krea (the user, 22
// October). Improve went in the same item. Not zero rows even at one: having no skill selected is
// an ordinary state.
//
// The start comes first in each pair because that is the answer to "which do I want": somebody with
// nothing yet takes the start, somebody who already has prompts takes the edit. Since Madde 186 the
// two are the halves of the work rather than two roads into it -- the start runs all the way to the
// built file. The SDXL two keep the ids they had, so an older chat and a remembered pick still find
// them; only the names say which model they are for now.
export const SKILLS = [
  {
    id: "start-a-scenario",
    name: "SDXL start scenario",
    detail: "Answer a few questions and get the characters, the places and the prompts.",
  },
  {
    id: "edit-prompts",
    name: "SDXL edit",
    detail: "Fix what is wrong in prompts you already have, and build them again.",
  },
  {
    id: "krea-start-scenario",
    name: "Krea start scenario",
    detail: "Answer a few questions and get the scenes and the Krea prompts.",
  },
  {
    id: "krea-edit",
    name: "Krea edit",
    detail: "Fix what is wrong in Krea prompts you already have, and build them again.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap. A
// record can still name a deleted one -- Improve, or one of Madde 94's five: the button says its id
// rather than going blank.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
