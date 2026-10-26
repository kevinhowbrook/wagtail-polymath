// Run with: node --test tests/js/*.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

const JS = new URL("../../src/wagtail_polymath/static/wagtail_polymath/js/", import.meta.url);
const read = (file) => readFileSync(new URL(file, JS), "utf8");

const FONTS_URL = "[mathjax]/fonts";

function run(file, { fontsUrl, window = {} } = {}) {
  const dataset = fontsUrl ? { fontsUrl } : {};
  const sandbox = {
    window,
    document: { currentScript: { dataset }, getElementById: () => null },
    console: { warn() {}, error() {} },
    setTimeout,
    clearTimeout,
  };
  vm.runInNewContext(read(file), sandbox);
  // Round-trip through JSON so objects from the sandbox's realm compare with deepEqual
  return { MathJax: sandbox.window.MathJax, config: JSON.parse(JSON.stringify(sandbox.window.MathJax)) };
}

test("mathjax_init.js without fonts_url keeps polymath's defaults", () => {
  const { config } = run("mathjax_init.js");
  assert.deepEqual(config, { loader: { load: ["input/asciimath"] } });
});

test("mathjax_init.js sets the fonts path and keeps AsciiMath", () => {
  const { config } = run("mathjax_init.js", { fontsUrl: FONTS_URL });
  assert.deepEqual(config, { loader: { load: ["input/asciimath"], paths: { fonts: FONTS_URL } } });
});

test("the widget without fonts_url sets no fonts path", () => {
  const { config } = run("wagtail_polymath-mathjax-widget.js");
  assert.deepEqual(config.loader, { load: ["input/asciimath"] });
});

test("the widget sets the fonts path and keeps its startup.ready hook", () => {
  const { MathJax, config } = run("wagtail_polymath-mathjax-widget.js", { fontsUrl: FONTS_URL });
  assert.deepEqual(config.loader, { load: ["input/asciimath"], paths: { fonts: FONTS_URL } });
  assert.equal(typeof MathJax.startup.ready, "function");
});

test("the widget leaves an already loaded MathJax alone", () => {
  const loaded = { version: "4.1.3", startup: { promise: Promise.resolve() } };
  const { MathJax } = run("wagtail_polymath-mathjax-widget.js", { fontsUrl: FONTS_URL, window: { MathJax: loaded } });
  assert.equal(MathJax, loaded);
  assert.equal(MathJax.loader, undefined);
});
