export function optionState(key, selected, correctAnswer, submitted, multi = false) {
  if (!submitted) return selected.includes(key) ? "selected" : "";
  if (correctAnswer.includes(key)) return selected.includes(key) || !multi ? "correct" : "missed";
  return selected.includes(key) ? "wrong" : "";
}

export function shouldKeepSubmittedQuestion(number, currentNumber, setIndex, currentSetIndex, filters, done) {
  return setIndex === currentSetIndex && number === currentNumber && filters.unfinished && !filters.wrong && !filters.favorite && !filters.chopped && !filters.all && done.includes(number);
}
