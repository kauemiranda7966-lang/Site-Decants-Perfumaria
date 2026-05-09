const produtos = [

  // MASCULINOS
  { nome: "Dior Sauvage", categoria: "masculino", img: "img/produtos/masculinos/dior-sauvage.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Dior Homme Sport", categoria: "masculino", img: "img/produtos/masculinos/dior_homme_sport.png", preco5: "66,99", preco10: "105,00" },
  { nome: "Bleu de Chanel", categoria: "masculino", img: "img/produtos/masculinos/bleu_de_chanel.png", preco5: "80,99", preco10: "139,99" },
  { nome: "Allure Homme Sport", categoria: "masculino", img: "img/produtos/masculinos/allure_homme_sport.png", preco5: "80,99", preco10: "139,99" },
  { nome: "Club de Nuit Intense", categoria: "masculino", img: "img/produtos/masculinos/club_de_nuit_intense.png", preco5: "44,99", preco10: "54,99" },
  { nome: "Asad Lattafa", categoria: "masculino", img: "img/produtos/masculinos/asad_lattafa.png", preco5: "44,99", preco10: "69,99" },
  { nome: "212 VIP Black", categoria: "masculino", img: "img/produtos/masculinos/212_vip_black.png", preco5: "46,99", preco10: "75,99" },
  { nome: "212 Men", categoria: "masculino", img: "img/produtos/masculinos/212_men.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Encre Noire", categoria: "masculino", img: "img/produtos/masculinos/Encre_Noire.png", preco5: "54,99", preco10: "99,99" },
  { nome: "Ferrari Black", categoria: "masculino", img: "img/produtos/masculinos/Ferrari_Black.png", preco5: "34,99", preco10: "49,99" },
  { nome: "Le Male Elixir", categoria: "masculino", img: "img/produtos/masculinos/le_male_elixir.png", preco5: "54,99", preco10: "114,99" },
  { nome: "Le Male Le Parfum", categoria: "masculino", img: "img/produtos/masculinos/le_male_le_parfum.png", preco5: "44,99", preco10: "69,99" },
  { nome: "One Million", categoria: "masculino", img: "img/produtos/masculinos/one_million_paco_rabanne.png", preco5: "46,99", preco10: "74,99" },
  { nome: "Phantom", categoria: "masculino", img: "img/produtos/masculinos/Phantom_Paco_Rabanne.png", preco5: "49,99", preco10: "84,99" },
  { nome: "Invictus Victory", categoria: "masculino", img: "img/produtos/masculinos/Invictus_Victory.png", preco5: "54,99", preco10: "94,99" },
  { nome: "Invictus Victory Elixir", categoria: "masculino", img: "img/produtos/masculinos/Invictus_Victory_Elixir.png", preco5: "54,99", preco10: "94,99" },
  { nome: "Silver Scent", categoria: "masculino", img: "img/produtos/masculinos/Silver_Scence.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Versace Eros", categoria: "masculino", img: "img/produtos/masculinos/versace_eros.png", preco5: "69,99", preco10: "99,99" },
  { nome: "L'eau d'Issey Miyake", categoria: "masculino", img: "img/produtos/masculinos/homme_Issey_miyake.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Hugo Boss Night", categoria: "masculino", img: "img/produtos/masculinos/Hugo_Boss_Bottled_Night.png", preco5: "59,99", preco10: "69,99" },

  // FEMININOS
  { nome: "Good Girl", categoria: "feminino", img: "img/produtos/femininos/Good_Girl.jpg", preco5: "54,99", preco10: "94,99" },
  { nome: "Scandal Feminino", categoria: "feminino", img: "img/produtos/femininos/scandal.jpg", preco5: "59,99", preco10: "109,99" },
  { nome: "Libre Yves Saint", categoria: "feminino", img: "img/produtos/femininos/libre_yves_saint_laurent.png", preco5: "69,99", preco10: "129,99" },
  { nome: "Yara Rosa", categoria: "feminino", img: "img/produtos/femininos/yara_rosa.png", preco5: "54,99", preco10: "69,99" },
  { nome: "La Vie Est Belle", categoria: "feminino", img: "img/produtos/femininos/la_vie_est_belle.png", preco5: "54,99", preco10: "89,99" },
  { nome: "212 VIP Rosé", categoria: "feminino", img: "img/produtos/femininos/212_vip_rose.png", preco5: "54,99", preco10: "89,99" },
  { nome: "Lady Million", categoria: "feminino", img: "img/produtos/femininos/lady_million.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Issey Miyake Fem", categoria: "feminino", img: "img/produtos/femininos/issey_miyake_fem.png", preco5: "54,99", preco10: "99,99" },
  { nome: "Afeef Lattafa", categoria: "feminino", img: "img/produtos/femininos/afeef_lattafa.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Royal Amber Rouge", categoria: "feminino", img: "img/produtos/femininos/royal_amber_rougue.png", preco5: "59,99", preco10: "109,99" },
  { nome: "My Way", categoria: "feminino", img: "img/produtos/femininos/my_way.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Idôle", categoria: "feminino", img: "img/produtos/femininos/Idole.png", preco5: "59,99", preco10: "109,99" }
];

const masculinosContainer = document.getElementById("masculinosContainer");
const femininosContainer = document.getElementById("femininosContainer");

if(masculinosContainer && femininosContainer){
  mostrarTodos();
}

// MOSTRAR TODOS
function mostrarTodos() {
  renderProdutos(
    produtos.filter(p => p.categoria === "masculino"),
    masculinosContainer
  );

  renderProdutos(
    produtos.filter(p => p.categoria === "feminino"),
    femininosContainer
  );
}

// FILTRAR
function mostrarCategoria(tipo) {
  const filtrados = produtos.filter(p => p.categoria === tipo);

  if(tipo === "masculino"){
    renderProdutos(filtrados, masculinosContainer);
    document.querySelector("#masculinosContainer").scrollIntoView({ behavior: "smooth", block: "center" });
  }

  if(tipo === "feminino"){
    renderProdutos(filtrados, femininosContainer);
    document.querySelector("#femininosContainer").scrollIntoView({ behavior: "smooth", block: "center" });
  }
}


// RENDER
function renderProdutos(lista, container) {
  if(!container) return;

  container.innerHTML = "";


lista.forEach(produto => {
container.innerHTML += `
      <div class="card">
        <img src="${produto.img}">
        <h3>${produto.nome}</h3>

        <p>5ml R$ ${produto.preco5}</p>
        <p>10ml R$ ${produto.preco10}</p>

        <button data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)">Comprar</button>
      </div>
    `;
  });
}

// BUSCA
function pesquisarProdutos() {
  const input = document.getElementById("searchInput").value.toLowerCase();

  const filtradosMasculinos = produtos.filter(p =>
    p.categoria === "masculino" &&
    p.nome.toLowerCase().includes(input)
  );

  const filtradosFemininos = produtos.filter(p =>
    p.categoria === "feminino" &&
    p.nome.toLowerCase().includes(input)
  );

  renderProdutos(filtradosMasculinos, masculinosContainer);
  renderProdutos(filtradosFemininos, femininosContainer);
}