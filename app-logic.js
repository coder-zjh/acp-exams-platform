export function optionState(key, selected, correctAnswer, submitted, multi = false) {
  if (!submitted) return selected.includes(key) ? "selected" : "";
  if (correctAnswer.includes(key)) return selected.includes(key) || !multi ? "correct" : "missed";
  return selected.includes(key) ? "wrong" : "";
}
