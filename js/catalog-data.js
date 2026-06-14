const produtosPadrao = [
  { nome: "Dior Sauvage", categoria: "masculino", img: "img/produtos/masculinos/dior-sauvage-card.png", preco5: "59,99", preco10: "109,99" },
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
  { nome: "Scandal Masculino EDT", categoria: "masculino", img: "img/produtos/masculinos/scandal_pour homme.png", preco5: "59,99", preco10: "109,99" },
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

const produtosDestaquePadrao = ["Dior Sauvage", "La Vie Est Belle", "Versace Eros", "Yara Rosa"];

const notasPorProduto = {
  "Dior Sauvage": "bergamota, pimenta, lavanda, ambroxan e madeiras",
  "Dior Homme Sport": "limão, bergamota, gengibre, elemi e madeiras",
  "Bleu de Chanel": "cítricos, hortelã, gengibre, incenso, âmbar e sândalo",
  "Allure Homme Sport": "laranja, notas marinhas, pimenta, almíscar e fava tonka",
  "Club de Nuit Intense": "limão, abacaxi, bergamota, rosa, bétula, almíscar e âmbar",
  "Asad Lattafa": "pimenta preta, tabaco, baunilha, âmbar, patchouli e madeiras",
  "212 VIP Black": "absinto, lavanda, anis, baunilha e almíscar",
  "212 Men": "folhas verdes, especiarias, lavanda, sândalo e almíscar",
  "Encre Noire": "cipreste, vetiver, cashmere, almíscar e madeira",
  "Ferrari Black": "maçã, ameixa, bergamota, canela, baunilha e cedro",
  "Le Male Elixir": "lavanda, hortelã, baunilha, mel, tabaco e fava tonka",
  "Le Male Le Parfum": "cardamomo, lavanda, íris, baunilha e madeiras",
  "One Million": "toranja, canela, couro, âmbar, patchouli e especiarias",
  "Phantom": "lavanda, limão, maçã, patchouli, baunilha e vetiver",
  "Invictus Victory": "limão, pimenta rosa, lavanda, baunilha, fava tonka e âmbar",
  "Invictus Victory Elixir": "lavanda, cardamomo, pimenta, incenso, baunilha e fava tonka",
  "Silver Scent": "flor de laranjeira, limão, lavanda, cardamomo, fava tonka e âmbar",
  "Versace Eros": "hortelã, maçã verde, limão, fava tonka, baunilha e cedro",
  "L'eau d'Issey Miyake": "yuzu, bergamota, noz-moscada, lírio, tabaco e sândalo",
  "Hugo Boss Night": "lavanda, bétula, violeta, cardamomo e madeiras",
  "Scandal Masculino EDT": "sálvia, mandarina, caramelo, fava tonka, vetiver e cedro",
  "Good Girl": "amêndoa, café, jasmim, tuberosa, cacau, fava tonka e baunilha",
  "Scandal Feminino": "laranja sanguínea, mel, gardênia, patchouli e caramelo",
  "Libre Yves Saint": "lavanda, mandarina, flor de laranjeira, jasmim, baunilha e âmbar gris",
  "Yara Rosa": "orquídea, frutas tropicais, baunilha, almíscar e notas doces",
  "La Vie Est Belle": "íris, pera, cassis, jasmim, flor de laranjeira, patchouli e pralinê",
  "212 VIP Rosé": "champagne rosé, pêssego, flor de pêssego, almíscar e âmbar",
  "Lady Million": "framboesa, neroli, flor de laranjeira, jasmim, mel e patchouli",
  "Issey Miyake Fem": "lótus, frésia, rosa, lírio, peônia, madeiras e almíscar",
  "Afeef Lattafa": "bergamota, pimenta rosa, jasmim, tuberosa, baunilha e sândalo",
  "Royal Amber Rouge": "açafrão, jasmim, âmbar, madeiras, resinas e almíscar",
  "My Way": "bergamota, flor de laranjeira, tuberosa, jasmim, baunilha e cedro",
  "Idôle": "bergamota, pera, rosa, jasmim, almíscar branco e baunilha"
};

const marcasPorProduto = {
  "Dior Sauvage": "Dior",
  "Dior Homme Sport": "Dior",
  "Bleu de Chanel": "Chanel",
  "Allure Homme Sport": "Chanel",
  "Club de Nuit Intense": "Armaf",
  "Asad Lattafa": "Lattafa",
  "212 VIP Black": "Carolina Herrera",
  "212 Men": "Carolina Herrera",
  "Encre Noire": "Lalique",
  "Ferrari Black": "Ferrari",
  "Le Male Elixir": "Jean Paul Gaultier",
  "Le Male Le Parfum": "Jean Paul Gaultier",
  "One Million": "Paco Rabanne",
  "Phantom": "Paco Rabanne",
  "Invictus Victory": "Paco Rabanne",
  "Invictus Victory Elixir": "Paco Rabanne",
  "Silver Scent": "Jacques Bogart",
  "Versace Eros": "Versace",
  "L'eau d'Issey Miyake": "Issey Miyake",
  "Hugo Boss Night": "Hugo Boss",
  "Scandal Masculino EDT": "Jean Paul Gaultier",
  "Good Girl": "Carolina Herrera",
  "Scandal Feminino": "Jean Paul Gaultier",
  "Libre Yves Saint": "Yves Saint Laurent",
  "Yara Rosa": "Lattafa",
  "La Vie Est Belle": "Lancôme",
  "212 VIP Rosé": "Carolina Herrera",
  "Lady Million": "Paco Rabanne",
  "Issey Miyake Fem": "Issey Miyake",
  "Afeef Lattafa": "Lattafa",
  "Royal Amber Rouge": "Lattafa",
  "My Way": "Giorgio Armani",
  "Idôle": "Lancôme"
};

const logosPorMarca = {
  "Dior": "img/marcas/dior.png",
  "Chanel": "img/marcas/chanel.png",
  "Armaf": "img/marcas/armaf.png",
  "Lattafa": "img/marcas/lattafa.png",
  "Carolina Herrera": "img/marcas/carolina-herrera.png",
  "Lalique": "img/marcas/lalique.png",
  "Ferrari": "img/marcas/ferrari.png",
  "Jean Paul Gaultier": "img/marcas/jean-paul-gaultier.png",
  "Paco Rabanne": "img/marcas/paco-rabanne.png",
  "Jacques Bogart": "img/marcas/jacques-bogart.png",
  "Versace": "img/marcas/versace.png",
  "Issey Miyake": "img/marcas/issey-miyake.png",
  "Hugo Boss": "img/marcas/hugo-boss.png",
  "Yves Saint Laurent": "img/marcas/yves-saint-laurent.png",
  "Lancôme": "img/marcas/lancome.png",
  "Giorgio Armani": "img/marcas/giorgio-armani.png",
  "Decant's": "img/marcas/decants.png"
};

const imagensDestaquePorProduto = {
  "dior sauvage": "img/highlights/masculine/dior_sauvage.png",
  "dior homme sport": "img/highlights/masculine/dior_homme_sport.png",
  "bleu de chanel": "img/highlights/masculine/bleu_de_chanel.png",
  "allure homme sport": "img/highlights/masculine/allure_homme_sport.png",
  "club de nuit intense": "img/highlights/masculine/club_de_nuit_intense.png",
  "asad lattafa": "img/highlights/masculine/asad_lattafa.png",
  "212 vip black": "img/highlights/masculine/212_vip_black.png",
  "212 men": "img/highlights/masculine/212_men.png",
  "encre noire": "img/highlights/masculine/Encre_Noire.png",
  "ferrari black": "img/highlights/masculine/ferrari_black.png",
  "le male elixir": "img/highlights/masculine/le_male_elixir.png",
  "le male le parfum": "img/highlights/masculine/le_male_le_parfum.png",
  "one million": "img/highlights/masculine/one_million.png",
  "phantom": "img/highlights/masculine/Phantom_Paco_Rabanne.png",
  "invictus victory": "img/highlights/masculine/Invictus_Victory.png",
  "invictus victory elixir": "img/highlights/masculine/Invictus_Victory_Elixir.png",
  "silver scent": "img/highlights/masculine/Silver_Scence.png",
  "versace eros": "img/highlights/masculine/versace_eros.png",
  "l'eau d'issey miyake": "img/highlights/masculine/issey_miyake.png",
  "hugo boss night": "img/highlights/masculine/Hugo_Boss_Bottled_Night.png",
  "scandal masculino edt": "img/highlights/masculine/scandal_pour homme.png",
  "good girl": "img/highlights/feminine/Good_Girl.png",
  "scandal feminino": "img/highlights/feminine/scandal.png",
  "libre yves saint": "img/highlights/feminine/libre_yves_saint.png",
  "yara rosa": "img/highlights/feminine/yara_rosa.png",
  "la vie est belle": "img/highlights/feminine/la_vie_est_belle.png",
  "212 vip rose": "img/highlights/feminine/212_vip_rose.png",
  "lady million": "img/highlights/feminine/lady_million.png",
  "issey miyake fem": "img/highlights/feminine/issey_miyake_fem.png",
  "afeef lattafa": "img/highlights/feminine/afeef_lattafa.png",
  "royal amber rouge": "img/highlights/feminine/royal_amber_rougue.png",
  "my way": "img/highlights/feminine/my_way.png",
  "idole": "img/highlights/feminine/idole.png"
};

const imagensContainerPorProduto = {
  "212 men": [
    "img/container/masculinos/212_man/212_men1.png",
    "img/container/masculinos/212_man/212_men2.png",
    "img/container/masculinos/212_man/212_men3.png",
    "img/container/masculinos/212_man/212_men4.png"
  ],
  "212 vip black": [
    "img/container/masculinos/212_vip_black/212_vip_black1.png",
    "img/container/masculinos/212_vip_black/212_vip_black2.png",
    "img/container/masculinos/212_vip_black/212_vip_black3.png",
    "img/container/masculinos/212_vip_black/212_vip_black4.png"
  ],
  "212 vip rose": [
    "img/container/femininos/212_vip_rose/212_vip_rose1.png",
    "img/container/femininos/212_vip_rose/212_vip_rose2.png",
    "img/container/femininos/212_vip_rose/212_vip_rose3.png",
    "img/container/femininos/212_vip_rose/212_vip_rose4.png"
  ],
  "afeef lattafa": [
    "img/container/femininos/afeef_lattafa/afeef_lattafa1.png",
    "img/container/femininos/afeef_lattafa/afeef_lattafa2.png",
    "img/container/femininos/afeef_lattafa/afeef_lattafa3.png",
    "img/container/femininos/afeef_lattafa/afeef_lattafa4.png"
  ],
  "allure homme sport": [
    "img/container/masculinos/allure_homme_sport/0b8b5652-e9e8-411d-bd6b-0bff168f8a53.png",
    "img/container/masculinos/allure_homme_sport/10bc8131-f619-4855-9289-7b2c50f544ef.png",
    "img/container/masculinos/allure_homme_sport/d0b0e401-b210-4894-a5be-627a796e36c6.png",
    "img/container/masculinos/allure_homme_sport/fd14d7be-d6f9-4682-b80d-c42297a9ab06.png"
  ],
  "asad lattafa": [
    "img/container/masculinos/asad_lattafa/asad_lattafa1.png",
    "img/container/masculinos/asad_lattafa/asad_lattafa2.png",
    "img/container/masculinos/asad_lattafa/asad_lattafa3.png",
    "img/container/masculinos/asad_lattafa/asad_lattafa4.png"
  ],
  "bleu de chanel": [
    "img/container/masculinos/bleu_de_chanel/bleu_de_chanel1.png",
    "img/container/masculinos/bleu_de_chanel/bleu_de_chanel2.png",
    "img/container/masculinos/bleu_de_chanel/bleu_de_chanel3.png",
    "img/container/masculinos/bleu_de_chanel/bleu_de_chanel4.png"
  ],
  "club de nuit intense": [
    "img/container/masculinos/club_de_nuit_intense/club_de_nuit_intense1.png",
    "img/container/masculinos/club_de_nuit_intense/club_de_nuit_intense2.png",
    "img/container/masculinos/club_de_nuit_intense/club_de_nuit_intense3.png",
    "img/container/masculinos/club_de_nuit_intense/club_de_nuit_intense4.png"
  ],
  "dior homme sport": [
    "img/container/masculinos/dior_homme_sport/dior_homme_sport1.png",
    "img/container/masculinos/dior_homme_sport/dior_homme_sport2.png",
    "img/container/masculinos/dior_homme_sport/dior_homme_sport3.png",
    "img/container/masculinos/dior_homme_sport/dior_homme_sport4.png"
  ],
  "dior sauvage": [
    "img/container/masculinos/dior_sauvage/dior_sauvage1.png",
    "img/container/masculinos/dior_sauvage/dior_sauvage2.png",
    "img/container/masculinos/dior_sauvage/dior_sauvage3.png",
    "img/container/masculinos/dior_sauvage/dior_sauvage4.png"
  ],
  "encre noire": [
    "img/container/masculinos/Encre_Noire/Encre_Noire1.png",
    "img/container/masculinos/Encre_Noire/Encre_Noire2.png",
    "img/container/masculinos/Encre_Noire/Encre_Noire3.png",
    "img/container/masculinos/Encre_Noire/Encre_Noire4.png"
  ],
  "ferrari black": [
    "img/container/masculinos/ferrari_black/ferrari_black3.png",
    "img/container/masculinos/ferrari_black/ferrari_black4.png",
    "img/container/masculinos/ferrari_black/ferrari_black1.png",
    "img/container/masculinos/ferrari_black/ferrari_black2.png"
  ],
  "good girl": [
    "img/container/femininos/Good_Girl/Good_Girl1.png",
    "img/container/femininos/Good_Girl/Good_Girl2.png",
    "img/container/femininos/Good_Girl/Good_Girl3.png",
    "img/container/femininos/Good_Girl/Good_Girl4.png"
  ],
  "hugo boss night": [
    "img/container/masculinos/Hugo_Boss_Bottled_Night/Hugo_Boss_Bottled_Night1.png",
    "img/container/masculinos/Hugo_Boss_Bottled_Night/Hugo_Boss_Bottled_Night2.png",
    "img/container/masculinos/Hugo_Boss_Bottled_Night/Hugo_Boss_Bottled_Night3.png",
    "img/container/masculinos/Hugo_Boss_Bottled_Night/Hugo_Boss_Bottled_Night4.png"
  ],
  "idole": [
    "img/container/femininos/Idole/Idole1.png",
    "img/container/femininos/Idole/Idole2.png",
    "img/container/femininos/Idole/Idole3.png",
    "img/container/femininos/Idole/Idole4.png"
  ],
  "l'eau d'issey miyake": [
    "img/container/masculinos/homme_Issey_miyake/homme_Issey_miyake1.png",
    "img/container/masculinos/homme_Issey_miyake/homme_Issey_miyake2.png",
    "img/container/masculinos/homme_Issey_miyake/homme_Issey_miyake3.png",
    "img/container/masculinos/homme_Issey_miyake/homme_Issey_miyake4.png"
  ],
  "invictus victory elixir": [
    "img/container/masculinos/Invictus_Victory_Elixir/Invictus_Victory_Elixir1.png",
    "img/container/masculinos/Invictus_Victory_Elixir/Invictus_Victory_Elixir2.png",
    "img/container/masculinos/Invictus_Victory_Elixir/Invictus_Victory_Elixir3.png",
    "img/container/masculinos/Invictus_Victory_Elixir/Invictus_Victory_Elixir4.png"
  ],
  "invictus victory": [
    "img/container/masculinos/Invictus_Victory/Invictus_Victory1.png",
    "img/container/masculinos/Invictus_Victory/Invictus_Victory2.png",
    "img/container/masculinos/Invictus_Victory/Invictus_Victory3.png",
    "img/container/masculinos/Invictus_Victory/Invictus_Victory4.png"
  ],
  "le male elixir": [
    "img/container/masculinos/le_male_elixir/le_male_elixir1.png",
    "img/container/masculinos/le_male_elixir/le_male_elixir2.png",
    "img/container/masculinos/le_male_elixir/le_male_elixir3.png",
    "img/container/masculinos/le_male_elixir/le_male_elixir4.png"
  ],
  "le male le parfum": [
    "img/container/masculinos/le_male_le_parfum/le_male_le_parfum1.png",
    "img/container/masculinos/le_male_le_parfum/le_male_le_parfum2.png",
    "img/container/masculinos/le_male_le_parfum/le_male_le_parfum3.png",
    "img/container/masculinos/le_male_le_parfum/le_male_le_parfum4.png"
  ],
  "one million": [
    "img/container/masculinos/one_million/one_million1.png",
    "img/container/masculinos/one_million/one_million2.png",
    "img/container/masculinos/one_million/one_million3.png",
    "img/container/masculinos/one_million/one_million4.png"
  ],
  "la vie est belle": [
    "img/container/femininos/la_vie_est_belle/la_vie_est_belle1.png",
    "img/container/femininos/la_vie_est_belle/la_vie_est_belle2.png",
    "img/container/femininos/la_vie_est_belle/la_vie_est_belle3.png",
    "img/container/femininos/la_vie_est_belle/la_vie_est_belle4.png"
  ],
  "lady million": [
    "img/container/femininos/lady_million/lady_million1.png",
    "img/container/femininos/lady_million/lady_million2.png",
    "img/container/femininos/lady_million/lady_million3.png",
    "img/container/femininos/lady_million/lady_million4.png"
  ],
  "libre yves saint": [
    "img/container/femininos/libre_yves_saint_laurent/libre_yves_saint_laurent1.png",
    "img/container/femininos/libre_yves_saint_laurent/libre_yves_saint_laurent2.png",
    "img/container/femininos/libre_yves_saint_laurent/libre_yves_saint_laurent3.png",
    "img/container/femininos/libre_yves_saint_laurent/libre_yves_saint_laurent4.png"
  ],
  "my way": [
    "img/container/femininos/my_way/my_way1.png",
    "img/container/femininos/my_way/my_way2.png",
    "img/container/femininos/my_way/my_way3.png",
    "img/container/femininos/my_way/my_way4.png"
  ],
  "phantom": [
    "img/container/masculinos/Phantom_Paco_Rabanne/Phantom_Paco_Rabanne1.png",
    "img/container/masculinos/Phantom_Paco_Rabanne/Phantom_Paco_Rabanne2.png",
    "img/container/masculinos/Phantom_Paco_Rabanne/Phantom_Paco_Rabanne3.png",
    "img/container/masculinos/Phantom_Paco_Rabanne/Phantom_Paco_Rabanne4.png"
  ],
  "scandal masculino edt": [
    "img/container/masculinos/scandal_pour homme/scandal_pour homme1.png",
    "img/container/masculinos/scandal_pour homme/scandal_pour homme2.png",
    "img/container/masculinos/scandal_pour homme/scandal_pour homme3.png",
    "img/container/masculinos/scandal_pour homme/scandal_pour homme4.png"
  ],
  "scandal feminino": [
    "img/container/femininos/scandal/scandal1.png",
    "img/container/femininos/scandal/scandal2.png",
    "img/container/femininos/scandal/scandal3.png",
    "img/container/femininos/scandal/scandal4.png"
  ],
  "yara rosa": [
    "img/container/femininos/yara_rosa/yara_rosa1.png",
    "img/container/femininos/yara_rosa/yara_rosa2.png",
    "img/container/femininos/yara_rosa/yara_rosa3.png",
    "img/container/femininos/yara_rosa/yara_rosa4.png"
  ],
  "royal amber rouge": [
    "img/container/femininos/royal_amber_rougue/royal_amber_rougue1.png",
    "img/container/femininos/royal_amber_rougue/royal_amber_rougue2.png",
    "img/container/femininos/royal_amber_rougue/royal_amber_rougue3.png",
    "img/container/femininos/royal_amber_rougue/royal_amber_rougue4.png"
  ],
  "silver scent": [
    "img/container/masculinos/Silver_Scence/Silver_Scence1.png",
    "img/container/masculinos/Silver_Scence/Silver_Scence2.png",
    "img/container/masculinos/Silver_Scence/Silver_Scence3.png",
    "img/container/masculinos/Silver_Scence/Silver_Scence4.png"
  ],
  "issey miyake fem": [
    "img/container/femininos/issey_miyake_fem/issey_miyake_fem1.png",
    "img/container/femininos/issey_miyake_fem/issey_miyake_fem2.png",
    "img/container/femininos/issey_miyake_fem/issey_miyake_fem3.png",
    "img/container/femininos/issey_miyake_fem/issey_miyake_fem4.png"
  ],
  "versace eros": [
    "img/container/masculinos/versace_eros/versace_eros1.png",
    "img/container/masculinos/versace_eros/versace_eros2.png",
    "img/container/masculinos/versace_eros/versace_eros3.png",
    "img/container/masculinos/versace_eros/versace_eros4.png"
  ]
};
