// Free face symmetry test. Runs entirely in the browser: the photo is drawn
// on a canvas and compared with its own mirror image; nothing is uploaded.
(() => {
  const $ = id => document.getElementById(id);
  const file = $("sym-file"), work = $("sym-work"), mid = $("sym-mid"), tilt = $("sym-tilt");
  const original = $("sym-original"), left = $("sym-left"), right = $("sym-right"), score = $("sym-score");
  if (!file) return;
  const W = 300, H = 400;
  const source = document.createElement("canvas");
  source.width = W; source.height = H;
  let image = null;

  // Draw the photo, rotated by the tilt correction, cropped to 3:4.
  function drawSource() {
    const ctx = source.getContext("2d");
    ctx.fillStyle = "#0c1016"; ctx.fillRect(0, 0, W, H);
    const scale = Math.max(W / image.width, H / image.height);
    ctx.save();
    ctx.translate(W / 2, H / 2);
    ctx.rotate((Number(tilt.value) * Math.PI) / 180);
    ctx.drawImage(image, (-image.width * scale) / 2, (-image.height * scale) / 2, image.width * scale, image.height * scale);
    ctx.restore();
  }

  // Mean grey-level difference between each pixel and its mirror across x = m,
  // over the central part of the frame where the face usually is.
  function difference(m) {
    const data = source.getContext("2d").getImageData(0, 0, W, H).data;
    const grey = (x, y) => { const i = (y * W + x) * 4; return 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]; };
    const span = Math.floor(Math.min(m, W - m) * 0.9);
    let total = 0, count = 0;
    for (let y = Math.floor(H * 0.15); y < H * 0.9; y += 2) {
      for (let dx = 2; dx < span; dx += 2) {
        total += Math.abs(grey(Math.round(m - dx), y) - grey(Math.round(m + dx), y));
        count++;
      }
    }
    return count ? total / count : 255;
  }

  function composite(canvas, m, side) {
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#0c1016"; ctx.fillRect(0, 0, W, H);
    const half = side === "left" ? m : W - m;
    const sx = side === "left" ? 0 : m;
    // Keep the chosen half in place, then mirror it onto the other side.
    const dx = side === "left" ? W / 2 - half : W / 2;
    ctx.drawImage(source, sx, 0, half, H, dx, 0, half, H);
    ctx.save();
    ctx.translate(W, 0); ctx.scale(-1, 1);
    ctx.drawImage(source, sx, 0, half, H, side === "left" ? W / 2 - half : W / 2, 0, half, H);
    ctx.restore();
  }

  function render() {
    if (!image) return;
    drawSource();
    const m = (Number(mid.value) / 100) * W;
    const ctx = original.getContext("2d");
    ctx.drawImage(source, 0, 0);
    ctx.strokeStyle = "#d4a95f"; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(m, 0); ctx.lineTo(m, H); ctx.stroke(); ctx.setLineDash([]);
    composite(left, m, "left");
    composite(right, m, "right");
    const value = Math.max(0, Math.min(100, 100 - difference(m) * 1.6));
    score.textContent = `${value.toFixed(0)} / 100`;
  }

  function autoMidline() {
    if (!image) return;
    drawSource();
    let best = 50, bestDiff = Infinity;
    for (let p = 40; p <= 60; p += 0.5) {
      const d = difference((p / 100) * W);
      if (d < bestDiff) { bestDiff = d; best = p; }
    }
    mid.value = best;
    render();
  }

  file.addEventListener("change", () => {
    const chosen = file.files && file.files[0];
    if (!chosen) return;
    const url = URL.createObjectURL(chosen);
    const img = new Image();
    img.onload = () => { image = img; work.hidden = false; tilt.value = 0; autoMidline(); URL.revokeObjectURL(url); };
    img.onerror = () => { score.textContent = "That file could not be read as an image."; work.hidden = false; };
    img.src = url;
  });
  mid.addEventListener("input", render);
  tilt.addEventListener("input", render);
  $("sym-auto").addEventListener("click", autoMidline);
})();
