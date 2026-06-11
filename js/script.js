// Compatibility loader for cached HTML that still references js/script.js.
[
  "store-core.js",
  "store-catalog.js",
  "store-product.js",
  "store-cart.js",
  "store-checkout.js",
  "store-navigation.js",
  "store-init.js"
].forEach(arquivo => {
  document.write(`<script src="js/${arquivo}?v=1"><\/script>`);
});
