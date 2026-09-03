import assert from "node:assert/strict";
import test from "node:test";

import { optionState } from "./app-logic.js";

test("a correct option in a multi-select answer is green instead of red", () => {
  assert.equal(optionState("A", ["A", "C"], "AC", true), "correct");
});
