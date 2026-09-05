import assert from "node:assert/strict";
import test from "node:test";

import { completionStats, isCurrentLoad, nextQuestionIndex, optionIndexForShortcut, optionState, questionSetCount, shouldKeepSubmittedQuestion } from "./app-logic.js";

test("a correct option in a multi-select answer is green instead of red", () => {
  assert.equal(optionState("A", ["A", "C"], "AC", true, true), "correct");
});

test("a missed correct option in a submitted multi-select answer is marked missed", () => {
  assert.equal(optionState("B", ["A"], "AB", true, true), "missed");
});

test("an unselected correct option in a single-select answer stays green", () => {
  assert.equal(optionState("B", ["A"], "B", true), "correct");
});

test("single-select and multi-select sets both use their catalog question totals", () => {
  assert.equal(questionSetCount({ section: "single", question_count: 896 }), 896);
  assert.equal(questionSetCount({ section: "multi", question_count: 370 }), 370);
});

test("completion stats count chopped questions in completion and accuracy", () => {
  assert.deepEqual(
    completionStats({ done: [1, 1, 2], excluded: [2, 3], results: { "1": true, "2": false } }),
    { done: 2, completed: 3, correct: 2 },
  );
});

test("stale question loads are rejected when a newer load exists", () => {
  assert.equal(isCurrentLoad(2, 2), true);
  assert.equal(isCurrentLoad(1, 2), false);
});

test("next question navigation follows the active filtered list", () => {
  assert.equal(nextQuestionIndex([2, 5, 9], 5), 9);
  assert.equal(nextQuestionIndex([2, 5, 9], 9), null);
});

test("number shortcuts map one through nine and zero to ten options", () => {
  assert.equal(optionIndexForShortcut("1"), 0);
  assert.equal(optionIndexForShortcut("9"), 8);
  assert.equal(optionIndexForShortcut("0"), 9);
  assert.equal(optionIndexForShortcut("a"), null);
});

test("the just-submitted question remains visible in the unfinished filter until navigation", () => {
  assert.equal(shouldKeepSubmittedQuestion(7, 7, 1, 1, { unfinished: true, wrong: false, favorite: false, chopped: false, all: false }, [7]), true);
});

test("a chopped submitted question is excluded from the unfinished filter", () => {
  assert.equal(shouldKeepSubmittedQuestion(7, 7, 1, 1, { unfinished: true, wrong: false, favorite: false, chopped: false, all: false }, [7], [7]), false);
});
