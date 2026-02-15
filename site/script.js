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
  statusFeed: [
    "Deploy pipeline active",
    "Offline AI assistant in production",
    "Voice UX latency tuning in progress",
    "Automation roadmap execution",
    "GitHub Pages synced to main",
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
  document.getElementById("stat-projects").textContent = String(portfolio.projects.length);
  document.getElementById("stat-years").textContent = String(portfolio.yearsBuilding);
  document.getElementById("stat-focus").textContent = String(portfolio.focusAreas.length);
}

function renderFooterYear() {
  document.getElementById("year").textContent = String(new Date().getFullYear());
}

function renderMarquee() {
  const root = document.getElementById("marquee-track");
  const items = [...portfolio.statusFeed, ...portfolio.statusFeed];
  root.innerHTML = items.map((text) => `<span>${text}</span>`).join("");
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

function setupStarfield() {
  const canvas = document.getElementById("starfield");
  if (!canvas) {
    return;
  }
  const ctx = canvas.getContext("2d");
  const stars = [];
  const starCount = 140;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function initStars() {
    stars.length = 0;
    for (let i = 0; i < starCount; i += 1) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        z: Math.random() * 1.2 + 0.2,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach((star) => {
      star.y += 0.18 * star.z;
      if (star.y > canvas.height) {
        star.y = -4;
        star.x = Math.random() * canvas.width;
      }
      const size = 1.2 * star.z;
      ctx.fillStyle = "rgba(157, 220, 255, 0.8)";
      ctx.fillRect(star.x, star.y, size, size);
    });
    window.requestAnimationFrame(draw);
  }

  resize();
  initStars();
  window.addEventListener("resize", () => {
    resize();
    initStars();
  });
  draw();
}

renderProjects();
renderSkills();
renderTimeline();
renderStats();
renderFooterYear();
renderMarquee();
setupReveal();
setupStarfield();
