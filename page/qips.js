/* Mesures visuelles portées du Aesthetics Toolbox (Redies, Bartho et al., 2025, MIT).
   Port fidèle de 10 mesures du code Python (AT/color_and_simple_qips.py, AT/balance_qips.py).
   Entrée : pixels RGBA (Uint8ClampedArray), largeur, hauteur. Vérifié contre le Toolbox. */
var QIP = (function () {
  function roundHalfEven(x) {
    var r = Math.round(x);
    return (Math.abs(x % 1) === 0.5 && r % 2 !== 0) ? r - 1 : r;
  }

  var LIN = new Float64Array(256);
  for (var i = 0; i < 256; i++) {
    var c = i / 255;
    LIN[i] = c > 0.04045 ? Math.pow((c + 0.055) / 1.055, 2.4) : c / 12.92;
  }
  function fLab(t) { return t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116; }

  function entropyOf(values, max) {
    var hist = new Float64Array(256), n = values.length, k;
    if (max > 0) { for (k = 0; k < n; k++) hist[roundHalfEven(values[k] / max * 255)]++; }
    else { hist[0] = n; }
    var e = 0;
    for (k = 0; k < 256; k++) if (hist[k] > 0) { var p = hist[k] / n; e -= p * Math.log2(p); }
    return e;
  }

  function otsu(gray, n) {
    var min = 255, max = 0, k;
    for (k = 0; k < n; k++) { var v = gray[k]; if (v < min) min = v; if (v > max) max = v; }
    if (min === max) return min;
    var nb = max - min + 1, counts = new Float64Array(nb);
    for (k = 0; k < n; k++) counts[gray[k] - min]++;
    var w1 = new Float64Array(nb), m1 = new Float64Array(nb), w2 = new Float64Array(nb), m2 = new Float64Array(nb);
    var cw = 0, cm = 0;
    for (k = 0; k < nb; k++) { cw += counts[k]; cm += counts[k] * (k + min); w1[k] = cw; m1[k] = cm / cw; }
    cw = 0; cm = 0;
    for (k = nb - 1; k >= 0; k--) { cw += counts[k]; cm += counts[k] * (k + min); w2[k] = cw; m2[k] = cm / cw; }
    var best = -1, idx = 0;
    for (k = 0; k < nb - 1; k++) {
      var d = m1[k] - m2[k + 1], v12 = w1[k] * w2[k + 1] * d * d;
      if (v12 > best) { best = v12; idx = k; }
    }
    return idx + min;
  }

  /* Somme des éléments de m (h lignes, w colonnes) avec j - i >= k (triu) ou j - i <= k (tril) */
  function triSum(m, h, w, k, upper) {
    var s = 0;
    for (var i = 0; i < h; i++) {
      var row = i * w, j0, j1;
      if (upper) { j0 = Math.max(0, i + k); j1 = w; } else { j0 = 0; j1 = Math.min(w, i + k + 1); }
      for (var j = j0; j < j1; j++) s += m[row + j];
    }
    return s;
  }
  function rot90(m, h, w) { // np.rot90 : sortie (w lignes, h colonnes), r[i][j] = m[j][w-1-i]
    var r = new Uint8Array(w * h);
    for (var i = 0; i < w; i++) for (var j = 0; j < h; j++) r[i * h + j] = m[j * w + (w - 1 - i)];
    return r;
  }
  function rectSum(m, w, y0, y1, x0, x1) {
    var s = 0;
    for (var y = y0; y < y1; y++) { var row = y * w; for (var x = x0; x < x1; x++) s += m[row + x]; }
    return s;
  }

  function balance(gray, w, h) {
    var n = w * h, k, c127 = 0, lo = 0, hi = 0;
    for (k = 0; k < n; k++) { var v = gray[k]; if (v < 128) lo++; if (v >= 127) hi++; }
    var im = new Uint8Array(n);
    if (lo <= hi) { for (k = 0; k < n; k++) im[k] = 255 - gray[k]; } else { im.set(gray); }
    var nall = 0; for (k = 0; k < n; k++) nall += im[k];
    if (nall === 0) nall = 1;
    var pct = function (a, b) { return Math.abs(a - b) / nall * 100; };
    var io = function (a, b) { return Math.abs((nall - (a + b)) - (a + b)) / nall * 100; };
    var w2 = Math.floor(w / 2), w4 = Math.floor(w / 4), h2 = Math.floor(h / 2), h4 = Math.floor(h / 4);
    var bh = pct(rectSum(im, w, 0, h, 0, w2), rectSum(im, w, 0, h, w - w2, w));
    var bioh = io(rectSum(im, w, 0, h, 0, w4), rectSum(im, w, 0, h, w - w4, w));
    var bv = pct(rectSum(im, w, 0, h2, 0, w), rectSum(im, w, h - h2, h, 0, w));
    var biov = io(rectSum(im, w, 0, h4, 0, w), rectSum(im, w, h - h4, h, 0, w));
    var bmd = pct(triSum(im, h, w, 1, true), triSum(im, h, w, -1, false));
    var prop = 1 / Math.sqrt(2);
    var b1 = h - Math.floor(h * prop), b2 = w - Math.floor(w * prop);
    var biomd = io(triSum(im, h, w, -b1, false), triSum(im, h, w, b2, true));
    var r = rot90(im, h, w), rh = w, rw = h;
    var bad = pct(triSum(r, rh, rw, 1, true), triSum(r, rh, rw, -1, false));
    var bioad = io(triSum(r, rh, rw, -b2, false), triSum(r, rh, rw, b1, true));
    return (bh + bv + bioh + biov + bmd + biomd + bad + bioad) / 8;
  }

  function dcm(gray, w, h) {
    var n = w * h, k, lo = 0;
    for (k = 0; k < n; k++) if (gray[k] < 128) lo++;
    var inv = lo <= n - lo, nall = 0, rx = 0, ry = 0;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      var v = gray[y * w + x]; if (inv) v = 255 - v;
      nall += v; rx += v * x; ry += v * y;
    }
    if (nall === 0) return NaN;
    var hn = 0.5 - (roundHalfEven(rx / nall) + 1) / w, vn = 0.5 - (roundHalfEven(ry / nall) + 1) / h;
    return Math.sqrt(hn * hn + vn * vn) / 0.5 * 100;
  }

  function mirrorSymmetry(gray, w, h) {
    var n = w * h, level = otsu(gray, n), bw = new Uint8Array(n), k, i, j, sym, n1;
    for (k = 0; k < n; k++) bw[k] = gray[k] <= level ? 1 : 0;
    var h2 = Math.floor(h / 2), w2 = Math.floor(w / 2);
    n1 = h2 - 1; sym = 0;
    for (i = 0; i < w; i++) for (j = 0; j < h2; j++) sym += bw[j * w + i] * bw[(h - 1 - j) * w + i] * (1 + j / n1);
    var Sh = sym * (2 / (3 * w * h2));
    n1 = w2 - 1; sym = 0;
    for (i = 0; i < h; i++) for (j = 0; j < w2; j++) sym += bw[i * w + j] * bw[i * w + (w - 1 - j)] * (1 + j / n1);
    var Sv = sym * (2 / (3 * h * w2));
    if (w !== h) return (Sh + Sv) / 2 * 100;
    var diag = function (m) {
      var s = 0, nn = 1;
      for (var a = 1; a < h; a++) { for (var b = 0; b < nn; b++) s += m[a * w + b] * m[b * w + a] * (1 + (b + 1) / nn); nn++; }
      return s * (2 / (3 * h * (w - 1) / 2));
    };
    var Smd = diag(bw), Sad = diag(rot90(bw, h, w));
    return (Sh + Sv + Smd + Sad) / 4 * 100;
  }

  function homogeneity(gray, w, h) {
    var n = w * h, k, lo = 0, hi = 0, B = 10;
    for (k = 0; k < n; k++) { var v = gray[k]; if (v < 128) lo++; if (v >= 127) hi++; }
    var im = new Uint8Array(n);
    if (lo <= hi) { for (k = 0; k < n; k++) im[k] = 255 - gray[k]; } else { im.set(gray); }
    var level = otsu(im, n), hinc = Math.floor(w / B), vinc = Math.floor(h / B);
    var cols = new Float64Array(B), rows = new Float64Array(B), all = 0;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      if (im[y * w + x] > level) {
        cols[Math.min(B - 1, Math.floor(x / hinc))]++; rows[Math.min(B - 1, Math.floor(y / vinc))]++; all++;
      }
    }
    var ent = function (a) {
      var e = 0; for (var q = 0; q < B; q++) { var p = a[q] / all; if (p > 0) e -= p * Math.log2(p); }
      return e / Math.log2(B) * 100;
    };
    return all === 0 ? NaN : (ent(cols) + ent(rows)) / 2;
  }

  function compute(rgba, w, h) {
    var n = w * h, L = new Float64Array(n), H = new Float64Array(n), gray = new Uint8Array(n);
    var sL = 0, sA = 0, sB = 0, sS = 0, sV = 0, maxL = 0, maxH = 0, k, p;
    var sS2 = 0;
    for (k = 0, p = 0; k < n; k++, p += 4) {
      var r = rgba[p], g = rgba[p + 1], b = rgba[p + 2];
      gray[k] = (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16;
      var R = LIN[r], G = LIN[g], Bl = LIN[b];
      var fx = fLab((R * 0.412453 + G * 0.357580 + Bl * 0.180423) / 0.95047);
      var fy = fLab(R * 0.212671 + G * 0.715160 + Bl * 0.072169);
      var fz = fLab((R * 0.019334 + G * 0.119193 + Bl * 0.950227) / 1.08883);
      var l = 116 * fy - 16;
      L[k] = l; sL += l; sA += 500 * (fx - fy); sB += 200 * (fy - fz); if (l > maxL) maxL = l;
      var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn, hh = 0;
      if (d > 0) {
        if (b === mx) hh = 4 + (r - g) / d; else if (g === mx) hh = 2 + (b - r) / d; else hh = (g - b) / d;
        hh = ((hh / 6) % 1 + 1) % 1;
      }
      H[k] = hh; if (hh > maxH) maxH = hh;
      var s = mx === 0 ? 0 : d / mx; sS += s; sS2 += s * s; sV += mx / 255;
    }
    var mL = sL / n, vL = 0;
    for (k = 0; k < n; k++) { var dl = L[k] - mL; vL += dl * dl; }
    return {
      rms_contrast: Math.sqrt(vL / n),
      lightness_entropy: entropyOf(L, maxL),
      color_entropy: entropyOf(H, maxH),
      mean_L: mL, mean_a: sA / n, mean_b: sB / n,
      mean_S: sS / n, mean_V: sV / n,
      balance: balance(gray, w, h),
      dcm: dcm(gray, w, h),
      mirror_symmetry: mirrorSymmetry(gray, w, h),
      homogeneity: homogeneity(gray, w, h)
    };
  }
  return { compute: compute };
})();
if (typeof module !== "undefined") module.exports = QIP;
