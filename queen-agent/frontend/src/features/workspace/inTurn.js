// One line of tasks: each starts once the one before it has settled, and its caller gets what it
// returned or threw. The line itself only waits -- a task that fails never stops the next one.
export function inTurn() {
  let last = Promise.resolve();
  return (task) => {
    const run = last.then(task);
    last = run.catch(() => {});
    return run;
  };
}
