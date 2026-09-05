export function optionState(key, selected, correctAnswer, submitted, multi = false) {
  if (!submitted) return selected.includes(key) ? "selected" : "";
  if (correctAnswer.includes(key)) return selected.includes(key) || !multi ? "correct" : "missed";
  return selected.includes(key) ? "wrong" : "";
}

export function questionSetCount(set) {
  return set.question_count;
}

export function completionStats(setProgress) {
  const done = new Set(setProgress.done);
  const excluded = new Set(setProgress.excluded);
  const completed = new Set([...done, ...excluded]).size;
  const correct = [...done].filter((number) => setProgress.results[String(number)] === true).length
    + [...excluded].filter((number) => !done.has(number)).length;
  return { done: done.size, completed, correct };
}

export function isCurrentLoad(loadId, latestLoadId) {
  return loadId === latestLoadId;
}

export function nextQuestionIndex(numbers, currentNumber) {
  const position = numbers.indexOf(currentNumber);
  return position >= 0 && position < numbers.length - 1 ? numbers[position + 1] : null;
}

export function optionIndexForShortcut(key) {
  if (/^[1-9]$/.test(key)) return Number(key) - 1;
  return key === "0" ? 9 : null;
}

export function shouldKeepSubmittedQuestion(number, currentNumber, setIndex, currentSetIndex, filters, done, excluded = []) {
  return setIndex === currentSetIndex && number === currentNumber && filters.unfinished && !filters.wrong && !filters.favorite && !filters.chopped && !filters.all && done.includes(number) && !excluded.includes(number);
}
