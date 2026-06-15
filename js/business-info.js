fetch("/api/public/business")
  .then(response => response.json())
  .then(data => {
    document.querySelectorAll("[data-business]").forEach(element => {
      const value = data[element.dataset.business];
      if (value) element.textContent = value;
    });
    document.querySelectorAll("[data-business-formalization]").forEach(element => {
      element.hidden = Boolean(data.formalized);
    });
  })
  .catch(() => {});
