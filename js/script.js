function comprar(produto) {
  const numero = "5588999999999";
  const mensagem = `Quero comprar ${produto}`;
  window.open(`https://wa.me/${numero}?text=${encodeURIComponent(mensagem)}`);
}

function pesquisarProdutos() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const cards = document.querySelectorAll(".card");

  cards.forEach(card => {
    const nome = card.querySelector("h3").innerText.toLowerCase();

    if (nome.includes(input)) {
      card.style.display = ""; // volta ao normal
    } else {
      card.style.display = "none";
    }
  });
}



/* ARRASTAR COM MOUSE */
document.querySelectorAll(".scroll-catalogo").forEach(slider => {
  let isDown = false;
  let startX;
  let scrollLeft;

  slider.addEventListener("mousedown", e => {
    isDown = true;
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
  });

  slider.addEventListener("mouseleave", () => isDown = false);
  slider.addEventListener("mouseup", () => isDown = false);

  slider.addEventListener("mousemove", e => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - slider.offsetLeft;
    const walk = (x - startX) * 2;
    slider.scrollLeft = scrollLeft - walk;
  });
});

/* AUTO SCROLL */
document.querySelectorAll(".auto-scroll").forEach(container => {
  let scrollAmount = 0;

  function autoScroll() {
    scrollAmount += 1;

    if (scrollAmount >= container.scrollWidth - container.clientWidth) {
      scrollAmount = 0;
    }

    container.scrollTo({
      left: scrollAmount,
      behavior: "smooth"
    });
  }

  let interval = setInterval(autoScroll, 30);

  container.addEventListener("mouseenter", () => clearInterval(interval));
  container.addEventListener("mouseleave", () => {
    interval = setInterval(autoScroll, 30);
  });
});