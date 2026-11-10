#!/usr/bin/env node
// Render one ECharts option (JSON on stdin) to SVG on stdout, server-side,
// for the render-and-look step (docs/DESIGN.md, "Look at the dashboard").
// Usage: npm i echarts; python extract-chart.py < page.html > cfg.json;
//        node tools/render-chart.js < cfg.json > chart.svg
const echarts = require('echarts');
let input = '';
process.stdin.on('data', d => (input += d));
process.stdin.on('end', () => {
  const { option, width, height } = JSON.parse(input);
  const chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width: width || 640, height: height || 430 });
  chart.setOption(option);
  process.stdout.write(chart.renderToSVGString());
  process.exit(0);
});
