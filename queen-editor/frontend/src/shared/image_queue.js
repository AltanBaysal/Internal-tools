// Skeleton only -- the rules land in the implementation cycle. Signatures exist so the tests next
// door can run and fail on what they assert rather than on a missing import.
export function createQueue(limit) {
  return { ask: () => ({ done: () => {} }) };
}

export const imageQueue = createQueue(2);
