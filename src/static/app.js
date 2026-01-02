document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageEl = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    activitiesList.innerHTML = "<p>Loading activities...</p>";
    try {
      const response = await fetch("/activities");
      if (!response.ok) throw new Error("Failed to load activities");
      const activities = await response.json();
      renderActivities(activities);
      populateSelect(activities);
    } catch (error) {
      activitiesList.innerHTML = `<p class="message error">${escapeHtml(
        error.message
      )}</p>`;
    }
  }

  function renderActivities(activities) {
    activitiesList.innerHTML = "";
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";
      const spotsLeft = details.max_participants - details.participants.length;

      activityCard.innerHTML = `
        <h4>${escapeHtml(name)}</h4>
        <p>${escapeHtml(details.description || "")}</p>
        <p><strong>Schedule:</strong> ${escapeHtml(details.schedule || "")}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <strong>Participants</strong>
          ${Array.isArray(details.participants) &&
          details.participants.length
            ? `<ul class="participants-list">${details.participants
                .map((email) => `<li><span class="participant-email">${escapeHtml(
                  email
                )}</span> <button class="delete-btn" data-activity="${escapeHtml(
                  name
                )}" data-email="${escapeHtml(email)}" title="Unregister">🗑️</button></li>`)
                .join("")}</ul>`
            : `<p class="participants-list">No participants yet.</p>`}
        </div>
      `;

      activitiesList.appendChild(activityCard);
    });
  }

  function populateSelect(activities) {
    // Remove any existing activity options (keep the placeholder)
    Array.from(activitySelect.querySelectorAll("option[value]"))
      .filter((o) => o.value !== "")
      .forEach((o) => o.remove());

    Object.keys(activities).forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const activity = activitySelect.value;
    if (!email || !activity) {
      return showMessage(
        "Please provide an email and select an activity.",
        "error"
      );
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(
          email
        )}`,
        {
          method: "POST",
        }
      );
      const result = await response.json();
      if (!response.ok)
        throw new Error(result.detail || result.message || "Signup failed");
      showMessage(result.message || "Signed up successfully!", "success");
      signupForm.reset();
      await fetchActivities(); // refresh UI to show new participant
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  function showMessage(text, type) {
    messageEl.className = `message ${type}`;
    messageEl.textContent = text;
    // hide after a short delay
    setTimeout(() => {
      messageEl.className = "hidden";
      messageEl.textContent = "";
    }, 4000);
  }

  function escapeHtml(unsafe) {
    return String(unsafe || "").replace(
      /[&<>"']/g,
      (m) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        }[m])
    );
  }

  // Handle participant delete/unregister clicks (event delegation)
  activitiesList.addEventListener("click", async (e) => {
    const btn = e.target.closest(".delete-btn");
    if (!btn) return;
    const activity = btn.dataset.activity;
    const email = btn.dataset.email;
    if (!activity || !email) return;
    if (!confirm(`Unregister ${email} from ${activity}?`)) return;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(
          email
        )}`,
        { method: "DELETE" }
      );
      const result = await response.json();
      if (!response.ok)
        throw new Error(result.detail || result.message || "Unregister failed");
      showMessage(result.message || "Unregistered successfully", "success");
      await fetchActivities();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  // Initialize app
  fetchActivities();
});
