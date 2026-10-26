(function () {
  const fontsUrl = document.currentScript && document.currentScript.dataset.fontsUrl;

  window.MathJax = {
    loader: { load: ["input/asciimath"] }
  };
  // Set from WAGTAIL_POLYMATH["fonts_url"]. Without it, MathJax 4 loads its fonts from jsDelivr.
  if (fontsUrl) {
    window.MathJax.loader.paths = { fonts: fontsUrl };
  }
})();
