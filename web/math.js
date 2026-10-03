function initializeNotesPage() {
  if (typeof renderMathInElement === "function") {
    document.querySelectorAll(".arithmatex").forEach((element) => {
      if (element.dataset.rendered === "yes") return;

renderMathInElement(element, {
        delimiters: [
          { left: "\\[", right: "\\]", display: true },
          { left: "\\(", right: "\\)", display: false },
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });

element.dataset.rendered = "yes";
    });
  }

const article = document.querySelector("article.md-content__inner");
  const isNote = Boolean(document.querySelector("[data-note-page]"));
  const resume = document.getElementById("continue-reading");

// Use a separate reading-history key for each GitHub Pages project.
  const storageKey =
    "notes:last-read:" +
    new URL(document.baseURI).pathname.split("/").filter(Boolean)[0];

if (resume) {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey));

if (saved && saved.url) {
        const target = new URL(saved.url, location.href);

if (target.origin === location.origin) {
          resume.href = target.href;
          resume.textContent = "ادامهٔ مطالعه: " + saved.title;
          resume.hidden = false;
        }
      }
    } catch {
      // The site still works if browser storage is unavailable.
    }
  }

if (!isNote || !article) return;

const title =
    article.querySelector("h1")?.textContent.replace(/¶$/, "").trim()
    || document.title;

try {
    localStorage.setItem(storageKey, JSON.stringify({
      title,
      url: location.href
    }));
  } catch {
    // Reading history is optional.
  }

if (article.querySelector(".note-tools")) return;

const tools = document.createElement("div");
  tools.className = "note-tools";

const share = document.createElement("button");
  share.type = "button";
  share.textContent = "اشتراکگذاری جلسه";

const status = document.createElement("span");
  status.className = "share-status";
  status.setAttribute("role", "status");

share.addEventListener("click", async () => {
    const url = location.href;

try {
      if (navigator.share) {
        await navigator.share({ title, url });
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(url);
        status.textContent = "لینک کپی شد.";
      } else {
        window.prompt("لینک این جلسه:", url);
      }
    } catch (error) {
      if (error.name !== "AbortError") {
        window.prompt("لینک این جلسه:", url);
      }
    }
  });

tools.append(share);

let fontSize = 100;

for (const [label, change] of [
    ["متن بزرگتر", 10],
    ["متن کوچکتر", -10]
  ]) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;

button.addEventListener("click", () => {
      fontSize = Math.max(80, Math.min(150, fontSize + change));
      article.style.fontSize = fontSize + "%";
    });

tools.append(button);
  }

tools.append(status);
  article.prepend(tools);
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initializeNotesPage);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeNotesPage);
} else {
  initializeNotesPage();
}
