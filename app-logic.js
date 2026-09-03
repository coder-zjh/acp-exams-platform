export function optionState(key, selected, correctAnswer, submitted) {
  if (!submitted) return selected.includes(key) ? "selected" : "";
  if (correctAnswer.includes(key)) return "correct";
  return selected.includes(key) ? "wrong" : "";
}
