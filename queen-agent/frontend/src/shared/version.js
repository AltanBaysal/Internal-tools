/** Which run of QueenAgent this is (Madde 209).
 *
 * Written by hand, because it is a decision rather than a fact anything else already holds: a run
 * opens, the number moves, and nothing in a build or a commit knows that happened. The date the
 * bundle was built, the version in package.json and a git tag all answer other questions on other
 * rhythms, and none of them says V8.
 *
 * Its own module rather than a line inside the sidebar: the sidebar draws it, it does not own it,
 * and whoever opens the next run should find this without reading a component.
 */
export const VERSION = "V8";
