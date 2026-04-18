class WebhookSettings {
  constructor() {
    this.apiBase = window.config?.apiBase || "http://localhost:8001";
    this.token = localStorage.getItem("github_token");
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadWebhooks();
    this.loadRecentEvents();
    this.setupThemeToggle();
  }

  setupEventListeners() {
    const form = document.getElementById("webhook-form");
    if (form) {
      form.addEventListener("submit", (e) => this.handleRegister(e));
    }

    const refreshBtn = document.getElementById("refresh-webhooks-btn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => this.loadWebhooks());
    }

    const refreshEventsBtn = document.getElementById("refresh-events-btn");
    if (refreshEventsBtn) {
      refreshEventsBtn.addEventListener("click", () => this.loadRecentEvents());
    }
  }

  setupThemeToggle() {
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
      const isDark = document.documentElement.classList.contains("dark");
      themeToggle.innerHTML = isDark
        ? '<span class="material-symbols-outlined">light_mode</span>'
        : '<span class="material-symbols-outlined">dark_mode</span>';

      themeToggle.addEventListener("click", () => {
        document.documentElement.classList.toggle("dark");
        const isDarkNow = document.documentElement.classList.contains("dark");
        localStorage.setItem("theme", isDarkNow ? "dark" : "light");
        themeToggle.innerHTML = isDarkNow
          ? '<span class="material-symbols-outlined">light_mode</span>'
          : '<span class="material-symbols-outlined">dark_mode</span>';
      });

      // Load saved theme
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme === "light") {
        document.documentElement.classList.remove("dark");
        themeToggle.innerHTML =
          '<span class="material-symbols-outlined">dark_mode</span>';
      }
    }
  }

  async loadWebhooks() {
    const list = document.getElementById("webhooks-list");
    const emptyState = document.getElementById("empty-state");

    try {
      list.innerHTML =
        '<div class="flex items-center justify-center py-12"><div class="animate-spin"><span class="material-symbols-outlined text-primary">hourglass_top</span></div></div>';

      const response = await fetch(`${this.apiBase}/webhooks/events`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load webhooks");
      }

      const data = await response.json();
      this.renderWebhooks(data.events || []);

      if (!data.events || data.events.length === 0) {
        list.classList.add("hidden");
        emptyState.classList.remove("hidden");
      } else {
        list.classList.remove("hidden");
        emptyState.classList.add("hidden");
      }
    } catch (error) {
      console.error("Error loading webhooks:", error);
      list.innerHTML = `
        <div class="p-4 bg-error/10 border border-error/30 rounded-lg">
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="text-sm font-body text-error">Failed to load webhooks</p>
          </div>
        </div>
      `;
    }
  }

  renderWebhooks(webhooks) {
    const list = document.getElementById("webhooks-list");
    const emptyState = document.getElementById("empty-state");

    if (!webhooks || webhooks.length === 0) {
      list.classList.add("hidden");
      emptyState.classList.remove("hidden");
      return;
    }

    list.classList.remove("hidden");
    emptyState.classList.add("hidden");

    // Group webhooks by repository
    const grouped = {};
    webhooks.forEach((event) => {
      const repo = event.repo || "Unknown";
      if (!grouped[repo]) {
        grouped[repo] = [];
      }
      grouped[repo].push(event);
    });

    list.innerHTML = Object.entries(grouped)
      .map(
        ([repo, events]) => `
      <div class="bg-white/5 border border-white/10 rounded-lg p-4 hover:border-primary/30 transition-colors">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-headline font-bold text-white">${repo}</h3>
            <p class="text-xs text-on-surface-variant font-body">${events.length} event${events.length !== 1 ? "s" : ""}</p>
          </div>
          <button
            class="delete-webhook-btn px-3 py-1.5 rounded-full bg-error/20 text-error hover:bg-error/30 font-label text-xs uppercase tracking-widest transition-all"
            data-repo="${repo}"
          >
            Delete
          </button>
        </div>
        <div class="text-xs text-on-surface-variant space-y-1">
          <p>Last event: ${events[0]?.timestamp ? new Date(events[0].timestamp).toLocaleString() : "Never"}</p>
          <p>Status: <span class="text-green-400">Active</span></p>
        </div>
      </div>
    `
      )
      .join("");

    // Add delete handlers
    document.querySelectorAll(".delete-webhook-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const repo = e.target.dataset.repo;
        this.deleteWebhook(repo);
      });
    });
  }

  async loadRecentEvents() {
    const list = document.getElementById("events-list");

    try {
      list.innerHTML =
        '<div class="flex items-center justify-center py-12"><div class="animate-spin"><span class="material-symbols-outlined text-primary">hourglass_top</span></div></div>';

      const response = await fetch(`${this.apiBase}/webhooks/events?limit=10`, {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load events");
      }

      const data = await response.json();
      this.renderEvents(data.events || []);
    } catch (error) {
      console.error("Error loading events:", error);
      list.innerHTML = `
        <div class="p-4 bg-error/10 border border-error/30 rounded-lg">
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-error">error</span>
            <p class="text-sm font-body text-error">Failed to load events</p>
          </div>
        </div>
      `;
    }
  }

  renderEvents(events) {
    const list = document.getElementById("events-list");

    if (!events || events.length === 0) {
      list.innerHTML =
        '<p class="text-center text-on-surface-variant py-8">No events yet</p>';
      return;
    }

    list.innerHTML = events
      .map(
        (event) => `
      <div class="bg-white/5 border border-white/10 rounded-lg p-3 hover:border-primary/30 transition-colors">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-sm font-body text-on-surface">
              <span class="font-bold text-primary">${event.event_type}</span>
              ${event.action ? `- ${event.action}` : ""}
            </p>
            <p class="text-xs text-on-surface-variant">${event.repo || "Unknown"}</p>
          </div>
          <span class="text-xs text-on-surface-variant whitespace-nowrap ml-2">
            ${event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ""}
          </span>
        </div>
        <div class="mt-2 flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full ${event.status === "processed" ? "bg-green-500" : event.status === "failed" ? "bg-error" : "bg-yellow-500"}"></span>
          <span class="text-xs text-on-surface-variant capitalize">${event.status || "pending"}</span>
        </div>
      </div>
    `
      )
      .join("");
  }

  async handleRegister(e) {
    e.preventDefault();

    const repoInput = document.getElementById("repo-input");
    const repo = repoInput.value.trim();
    const statusDiv = document.getElementById("form-status");

    if (!repo) {
      this.showStatus(
        statusDiv,
        "Please enter a repository name",
        "error"
      );
      return;
    }

    if (!repo.includes("/")) {
      this.showStatus(
        statusDiv,
        "Repository must be in format: owner/repository",
        "error"
      );
      return;
    }

    const events = Array.from(
      document.querySelectorAll('input[name="events"]:checked')
    ).map((cb) => cb.value);

    if (events.length === 0) {
      this.showStatus(
        statusDiv,
        "Please select at least one event type",
        "error"
      );
      return;
    }

    try {
      this.showStatus(statusDiv, "Registering webhook...", "loading");

      const response = await fetch(
        `${this.apiBase}/api/webhooks/register/${repo}?${events.map((e) => `events=${e}`).join("&")}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to register webhook");
      }

      this.showStatus(
        statusDiv,
        `Webhook registered for ${repo}`,
        "success"
      );
      repoInput.value = "";
      document.querySelectorAll('input[name="events"]').forEach((cb) => {
        cb.checked = cb.value === "issues";
      });

      // Reload webhooks after a short delay
      setTimeout(() => this.loadWebhooks(), 1000);
    } catch (error) {
      console.error("Error registering webhook:", error);
      this.showStatus(statusDiv, error.message, "error");
    }
  }

  async deleteWebhook(repo) {
    if (!confirm(`Delete webhook for ${repo}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `${this.apiBase}/api/webhooks/delete/${repo}/0`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete webhook");
      }

      this.loadWebhooks();
    } catch (error) {
      console.error("Error deleting webhook:", error);
      alert("Failed to delete webhook");
    }
  }

  showStatus(element, message, type) {
    if (!element) return;

    const bgColor =
      type === "error"
        ? "bg-error/10"
        : type === "success"
          ? "bg-green-500/10"
          : "bg-primary/10";
    const borderColor =
      type === "error"
        ? "border-error/30"
        : type === "success"
          ? "border-green-500/30"
          : "border-primary/30";
    const textColor =
      type === "error"
        ? "text-error"
        : type === "success"
          ? "text-green-400"
          : "text-primary";
    const icon =
      type === "error"
        ? "error"
        : type === "success"
          ? "check_circle"
          : "hourglass_top";

    element.innerHTML = `
      <div class="p-4 ${bgColor} border ${borderColor} rounded-lg">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined ${textColor} ${type === "loading" ? "animate-spin" : ""}">${icon}</span>
          <p class="text-sm font-body ${textColor}">${message}</p>
        </div>
      </div>
    `;
    element.classList.remove("hidden");

    if (type !== "loading") {
      setTimeout(() => {
        element.classList.add("hidden");
      }, 5000);
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new WebhookSettings();
});
