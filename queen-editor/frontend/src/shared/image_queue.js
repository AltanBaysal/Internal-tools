// One at a time, in the order the tiles were built. Every tile is its own request through the same
// tunnel and the status poll shares it, so a ceiling is what keeps the API's request from waiting
// behind a project's worth of photos. One rather than more: on a full gallery the difference is
// seconds, and a pipe with one thing in it is the pipe nobody has to reason about.
const GALLERY_SLOTS = 1;

export function createQueue(limit) {
  const waiting = [];
  let flying = 0;

  function pour() {
    while (flying < limit && waiting.length) {
      const ticket = waiting.shift();
      // Skip rather than stop: a tile scrolled past while in line must not hold up the ones behind
      // it, which is the whole reason the queue is worth having.
      if (ticket.spent) continue;
      flying += 1;
      ticket.holding = true;
      ticket.grant();
    }
  }

  return {
    ask(grant) {
      const ticket = {
        grant,
        holding: false,
        spent: false,
        done() {
          // One ticket frees one slot however often it is released. A tile that loads and is then
          // taken off the screen releases twice, and the second must not invent a slot.
          if (ticket.spent) return;
          ticket.spent = true;
          if (!ticket.holding) return;
          flying -= 1;
          pour();
        },
      };
      waiting.push(ticket);
      pour();
      return ticket;
    },
  };
}

export const imageQueue = createQueue(GALLERY_SLOTS);
