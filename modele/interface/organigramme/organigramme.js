// Organigramme des pivots (feuille de route, étape 8). Toutes les probabilités sont recalculées dans la page à partir
// des trajectoires du moteur et de leurs poids (data/organigramme_v0.json, scripts/organigramme.py). Le mode « et si »
// multiplie ces poids par la vraisemblance des faits supposés : même calcul que le moteur de preuve (scripts/preuves.py).
(async () => {
const D = window.__DONNEES__ || await (await fetch("data/organigramme_v0.json", {cache: "no-store"})).json();
const P = D.pivots, V = D.variables, J = D.jalons, N = D.codes.length, NM = D.mois.length;
const IX = Object.fromEntries(P.map((p, i) => [p.id, i])), VX = Object.fromEntries(V.map((v, i) => [v.id, i]));
const ET = P.map((p, i) => Uint8Array.from(D.codes, c => +c[i]));
const VT = V.map((v, j) => Array.from({length: NM}, (_, m) => Uint8Array.from(D.variables_codes, c => +c[j * NM + m])));
const W0 = Float64Array.from(D.poids);
const MOISL = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const pc = x => x == null ? "–" : (x > 0 && x < 1 ? "< 1" : Math.round(x)) + " %";
const MIN_CAS = 60;   // trajectoires effectives minimales pour chiffrer un cas

// --- Poids : preuves notées (W0) × faits supposés ---------------------------------------------------------------
let faits = [];
function facteurs(f) {
  if (f.type === "pivot") return P[IX[f.id]].issues.map((_, k) => k === f.issue ? 1 : 0);
  const j = J.find(x => x.id === f.id);
  const L = f.statut === "observé" ? j.L : j.L.map(x => 1 - x);
  return (f.statut === "observé" && j.classe === "tranche") ? L : L.map(x => Math.pow(Math.max(x, 0), D.k));
}
function poids(fs) {
  const w = W0.slice();
  for (const f of fs) {
    const i = IX[f.type === "pivot" ? f.id : J.find(x => x.id === f.id).noeud], fac = facteurs(f), e = ET[i];
    for (let t = 0; t < N; t++) w[t] *= fac[e[t]];
  }
  return w;
}
function ess(w) { let s = 0, s2 = 0; for (const x of w) { s += x; s2 += x * x } return s2 > 0 ? s * s / s2 : 0 }
function marg(i, w) {
  const a = new Float64Array(P[i].issues.length); let s = 0;
  for (let t = 0; t < N; t++) { a[ET[i][t]] += w[t]; s += w[t] }
  return Array.from(a, x => s > 0 ? 100 * x / s : 0);
}
// P(issue k de c | cas), cas = trajectoires où le parent a vaut s (pivot) ou la variable v vaut s au mois m.
function sachant(c, k, filtre, w) {
  let s = 0, s2 = 0, num = 0, tot = 0;
  for (let t = 0; t < N; t++) { tot += w[t]; if (!filtre(t)) continue; s += w[t]; s2 += w[t] * w[t]; if (ET[c][t] === k) num += w[t] }
  return {p: s > 0 ? 100 * num / s : null, pr: tot > 0 ? 100 * s / tot : 0, neff: s2 > 0 ? s * s / s2 : 0};
}
function vdist(j, m, w) {
  const a = new Float64Array(V[j].etats.length); let s = 0;
  for (let t = 0; t < N; t++) { a[VT[j][m][t]] += w[t]; s += w[t] }
  return Array.from(a, x => s > 0 ? 100 * x / s : 0);
}

// --- Modèle affiché pour un jeu de poids ------------------------------------------------------------------------
function modele(w) {
  const MG = P.map((_, i) => marg(i, w));
  return {w, MG, VD: V.map((_, j) => Array.from({length: NM}, (_, m) => vdist(j, m, w))), ess: ess(w)};
}
const BASE = modele(poids([]));
let M = BASE;
const affiche = (i, mg) => P[i].k != null ? P[i].k : mg.indexOf(Math.max(...mg));
function effets(i, m) {
  const p = P[i], out = [];
  const cible = p.k != null ? p.k : affiche(i, m.MG[i]);
  for (const x of p.parents) {
    let cas = [], facteur;
    if (x.id in IX) {
      const a = IX[x.id];
      facteur = P[a].titre;
      P[a].issues.forEach((_, s) => { const r = sachant(i, cible, t => ET[a][t] === s, m.w); if (r.neff >= MIN_CAS) cas.push({si: P[a].phrases[s], ...r}) });
      if (P[a].k != null) cas.sort((u, v) => (u.si !== P[a].phrases[P[a].k]) - (v.si !== P[a].phrases[P[a].k])); else cas.sort((u, v) => v.pr - u.pr);
      cas = cas.slice(0, 5);
    } else if (x.id in VX) {
      const j = VX[x.id], mm = Math.max(0, Math.min(NM - 1, p.mois - x.decalage));
      facteur = `${V[j].titre} (${MOISL[+D.mois[mm].slice(5, 7) - 1]} ${D.mois[mm].slice(0, 4)})`;
      V[j].etats.forEach((e, s) => { const r = sachant(i, cible, t => VT[j][mm][t] === s, m.w); if (r.neff >= MIN_CAS) cas.push({si: "Si " + V[j].si + e, ...r}) });
      if (cas.length < 2) continue;
    } else continue;
    const vs = cas.map(c => c.p);
    out.push({de: x.id, facteur, cible: p.k != null ? null : p.libelles[cible], cas, couvert: cas.reduce((s, c) => s + c.pr, 0),
              ecart: vs.length > 1 ? Math.max(...vs) - Math.min(...vs) : 0});
  }
  return out;
}

// --- Rendu -------------------------------------------------------------------------------------------------------
// Écart affiché à partir de 2 points : en dessous, c'est l'ordre du bruit de la repondération.
const delta = (a, b) => { const d = Math.round(b) - Math.round(a); return Math.abs(d) >= 2 ? `<span class="av ${d > 0 ? "up" : "down"}">avant ${pc(a)}</span>` : "" };
function tete(i) {
  const p = P[i], mg = M.MG[i], b = BASE.MG[i], h = M !== BASE;
  if (p.k != null) return `<div class="gros"><b>${pc(mg[p.k])}</b><div class="barre"><i style="width:${mg[p.k]}%"></i></div></div>${h ? `<div class="reste">${delta(b[p.k], mg[p.k])}</div>` : ""}`;
  const ord = mg.map((v, k) => [k, v]).sort((u, v) => v[1] - u[1]), top = ord.filter(x => x[1] >= 3).slice(0, 3);
  const reste = 100 - top.reduce((s, x) => s + x[1], 0);
  return `<div class="iss">${top.map(([k, v]) => `<span>${esc(p.libelles[k])}${h ? delta(b[k], v) : ""}</span><div class="barre"><i style="width:${v}%"></i></div><b>${pc(v)}</b>`).join("")}</div>${reste >= 1 ? `<div class="reste">autres : ${pc(reste)}</div>` : ""}`;
}
function carte(i) {
  const p = P[i], nj = J.filter(j => j.noeud === p.id).length, nf = p.parents.length;
  return `<div class="c"><div class="quand">${esc(p.quand)}</div><div class="titre">${esc(p.titre)}</div>${tete(i)}
  <div class="pied">${nf ? `${nf} facteur${nf > 1 ? "s" : ""}` : ""}${nf && nj ? " · " : ""}${nj ? `${nj} jalon${nj > 1 ? "s" : ""}` : ""}<span>détail ›</span></div></div>`;
}
const TV = [.28, .6, 1];
function spark(j, w, h, axes, dist) {
  const v = V[j], k = NM, bw = w / k; let s = `<svg class="spark" width="${w}" height="${h + (axes ? 16 : 0)}" viewBox="0 0 ${w} ${h + (axes ? 16 : 0)}">`;
  dist.forEach((d, m) => { let y = 0; d.forEach((x, e) => { const hh = h * x / 100; s += `<rect x="${m * bw + .5}" y="${y}" width="${bw - 1}" height="${hh}" fill="var(--t-variable)" opacity="${TV[e]}"><title>${esc(D.mois[m])} : ${esc(v.etats[e])} ${Math.round(x)} %</title></rect>`; y += hh }) });
  if (axes) [0, 3, 6, 9, 12, 15, 18, 21].forEach(m => { const [a, mm] = D.mois[m].split("-"); s += `<text x="${m * bw}" y="${h + 12}" font-size="10" fill="var(--muted)">${MOISL[+mm - 1]}${mm === "01" || m === 0 ? " " + a.slice(2) : ""}</text>` });
  return s + "</svg>";
}
const legende = j => `<div class="le">${V[j].etats.map((e, i) => `<span><i style="opacity:${TV[i]}"></i>${esc(e)}</span>`).join("")}</div>`;
function carteVariable(j) {
  const v = V[j], o = v.observe;
  return `<div class="c"><div class="quand">variable suivie chaque mois</div><div class="titre">${esc(v.titre)}</div>
  <div class="obs1">${o ? `observé : <b>${esc(o[1])}</b> (${esc(o[0])})` : "non observé"}</div>${spark(j, 236, 30, false, M.VD[j])}${legende(j)}
  <div class="pied">${v.questions.length ? `${v.questions.length} question${v.questions.length > 1 ? "s" : ""}` : ""}<span>détail ›</span></div></div>`;
}
const estSuppose = f => faits.some(x => x.type === f.type && x.id === f.id && (x.issue === f.issue) && (x.statut === f.statut));
const bouton = (f, lib) => `<button class="suppose ${estSuppose(f) ? "actif" : ""}" data-f='${esc(JSON.stringify(f))}'>${estSuppose(f) ? "supposé" : lib}</button>`;
function jalonHtml(j) {
  const i = IX[j.noeud], mg = M.MG[i], pobs = mg.reduce((s, x, k) => s + x * j.L[k], 0);
  const w2 = poids([...faits.filter(f => !(f.type === "jalon" && f.id === j.id)), {type: "jalon", id: j.id, statut: "observé"}]), e2 = ess(w2);
  let opts = "", cons = "";
  if (e2 >= D.seuil_ess * N) {
    const MG2 = P.map((_, c) => marg(c, w2)), lignes = [];
    P.forEach((p, c) => {
      const ks = p.k != null ? [p.k] : M.MG[c].map((v, k) => [k, v]).sort((u, v) => v[1] - u[1]).slice(0, 3).map(x => x[0]);
      ks.forEach(k => { const a = M.MG[c][k], b = MG2[c][k]; if (Math.abs(b - a) >= 3) lignes.push([c === i ? 0 : 1, p.court + (p.k != null ? "" : " : " + p.libelles[k]), a, b]) });
    });
    lignes.sort((u, v) => u[0] - v[0] || Math.abs(v[3] - v[2]) - Math.abs(u[3] - u[2]));
    const row = ([_, l, a, b]) => { const d = Math.round(b) - Math.round(a); return `<div class="or"><span>${esc(l)}</span><span>${pc(a)}</span><span class="b2"><i style="width:${b}%"></i><b>${pc(b)}</b></span><span class="dd ${d ? "up" : ""}">${d > 0 ? "+" : d < 0 ? "−" : ""}${d ? Math.abs(d) + " pts" : "="}</span></div>` };
    const ici = lignes.filter(x => x[0] === 0), aval = lignes.filter(x => x[0] === 1).slice(0, 8);
    if (ici.length) opts = `<div class="opt"><div class="oh"><span>s'il survient</span><span>aujourd'hui</span><span>après</span><span></span></div>${ici.map(row).join("")}</div>`;
    if (aval.length) cons = `<div class="opt"><div class="oh"><span>et dans tout le réseau</span><span>aujourd'hui</span><span>après</span><span></span></div>${aval.map(row).join("")}</div>`;
  } else opts = `<p class="note">Combinaison trop rare pour être chiffrée avec les faits déjà supposés.</p>`;
  const eq = j.etat_reseau != null ? `<p class="eq">Ce fait équivaut à « ${esc(P[i].libelles[j.etat_reseau])} » dans le réseau.</p>` : "";
  return `<li><i class="pt ${j.niveau === 2 ? "n2" : ""} ${esc(j.statut)}"></i><div><div class="jt"><b>${esc(j.lib)}<span class="classe">${j.classe === "tranche" ? "tranche" : "indice"}</span></b><span class="pills"><span class="pill">probable à ${pc(pobs)}</span></span></div><p class="quand2">${esc(j.quand)} ${bouton({type: "jalon", id: j.id, statut: "observé"}, "supposer observé")}${bouton({type: "jalon", id: j.id, statut: "manqué"}, "supposer manqué")}</p>${eq}${opts}${cons}<p class="obs">${esc(j.observable)}</p></div></li>`;
}
function corps(i) {
  const p = P[i], mg = M.MG[i];
  const issues = `<div class="sec"><div class="h">Issues</div><table class="iss2">${p.issues.map((_, k) => `<tr><td>${esc(p.libelles[k])}</td><td class="nb">${pc(mg[k])}${M !== BASE ? delta(BASE.MG[i][k], mg[k]) : ""}</td><td class="nb">${bouton({type: "pivot", id: p.id, issue: k}, "supposer")}</td></tr>`).join("")}</table></div>`;
  const effs = effets(i, M).sort((u, v) => v.ecart - u.ecart), e0 = effs[0];
  const FIA = {bon: "bon : les évaluateurs donnaient des valeurs proches", moyen: "moyen : les évaluateurs divergeaient sensiblement", faible: "faible : les évaluateurs donnaient des valeurs très différentes"};
  let dec = "";
  if (!e0) dec = `<p>Aucune cause chiffrable dans le réseau : la probabilité vient directement des tables des évaluateurs.</p>`;
  else {
    const cible = p.k != null ? p.k : affiche(i, mg), tot0 = mg[cible];
    let tot = 0;
    const rows = e0.cas.map(c => { const ct = c.pr * c.p / 100; tot += ct; return `<tr><td>${esc(c.si)}</td><td class="nb">${pc(c.pr)}</td><td class="nb"><span class="mb"><i style="width:${c.p}%"></i></span>${pc(c.p)}</td><td class="nb">${Math.round(ct)} pts</td></tr>` }).join("");
    const reste = 100 - e0.couvert;
    dec = `<table class="dec"><thead><tr><th>Cas : ${esc(e0.facteur)}</th><th>Proba. du cas</th><th>« ${esc(p.k != null ? p.court : p.libelles[cible])} » dans ce cas</th><th>Contribution</th></tr></thead><tbody>${rows}${reste >= 1 ? `<tr class="muted"><td>Autres cas, trop rares pour être chiffrés</td><td class="nb">${pc(reste)}</td><td></td><td class="nb">${Math.round(tot0 - tot)} pts</td></tr>` : ""}<tr class="tot"><td colspan="3">Total : probabilité de « ${esc(p.k != null ? p.court : p.libelles[cible])} »</td><td class="nb">${pc(tot0)}</td></tr></tbody></table>`;
  }
  const autres = effs.slice(1).map(e => { const vs = e.cas.map(c => c.p), lo = Math.min(...vs), hi = Math.max(...vs), cmin = e.cas.find(c => c.p === lo), cmax = e.cas.find(c => c.p === hi);
    return `<li><b>${esc(e.facteur)}</b>${e.cible ? ` (sur « ${esc(e.cible)} »)` : ""} : ${hi - lo < 3 ? "effet négligeable" : `de ${pc(lo)} (${esc(cmin.si.replace(/^Si /, "si "))}) à ${pc(hi)} (${esc(cmax.si.replace(/^Si /, "si "))})`}</li>` }).join("");
  const ctx = p.ctx.length ? `<li>Pris en compte sans chiffrage ici : ${esc(p.ctx.join(", "))}.</li>` : "";
  const js = J.filter(j => j.noeud === p.id).sort((a, b) => a.debut < b.debut ? -1 : 1);
  return `${issues}<div class="sec"><div class="h">D'où vient ce chiffre</div>${dec}${autres || ctx ? `<div class="h" style="margin-top:12px">Autres facteurs</div><ul class="af">${autres}${ctx}</ul>` : ""}<p class="fia fia-${p.fiabilite}">Fiabilité des paramètres : ${FIA[p.fiabilite]}.</p></div>${js.length ? `<div class="sec js"><div class="h">Jalons à surveiller</div><ul>${js.map(jalonHtml).join("")}</ul></div>` : ""}`;
}
function corpsVariable(j) {
  const v = V[j];
  const qs = v.questions.length ? `<div class="sec"><div class="h">Questions notées qui en dépendent</div>${v.questions.map(q => `<div class="qv"><span>${esc(q.texte)}</span><span class="pills"><span class="pill">réseau ${pc(q.reseau)}</span><span class="pill">ensemble ${pc(q.ensemble)}</span></span></div>`).join("")}</div>` : "";
  const agit = P.filter(p => p.parents.some(x => x.id === v.id)).map(p => p.court).concat(V.filter(u => u.parents.includes(v.id)).map(u => u.titre.toLowerCase()));
  return `<div class="sec"><div class="h">Liens</div><p>Agit sur : ${esc(agit.join(", ") || "aucun pivot directement")}.</p><p>Évolue avec : ${esc(v.parents.map(x => (P[IX[x]] || V[VX[x]] || {}).court || (V[VX[x]] || {}).titre || x).join(", ") || "rien dans le réseau")}.</p></div><div class="sec"><div class="h">Projection mois par mois</div>${spark(j, 560, 60, true, M.VD[j])}${legende(j)}${v.definition ? `<p class="note">${esc(v.definition)}</p>` : ""}</div>${qs}`;
}

// --- Organigramme ------------------------------------------------------------------------------------------------
const org = document.getElementById("org");
const ids = P.map(p => p.id).concat(V.map(v => v.id));
org.innerHTML = P.map((p, i) => `<div class="n pv" id="${p.id}" style="--th:var(--t-${p.theme})" tabindex="0" role="button" aria-label="${esc(p.titre)} : détail">${carte(i)}</div>`).join("")
  + V.map((v, j) => `<div class="n pv va" id="${v.id}" style="--th:var(--t-variable)" tabindex="0" role="button" aria-label="${esc(v.titre)} : détail">${carteVariable(j)}</div>`).join("");
const liens = [];
P.forEach((p, c) => p.parents.forEach(x => {
  if (x.id in IX) { const ef = effets(c, BASE).find(e => e.de === x.id); const vs = ef ? ef.cas.map(u => u.p) : []; const d = vs.length > 1 ? Math.max(...vs) - Math.min(...vs) : 0;
    liens.push({de: x.id, vers: p.id, fort: d >= 10}) }
  else if (x.id in VX) { const ef = effets(c, BASE).find(e => e.de === x.id); const vs = ef ? ef.cas.map(u => u.p) : [];
    liens.push({de: x.id, vers: p.id, fort: vs.length > 1 && Math.max(...vs) - Math.min(...vs) >= 10, variable: true}) }
}));
V.forEach(v => v.parents.forEach(x => liens.push({de: x, vers: v.id, fort: false, variable: true})));
const taille = id => { const e = document.getElementById(id); return {width: e.offsetWidth, height: e.offsetHeight} };
const graph = {id: "racine", layoutOptions: {"elk.algorithm": "layered", "elk.direction": "RIGHT", "elk.edgeRouting": "ORTHOGONAL",
  "elk.spacing.nodeNode": "18", "elk.layered.spacing.nodeNodeBetweenLayers": "78", "elk.separateConnectedComponents": "false", "elk.aspectRatio": "3", "elk.spacing.edgeNode": "28", "elk.spacing.edgeEdge": "14",
  "elk.layered.spacing.edgeNodeBetweenLayers": "26", "elk.layered.spacing.edgeEdgeBetweenLayers": "12", "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX", "elk.layered.layering.strategy": "LONGEST_PATH_SOURCE",
  "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES", "elk.layered.thoroughness": "30", "elk.layered.mergeEdges": "false"},
  children: ids.map(id => ({id, ...taille(id)})), edges: liens.map((l, k) => ({id: "e" + k, sources: [l.de], targets: [l.vers]}))};
const r = await new ELK().layout(graph);
r.children.forEach(c => { const e = document.getElementById(c.id); e.style.left = c.x + "px"; e.style.top = c.y + "px" });
org.style.width = r.width + "px"; org.style.height = r.height + "px";
const ajuster = () => { const cadre = document.getElementById("cadre"), dispo = innerHeight - cadre.getBoundingClientRect().top - window.scrollY - 28, h = r.height + 32, k = Math.min(1, Math.max(.6, dispo / h));
  org.style.transform = `scale(${k})`; cadre.style.width = (r.width + 32) * k + "px"; cadre.style.height = h * k + "px" };
ajuster(); addEventListener("resize", ajuster);
let svg = `<svg width="${r.width}" height="${r.height}"><defs>${["f", "fa"].map((m, k) => `<marker id="${m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="${k ? "var(--accent)" : "var(--line-strong)"}"/></marker>`).join("")}</defs>`;
r.edges.forEach((e, k) => { const l = liens[k]; (e.sections || []).forEach(sec => { const pts = [sec.startPoint, ...(sec.bendPoints || []), sec.endPoint];
  svg += `<path d="M${pts.map(p => p.x + " " + p.y).join(" L")}" fill="none" stroke="${l.fort ? "var(--accent)" : "var(--line-strong)"}" stroke-width="${l.fort ? 2.4 : 1.4}" stroke-linejoin="round" ${l.variable ? 'stroke-dasharray="5 4" opacity=".75"' : ""} marker-end="url(#${l.fort ? "fa" : "f"})"/>` }) });
org.insertAdjacentHTML("afterbegin", svg + "</svg>");

// --- Interactions ------------------------------------------------------------------------------------------------
const dlg = document.getElementById("dlg"), dc = document.getElementById("dc");
let ouvert = null;
document.getElementById("x").onclick = () => dlg.close();
dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close() });
dlg.addEventListener("close", () => { ouvert = null });
function ouvrir(id) {
  ouvert = id;
  if (id in IX) { const i = IX[id], p = P[i]; dc.innerHTML = `<div class="pv dl" style="--th:var(--t-${p.theme})"><div class="c"><div class="quand">${esc(p.quand)}</div><div class="titre">${esc(p.titre)}</div>${tete(i)}</div>${corps(i)}</div>` }
  else { const j = VX[id], v = V[j]; dc.innerHTML = `<div class="pv dl" style="--th:var(--t-variable)"><div class="c"><div class="quand">variable suivie chaque mois</div><div class="titre">${esc(v.titre)}</div><div class="obs1">${v.observe ? `observé : <b>${esc(v.observe[1])}</b> (${esc(v.observe[0])})` : ""}</div></div>${corpsVariable(j)}</div>` }
  if (!dlg.open) { dlg.showModal(); dlg.scrollTop = 0 }
}
function libFait(f) {
  if (f.type === "pivot") { const p = P[IX[f.id]]; return `${p.court} : ${p.libelles[f.issue]}` }
  const j = J.find(x => x.id === f.id); return `${j.lib} (${f.statut})`;
}
function rafraichir() {
  M = faits.length ? modele(poids(faits)) : BASE;
  const rare = M.ess < D.seuil_ess * N;
  const b = document.getElementById("etsi");
  b.classList.toggle("on", faits.length > 0);
  b.innerHTML = faits.length ? `<span class="t">Et si :</span>${faits.map((f, k) => `<span class="f">${esc(libFait(f))}<button data-k="${k}" aria-label="Retirer">×</button></span>`).join("")}<button class="raz" id="raz">tout retirer</button><span class="ess">${Math.round(M.ess)} trajectoires effectives sur ${N}</span>${rare ? `<span class="rare">Combinaison trop rare pour être estimée : chiffres non fiables.</span>` : ""}` : "";
  P.forEach((_, i) => { document.getElementById(P[i].id).innerHTML = carte(i) });
  V.forEach((_, j) => { document.getElementById(V[j].id).innerHTML = carteVariable(j) });
  if (ouvert) ouvrir(ouvert);
}
document.body.addEventListener("click", e => {
  const s = e.target.closest(".suppose");
  if (s) { const f = JSON.parse(s.dataset.f);
    if (estSuppose(f)) faits = faits.filter(x => !(x.type === f.type && x.id === f.id && x.issue === f.issue && x.statut === f.statut));
    else { faits = faits.filter(x => !(x.type === f.type && x.id === f.id)); faits.push(f) }
    rafraichir(); return }
  const x = e.target.closest(".etsi .f button"); if (x) { faits.splice(+x.dataset.k, 1); rafraichir(); return }
  if (e.target.id === "raz") { faits = []; rafraichir(); return }
  const n = e.target.closest(".n.pv"); if (n) ouvrir(n.id);
});
document.querySelectorAll(".n.pv").forEach(e => { e.onkeydown = k => { if (k.key === "Enter" || k.key === " ") { k.preventDefault(); ouvrir(e.id) } } });
const bh = document.getElementById("hors");
bh.textContent = `${D.hors.length} questions suivies hors réseau ›`;
bh.onclick = () => { ouvert = null; dc.innerHTML = `<div class="pv dl" style="--th:var(--muted)"><div class="c"><div class="titre">Questions suivies hors réseau</div><p class="note">Prévues par l'ensemble de prévisionnistes et notées, mais aucun pivot ni aucune variable du réseau ne les porte encore.</p></div><div class="sec"><ul class="hl">${D.hors.map(h => `<li><b>${esc(h.id)}</b> ${esc(h.nom)}</li>`).join("")}</ul></div></div>`; dlg.showModal() };
const bp = document.getElementById("hyp");
bp.textContent = `${D.hypotheses.length} hypothèses porteuses ›`;
bp.onclick = () => { ouvert = null; dc.innerHTML = `<div class="pv dl" style="--th:var(--muted)"><div class="c"><div class="titre">Hypothèses porteuses</div><p class="note">Ce que le réseau suppose sans le représenter, ou en partie. Probabilité de rupture tirée de précédents ; une alerte de la veille déclenche un examen, jamais un changement de probabilité.</p></div><div class="sec">${D.hypotheses.map(h => `<p><b>${esc(h.id)}</b> ${esc(h.enonce)} <span class="pill">rupture ${pc(100 * h.rupture)}</span></p><p class="note">${esc(h.traitement)}</p>`).join("")}</div></div>`; dlg.showModal() };
document.getElementById("meta").textContent = `${N} trajectoires du moteur ; ${D.version_tables}. Calculé le ${D.etabli_le}.`;
document.body.dataset.pret = "1";
})();
