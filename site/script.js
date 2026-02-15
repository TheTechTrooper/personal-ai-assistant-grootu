const portfolio = {
  yearsBuilding: 2,
  focusAreas: ["AI Assistants", "Voice UX", "Automation"],
  skills: [
    "Python",
    "FastAPI",
    "Flet",
    "WebSockets",
    "Ollama",
    "Faster-Whisper",
    "SQLite",
    "GitHub Actions",
    "HTML/CSS/JS",
  ],
  projects: [
    {
      name: "Personal AI Assistant (Jarvis)",
      summary:
        "Offline-first assistant with wake-word voice flow, memory, desktop UI, and local LLM responses.",
      status: "Active",
      impact: "Daily personal productivity assistant",
    },
    {
      name: "Desktop Voice Control Deck",
      summary:
        "Custom Flet interface with live voice-state feedback so speaking timing is clear and reliable.",
      status: "Shipped",
      impact: "Reduced command timing confusion",
    },
    {
      name: "Memory + Task Engine",
      summary:
        "Persistent notes, profile memory, and actionable task commands with local SQLite storage.",
      status: "Shipped",
      impact: "Useful continuity across sessions",
    },
  ],
  timeline: [
    { date: "2026-02", text: "Built wake-word session flow and improved barge-in handling." },
    { date: "2026-02", text: "Added desktop 'Speak now' and processing visual states." },
    { date: "2026-02", text: "Set up docs and backup workflow across GitHub." },
  ],
};

function renderProjects() {
  const root = document.getElementById("project-list");
  root.innerHTML = portfolio.projects
    .map(
      (project) => `
        <article class="project-card">
          <h3>${project.name}</h3>
          <p>${project.summary}</p>
          <div class="meta-row">
            <span>${project.status}</span>
            <span>${project.impact}</span>
          </div>
        </article>
      `
    )
    .join("");
}

function renderSkills() {
  const root = document.getElementById("skill-list");
  root.innerHTML = portfolio.skills.map((s) => `<span class="chip">${s}</span>`).join("");
}

function renderTimeline() {
  const root = document.getElementById("timeline-list");
  root.innerHTML = portfolio.timeline
    .map(
      (entry) => `
        <article class="timeline-item">
          <div class="date">${entry.date}</div>
          <p>${entry.text}</p>
        </article>
      `
    )
    .join("");
}

function renderStats() {
  const projects = document.getElementById("stat-projects");
  const years = document.getElementById("stat-years");
  const focus = document.getElementById("stat-focus");
  if (!projects || !years || !focus) {
    return;
  }
  projects.textContent = String(portfolio.projects.length);
  years.textContent = String(portfolio.yearsBuilding);
  focus.textContent = String(portfolio.focusAreas.length);
}

function renderFooterYear() {
  document.getElementById("year").textContent = String(new Date().getFullYear());
}

function setupReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
}

renderProjects();
renderSkills();
renderTimeline();
renderStats();
renderFooterYear();
setupReveal();
