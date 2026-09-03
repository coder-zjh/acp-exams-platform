import assert from "node:assert/strict";
import test from "node:test";

import { optionState, shouldKeepSubmittedQuestion } from "./app-logic.js";

test("a correct option in a multi-select answer is green instead of red", () => {
  assert.equal(optionState("A", ["A", "C"], "AC", true, true), "correct");
});

test("a missed correct option in a submitted multi-select answer is marked missed", () => {
  assert.equal(optionState("B", ["A"], "AB", true, true), "missed");
});

test("an unselected correct option in a single-select answer stays green", () => {
  assert.equal(optionState("B", ["A"], "B", true), "correct");
});

test("the just-submitted question remains visible in the unfinished filter until navigation", () => {
  assert.equal(shouldKeepSubmittedQuestion(7, 7, 1, 1, { unfinished: true, wrong: false, favorite: false, chopped: false, all: false }, [7]), true);
});
