const levels = ["easy", "medium", "hard"];

const quizQuestions = [
  { topic: "General Knowledge", level: "easy", question: "What is the capital of India?", options: ["Delhi", "Mumbai", "Chennai", "Kolkata"], answer: "Delhi" },
  { topic: "General Knowledge", level: "easy", question: "How many days are there in a week?", options: ["5", "6", "7", "8"], answer: "7" },
  { topic: "Science", level: "easy", question: "Which planet do we live on?", options: ["Mars", "Earth", "Venus", "Jupiter"], answer: "Earth" },
  { topic: "Science", level: "medium", question: "What gas do plants use to make food?", options: ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], answer: "Carbon Dioxide" },
  { topic: "Math", level: "easy", question: "What is 8 + 5?", options: ["11", "12", "13", "14"], answer: "13" },
  { topic: "Math", level: "medium", question: "What is 9 x 6?", options: ["42", "48", "54", "63"], answer: "54" },
  { topic: "English", level: "easy", question: "Which word is a noun?", options: ["Run", "Blue", "School", "Quickly"], answer: "School" },
  { topic: "English", level: "medium", question: "Choose the correct spelling.", options: ["Beutiful", "Beautiful", "Beautifull", "Beautifil"], answer: "Beautiful" },
  { topic: "General Knowledge", level: "medium", question: "Which animal is called the king of the jungle?", options: ["Tiger", "Elephant", "Lion", "Leopard"], answer: "Lion" },
  { topic: "Science", level: "hard", question: "Which part of the plant absorbs water from the soil?", options: ["Flower", "Leaf", "Stem", "Root"], answer: "Root" },
  { topic: "Math", level: "hard", question: "What is 144 divided by 12?", options: ["10", "11", "12", "13"], answer: "12" },
  { topic: "English", level: "hard", question: "Which word is the opposite of ancient?", options: ["Old", "Tiny", "Modern", "Heavy"], answer: "Modern" }
];

const riddles = [
  { level: "easy", question: "I have hands but cannot clap. What am I?", answer: "clock", hint: "You look at me to know the time." },
  { level: "easy", question: "What has a face and two hands but no arms or legs?", answer: "clock", hint: "It hangs on a wall." },
  { level: "medium", question: "What gets wetter the more it dries?", answer: "towel", hint: "You use it after a bath." },
  { level: "medium", question: "I am full of keys but I cannot open any door. What am I?", answer: "piano", hint: "It makes music." },
  { level: "hard", question: "The more you take, the more you leave behind. What are they?", answer: "footsteps", hint: "You make them when you walk." },
  { level: "hard", question: "What has one eye but cannot see?", answer: "needle", hint: "It is used with thread." }
];

const memoryWords = {
  easy: ["apple", "sun", "book", "tree", "ball", "fish", "milk", "star", "chair", "bird"],
  medium: ["planet", "garden", "window", "castle", "orange", "bridge", "pencil", "rabbit", "basket", "rocket"],
  hard: ["adventure", "volcano", "triangle", "notebook", "elephant", "dinosaur", "treasure", "library", "calendar", "microscope"]
};

const wordChallenges = [
  { type: "scramble", level: "easy", prompt: "Unscramble this word", clue: "LPAEP", answer: "apple" },
  { type: "scramble", level: "medium", prompt: "Unscramble this word", clue: "RTAINE", answer: "retain" },
  { type: "scramble", level: "hard", prompt: "Unscramble this word", clue: "CSENICE", answer: "science" },
  { type: "opposite", level: "easy", prompt: "What is the opposite of happy?", clue: "Type one word", answer: "sad" },
  { type: "opposite", level: "medium", prompt: "What is the opposite of noisy?", clue: "Type one word", answer: "quiet" },
  { type: "opposite", level: "hard", prompt: "What is the opposite of ancient?", clue: "Type one word", answer: "modern" },
  { type: "blank", level: "easy", prompt: "Fill in the blank: C _ T", clue: "A pet animal", answer: "cat" },
  { type: "blank", level: "medium", prompt: "Fill in the blank: PLA _ ET", clue: "A world in space", answer: "planet" },
  { type: "blank", level: "hard", prompt: "Fill in the blank: MI _ ROSCOPE", clue: "Used to see tiny things", answer: "microscope" },
  { type: "vocab", level: "easy", prompt: "Which word means very big?", clue: "Use one word", answer: "huge" },
  { type: "vocab", level: "medium", prompt: "Which word means begin?", clue: "Use one word", answer: "start" },
  { type: "vocab", level: "hard", prompt: "Which word means brave?", clue: "Use one word", answer: "courageous" }
];

const dailyPool = [
  { type: "quiz", prompt: "What is 10 + 4?", options: ["12", "13", "14", "15"], answer: "14" },
  { type: "quiz", prompt: "Which animal says meow?", options: ["Dog", "Cat", "Cow", "Duck"], answer: "Cat" },
  { type: "input", prompt: "Riddle: What has four legs and a back, but cannot walk?", answer: "chair", hint: "You sit on it." },
  { type: "input", prompt: "Unscramble: NUSIHNSE", answer: "sunshine", hint: "A bright day word." },
  { type: "input", prompt: "Fill in the blank: B _ _ K", answer: "book", hint: "You read it." },
  { type: "quiz", prompt: "Which planet is closest to the Sun?", options: ["Mars", "Mercury", "Earth", "Saturn"], answer: "Mercury" },
  { type: "input", prompt: "What is the opposite of cold?", answer: "hot", hint: "Think of summer." },
  { type: "quiz", prompt: "What is 7 x 3?", options: ["18", "20", "21", "24"], answer: "21" }
];

const storageKey = "smart-kids-learning-scores";

const state = {
  scores: { totalPoints: 0, bestQuiz: 0, bestMath: 0, dailyStars: 0 },
  quiz: { questions: [], index: 0, score: 0, locked: false },
  riddle: { current: null, revealed: false },
  memory: { words: [], countdown: null, score: 0, phase: "idle" },
  math: { running: false, timer: null, timeLeft: 30, score: 0, current: null },
  word: { current: null },
  daily: { key: "", items: [], index: 0, score: 0, done: false }
};

function $(id) {
  return document.getElementById(id);
}

function shuffle(items) {
  const clone = [...items];
  for (let index = clone.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [clone[index], clone[swapIndex]] = [clone[swapIndex], clone[index]];
  }
  return clone;
}

function pickRandom(items, count) {
  return shuffle(items).slice(0, count);
}

function normalize(text) {
  return text.trim().toLowerCase();
}

function setProgress(elementId, current, total) {
  const percent = total === 0 ? 0 : (current / total) * 100;
  $(elementId).style.width = `${percent}%`;
}

function loadScores() {
  const stored = localStorage.getItem(storageKey);
  if (!stored) {
    return;
  }
  try {
    const parsed = JSON.parse(stored);
    state.scores = { ...state.scores, ...parsed };
  } catch (error) {
    localStorage.removeItem(storageKey);
  }
}

function saveScores() {
  localStorage.setItem(storageKey, JSON.stringify(state.scores));
}

function addPoints(points) {
  state.scores.totalPoints += points;
  saveScores();
  renderScoreboard();
}

function renderScoreboard() {
  $("total-points").textContent = String(state.scores.totalPoints);
  $("best-quiz").textContent = String(state.scores.bestQuiz);
  $("best-math").textContent = String(state.scores.bestMath);
  $("daily-score").textContent = String(state.scores.dailyStars);
}

function fillLevelSelects() {
  ["quiz-level", "riddle-level", "memory-level", "math-level", "word-level"].forEach((id) => {
    $(id).innerHTML = levels
      .map((level) => `<option value="${level}">${level[0].toUpperCase()}${level.slice(1)}</option>`)
      .join("");
  });
}

function setActiveView(viewId) {
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === viewId);
  });
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.classList.toggle("active", button.dataset.target === viewId);
  });
}

function playTone(type) {
  const AudioContextRef = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextRef) {
    return;
  }
  const audioContext = new AudioContextRef();
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = "sine";
  oscillator.frequency.value = type === "good" ? 620 : 220;
  gain.gain.value = 0.06;
  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.14);
}

function getQuizSet() {
  const level = $("quiz-level").value;
  const topic = $("quiz-topic").value;
  const filtered = quizQuestions.filter((item) => item.level === level && (topic === "all" || item.topic === topic));
  const fallback = quizQuestions.filter((item) => topic === "all" || item.topic === topic);
  return pickRandom(filtered.length >= 5 ? filtered : fallback, 5);
}

function startQuiz() {
  state.quiz = { questions: getQuizSet(), index: 0, score: 0, locked: false };
  $("quiz-score-label").textContent = "Score: 0";
  renderQuizQuestion();
}

function renderQuizQuestion() {
  const card = $("quiz-card");
  const current = state.quiz.questions[state.quiz.index];

  if (!current) {
    state.scores.bestQuiz = Math.max(state.scores.bestQuiz, state.quiz.score);
    addPoints(state.quiz.score * 2);
    saveScores();
    renderScoreboard();
    $("quiz-step-label").textContent = "Finished";
    setProgress("quiz-progress-bar", state.quiz.questions.length, state.quiz.questions.length);
    card.innerHTML = `
      <h3>Quiz Complete</h3>
      <p class="big-text">You scored ${state.quiz.score} out of ${state.quiz.questions.length}.</p>
      <button class="action-btn" id="quiz-restart">Play Again</button>
    `;
    $("quiz-restart").addEventListener("click", startQuiz);
    return;
  }

  $("quiz-step-label").textContent = `Question ${state.quiz.index + 1} / ${state.quiz.questions.length}`;
  $("quiz-score-label").textContent = `Score: ${state.quiz.score}`;
  setProgress("quiz-progress-bar", state.quiz.index, state.quiz.questions.length);

  card.innerHTML = `
    <p class="pill">${current.topic} | ${current.level}</p>
    <p class="question-text">${current.question}</p>
    <div class="option-grid">
      ${current.options.map((option) => `<button class="option-btn" data-value="${option}">${option}</button>`).join("")}
    </div>
    <div id="quiz-result"></div>
  `;

  card.querySelectorAll(".option-btn").forEach((button) => {
    button.addEventListener("click", () => handleQuizAnswer(button, current.answer));
  });
}

function handleQuizAnswer(button, answer) {
  if (state.quiz.locked) {
    return;
  }
  state.quiz.locked = true;

  const value = button.dataset.value;
  const correct = value === answer;
  const result = $("quiz-result");
  const buttons = Array.from(document.querySelectorAll("#quiz-card .option-btn"));

  buttons.forEach((item) => {
    if (item.dataset.value === answer) {
      item.classList.add("correct");
    } else if (item === button && !correct) {
      item.classList.add("wrong");
    }
    item.disabled = true;
  });

  if (correct) {
    state.quiz.score += 1;
    result.innerHTML = `<div class="result good">Correct! Great job.</div>`;
    playTone("good");
  } else {
    result.innerHTML = `<div class="result bad">Wrong. The correct answer is ${answer}.</div>`;
    playTone("bad");
  }

  $("quiz-score-label").textContent = `Score: ${state.quiz.score}`;

  setTimeout(() => {
    state.quiz.index += 1;
    state.quiz.locked = false;
    renderQuizQuestion();
  }, 900);
}

function renderRiddle() {
  const level = $("riddle-level").value;
  const items = riddles.filter((item) => item.level === level);
  state.riddle.current = items[Math.floor(Math.random() * items.length)];
  state.riddle.revealed = false;

  $("riddle-card").innerHTML = `
    <p class="pill">${level}</p>
    <p class="question-text">${state.riddle.current.question}</p>
    <div class="input-row">
      <input id="riddle-answer" type="text" placeholder="Type your answer" />
      <button id="riddle-submit" class="action-btn">Check</button>
      <button id="riddle-hint" class="ghost-btn">Show Hint</button>
    </div>
    <div id="riddle-feedback"></div>
  `;

  $("riddle-submit").addEventListener("click", submitRiddle);
  $("riddle-hint").addEventListener("click", showRiddleHint);
}

function showRiddleHint() {
  const feedback = $("riddle-feedback");
  feedback.innerHTML = `<div class="hint-box">Hint: ${state.riddle.current.hint}</div>`;
}

function submitRiddle() {
  const guess = normalize($("riddle-answer").value);
  const correct = normalize(state.riddle.current.answer);
  const feedback = $("riddle-feedback");
  const matched = guess === correct;

  if (matched) {
    feedback.innerHTML = `<div class="result good">Correct! The answer is ${state.riddle.current.answer}.</div>`;
    addPoints(3);
    playTone("good");
  } else {
    feedback.innerHTML = `<div class="result bad">Nice try. The correct answer is ${state.riddle.current.answer}.</div>`;
    playTone("bad");
  }
}

function startMemoryGame() {
  if (state.memory.countdown) {
    clearInterval(state.memory.countdown);
  }

  const level = $("memory-level").value;
  state.memory.words = pickRandom(memoryWords[level], 5);
  state.memory.phase = "show";
  state.memory.score = 0;
  let timeLeft = 5;

  $("memory-score-label").textContent = `Score: ${state.memory.score}`;
  $("memory-timer-label").textContent = `Memorize: ${timeLeft}s`;
  $("memory-card").innerHTML = `
    <p class="pill">${level}</p>
    <p class="question-text">Remember these five words:</p>
    <div class="memory-words">${state.memory.words.map((word) => `<span>${word}</span>`).join("")}</div>
  `;

  state.memory.countdown = setInterval(() => {
    timeLeft -= 1;
    $("memory-timer-label").textContent = `Memorize: ${timeLeft}s`;
    if (timeLeft <= 0) {
      clearInterval(state.memory.countdown);
      state.memory.countdown = null;
      renderMemoryRecall();
    }
  }, 1000);
}

function renderMemoryRecall() {
  state.memory.phase = "recall";
  $("memory-timer-label").textContent = "Type the words you remember";
  $("memory-card").innerHTML = `
    <p class="question-text">Enter the five words, separated by commas.</p>
    <div class="input-row">
      <input id="memory-answer" type="text" placeholder="apple, tree, ball..." />
      <button id="memory-submit" class="action-btn">Check Memory</button>
    </div>
    <p class="mini-note">Words can be in any order.</p>
    <div id="memory-feedback"></div>
  `;
  $("memory-submit").addEventListener("click", submitMemoryGame);
}

function submitMemoryGame() {
  const guessedWords = $("memory-answer").value
    .split(",")
    .map((word) => normalize(word))
    .filter(Boolean);
  const actualWords = state.memory.words.map((word) => normalize(word));
  const uniqueMatches = [...new Set(guessedWords)].filter((word) => actualWords.includes(word));
  const roundScore = uniqueMatches.length;
  state.memory.score = roundScore;
  $("memory-score-label").textContent = `Score: ${roundScore}`;
  addPoints(roundScore * 2);

  $("memory-feedback").innerHTML = `
    <div class="answer-box">You got ${roundScore} / 5. Correct words: ${state.memory.words.join(", ")}.</div>
  `;
  playTone(roundScore >= 3 ? "good" : "bad");
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function buildMathQuestion(level) {
  const ops = ["+", "-", "x"];
  const op = ops[randomInt(0, ops.length - 1)];
  const ranges = {
    easy: [1, 10],
    medium: [4, 20],
    hard: [6, 30]
  };
  const [min, max] = ranges[level];
  let left = randomInt(min, max);
  let right = randomInt(min, max);
  if (op === "-" && left < right) {
    [left, right] = [right, left];
  }
  const answer = op === "+" ? left + right : op === "-" ? left - right : left * right;
  return { left, right, op, answer };
}

function startMathGame() {
  if (state.math.timer) {
    clearInterval(state.math.timer);
  }

  state.math.running = true;
  state.math.timeLeft = 30;
  state.math.score = 0;
  $("math-score-label").textContent = "Score: 0";
  $("math-timer-label").textContent = "Time: 30s";
  setProgress("math-progress-bar", 30, 30);
  renderMathQuestion();

  state.math.timer = setInterval(() => {
    state.math.timeLeft -= 1;
    $("math-timer-label").textContent = `Time: ${state.math.timeLeft}s`;
    setProgress("math-progress-bar", state.math.timeLeft, 30);
    if (state.math.timeLeft <= 0) {
      clearInterval(state.math.timer);
      state.math.timer = null;
      finishMathGame();
    }
  }, 1000);
}

function renderMathQuestion() {
  const level = $("math-level").value;
  state.math.current = buildMathQuestion(level);
  $("math-card").innerHTML = `
    <p class="pill">${level}</p>
    <p class="big-text">${state.math.current.left} ${state.math.current.op} ${state.math.current.right} = ?</p>
    <div class="input-row">
      <input id="math-answer" type="number" placeholder="Type answer" />
      <button id="math-submit" class="action-btn">Submit</button>
    </div>
    <div id="math-feedback"></div>
  `;
  $("math-submit").addEventListener("click", submitMathAnswer);
  $("math-answer").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      submitMathAnswer();
    }
  });
}

function submitMathAnswer() {
  if (!state.math.running) {
    return;
  }
  const answer = Number($("math-answer").value);
  const correct = answer === state.math.current.answer;

  if (correct) {
    state.math.score += 1;
    $("math-score-label").textContent = `Score: ${state.math.score}`;
    $("math-feedback").innerHTML = `<div class="result good">Correct!</div>`;
    playTone("good");
  } else {
    $("math-feedback").innerHTML = `<div class="result bad">Correct answer: ${state.math.current.answer}</div>`;
    playTone("bad");
  }

  setTimeout(() => {
    if (state.math.running) {
      renderMathQuestion();
    }
  }, 350);
}

function finishMathGame() {
  state.math.running = false;
  state.scores.bestMath = Math.max(state.scores.bestMath, state.math.score);
  addPoints(state.math.score * 2);
  saveScores();
  renderScoreboard();
  $("math-card").innerHTML = `
    <h3>Time Up</h3>
    <p class="big-text">You solved ${state.math.score} questions.</p>
    <button id="math-restart" class="action-btn">Play Again</button>
  `;
  $("math-restart").addEventListener("click", startMathGame);
}

function renderWordChallenge() {
  const level = $("word-level").value;
  const options = wordChallenges.filter((item) => item.level === level);
  state.word.current = options[Math.floor(Math.random() * options.length)];

  $("word-card").innerHTML = `
    <p class="pill">${state.word.current.type} | ${level}</p>
    <p class="question-text">${state.word.current.prompt}</p>
    <div class="answer-box">${state.word.current.clue}</div>
    <div class="input-row">
      <input id="word-answer" type="text" placeholder="Type your answer" />
      <button id="word-submit" class="action-btn">Check Word</button>
    </div>
    <div id="word-feedback"></div>
  `;

  $("word-submit").addEventListener("click", submitWordChallenge);
}

function submitWordChallenge() {
  const guess = normalize($("word-answer").value);
  const answer = normalize(state.word.current.answer);
  if (guess === answer) {
    $("word-feedback").innerHTML = `<div class="result good">Correct! ${state.word.current.answer} is right.</div>`;
    addPoints(3);
    playTone("good");
  } else {
    $("word-feedback").innerHTML = `<div class="result bad">Try again next round. Correct answer: ${state.word.current.answer}.</div>`;
    playTone("bad");
  }
}

function todayKey() {
  const today = new Date();
  return `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
}

function seededIndex(seed, mod, offset) {
  let total = offset;
  for (let index = 0; index < seed.length; index += 1) {
    total += seed.charCodeAt(index) * (index + 3);
  }
  return total % mod;
}

function buildDailyItems() {
  const key = todayKey();
  const items = [];
  const usedIndexes = new Set();
  for (let index = 0; index < 5; index += 1) {
    let candidateIndex = seededIndex(key, dailyPool.length, index * 11);
    while (usedIndexes.has(candidateIndex)) {
      candidateIndex = (candidateIndex + 1) % dailyPool.length;
    }
    usedIndexes.add(candidateIndex);
    const chosen = dailyPool[candidateIndex];
    items.push(chosen);
  }
  state.daily = { key, items, index: 0, score: 0, done: false };
}

function renderDailyChallenge() {
  if (state.daily.key !== todayKey()) {
    buildDailyItems();
  }

  $("daily-date-label").textContent = `Challenge date: ${state.daily.key}`;
  $("daily-progress-label").textContent = `${state.daily.index} / ${state.daily.items.length} solved`;
  setProgress("daily-progress-bar", state.daily.index, state.daily.items.length);

  const item = state.daily.items[state.daily.index];
  const card = $("daily-card");

  if (!item) {
    state.daily.done = true;
    state.scores.dailyStars = Math.max(state.scores.dailyStars, state.daily.score);
    addPoints(state.daily.score * 2);
    saveScores();
    renderScoreboard();
    card.innerHTML = `
      <h3>Daily Challenge Complete</h3>
      <p class="big-text">You earned ${state.daily.score} stars today.</p>
      <div class="answer-box">Come back tomorrow for a new challenge.</div>
    `;
    $("daily-progress-label").textContent = `5 / 5 solved`;
    setProgress("daily-progress-bar", 5, 5);
    return;
  }

  if (item.type === "quiz") {
    card.innerHTML = `
      <p class="pill">Daily Quiz</p>
      <p class="question-text">${item.prompt}</p>
      <div class="option-grid">
        ${item.options.map((option) => `<button class="option-btn" data-daily-option="${option}">${option}</button>`).join("")}
      </div>
      <div id="daily-feedback"></div>
    `;
    card.querySelectorAll("[data-daily-option]").forEach((button) => {
      button.addEventListener("click", () => submitDailyAnswer(button.dataset.dailyOption));
    });
    return;
  }

  card.innerHTML = `
    <p class="pill">Daily Text Challenge</p>
    <p class="question-text">${item.prompt}</p>
    <div class="input-row">
      <input id="daily-answer" type="text" placeholder="Type your answer" />
      <button id="daily-submit" class="action-btn">Check</button>
      <button id="daily-hint" class="ghost-btn">Hint</button>
    </div>
    <div id="daily-feedback"></div>
  `;
  $("daily-submit").addEventListener("click", () => submitDailyAnswer($("daily-answer").value));
  $("daily-hint").addEventListener("click", () => {
    $("daily-feedback").innerHTML = `<div class="hint-box">Hint: ${item.hint}</div>`;
  });
}

function submitDailyAnswer(value) {
  const item = state.daily.items[state.daily.index];
  const correct = normalize(value) === normalize(item.answer);
  const feedback = $("daily-feedback");

  if (correct) {
    state.daily.score += 1;
    feedback.innerHTML = `<div class="result good">Correct!</div>`;
    playTone("good");
  } else {
    feedback.innerHTML = `<div class="result bad">Correct answer: ${item.answer}</div>`;
    playTone("bad");
  }

  setTimeout(() => {
    state.daily.index += 1;
    renderDailyChallenge();
  }, 900);
}

function bindEvents() {
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveView(button.dataset.target);
      if (button.dataset.target === "daily") {
        renderDailyChallenge();
      }
    });
  });

  $("quiz-start").addEventListener("click", startQuiz);
  $("riddle-next").addEventListener("click", renderRiddle);
  $("memory-start").addEventListener("click", startMemoryGame);
  $("math-start").addEventListener("click", startMathGame);
  $("word-next").addEventListener("click", renderWordChallenge);
}

function init() {
  loadScores();
  fillLevelSelects();
  renderScoreboard();
  bindEvents();
  buildDailyItems();
  $("daily-progress-label").textContent = `0 / 5 solved`;
  $("daily-date-label").textContent = `Challenge date: ${state.daily.key}`;
  $("quiz-card").innerHTML = `<p class="mini-note">Choose a topic and level, then start the quiz.</p>`;
  $("riddle-card").innerHTML = `<p class="mini-note">Pick a level and press New Riddle.</p>`;
  $("memory-card").innerHTML = `<p class="mini-note">Press Start Memory Round to see five words.</p>`;
  $("math-card").innerHTML = `<p class="mini-note">Press Start 30s Challenge to begin.</p>`;
  $("word-card").innerHTML = `<p class="mini-note">Pick a level and press New Word Challenge.</p>`;
  renderDailyChallenge();
}

init();
