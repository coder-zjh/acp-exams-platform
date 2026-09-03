import assert from "node:assert/strict";
import test from "node:test";

import { optionState } from "./app-logic.js";

test("a correct option in a multi-select answer is green instead of red", () => {
  assert.equal(optionState("A", ["A", "C"], "AC", true, true), "correct");
});

test("a missed correct option in a submitted multi-select answer is marked missed", () => {
  assert.equal(optionState("B", ["A"], "AB", true, true), "missed");
});

test("an unselected correct option in a single-select answer stays green", () => {
  assert.equal(optionState("B", ["A"], "B", true), "correct");
});
