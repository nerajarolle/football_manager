const TEAM_NAMES = [
  "London FC",
  "Manchester United",
  "Madrid Whites",
  "Catalonia Blaugrana",
  "Bavaria Munich",
  "Parisian Club",
  "Turin Old Lady",
  "Milan Red",
];

const FIRST_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth"];
const LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"];
const POSITIONS = ["GK", "DEF", "MID", "ATT"];
const SAVE_KEY = "football-manager-static-save";

const app = document.querySelector("#app");
let state = loadState();

function randomItem(items) { return items[Math.floor(Math.random() * items.length)]; }
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function money(value) { return `€${Math.round(value).toLocaleString("en-US")}`; }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char])); }

function makePlayer(position) {
  const player = {
    id: crypto.randomUUID(),
    name: `${randomItem(FIRST_NAMES)} ${randomItem(LAST_NAMES)}`,
    position,
    att: randomInt(position === "ATT" ? 65 : 35, position === "ATT" ? 92 : 80),
    mid: randomInt(position === "MID" ? 65 : 35, position === "MID" ? 92 : 80),
    dfn: randomInt(["DEF", "GK"].includes(position) ? 65 : 35, ["DEF", "GK"].includes(position) ? 92 : 80),
    value: randomInt(8, 28) * 100000,
    goals: 0,
  };
  player.overall = Math.round((player.att + player.mid + player.dfn) / 3);
  return player;
}

function makeTeam(name, isUser = false) {
  const players = ["GK", "GK", "GK", "DEF", "DEF", "DEF", "DEF", "DEF", "DEF", "MID", "MID", "MID", "MID", "MID", "MID", "ATT", "ATT", "ATT", "ATT"].map(makePlayer);
  return { name, isUser, budget: isUser ? 25000000 : randomInt(20, 60) * 1000000, players, played: 0, wins: 0, draws: 0, losses: 0, goalsFor: 0, goalsAgainst: 0, points: 0 };
}

function teamOverall(team) {
  const average = (position) => {
    const values = team.players.filter((player) => player.position === position).map((player) => player.overall);
    return values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : 50;
  };
  return Math.round((average("ATT") + average("MID") + average("DEF") + average("GK")) / 4);
}

function makeFixtures(teamNames) {
  const fixtures = [];
  const rotating = [...teamNames];
  for (let round = 0; round < rotating.length - 1; round += 1) {
    for (let index = 0; index < rotating.length / 2; index += 1) {
      const home = rotating[index];
      const away = rotating[rotating.length - 1 - index];
      fixtures.push({ id: crypto.randomUUID(), round, home, away, homeScore: 0, awayScore: 0, played: false, scorers: [] });
    }
    rotating.splice(1, 0, rotating.pop());
  }
  const firstHalf = fixtures.map((fixture) => ({ ...fixture, id: crypto.randomUUID(), round: fixture.round + 7, home: fixture.away, away: fixture.home, homeScore: 0, awayScore: 0, played: false, scorers: [] }));
  return fixtures.concat(firstHalf);
}

function newGame(managerName, teamName) {
  const teams = {};
  const names = [teamName, ...TEAM_NAMES.filter((name) => name !== teamName)];
  names.forEach((name, index) => { teams[name] = makeTeam(name, index === 0); });
  return { managerName, teamName, teams, fixtures: makeFixtures(names), round: 0, market: Array.from({ length: 10 }, () => makePlayer(randomItem(POSITIONS))), activeTab: "squad" };
}

function loadState() {
  try { return JSON.parse(localStorage.getItem(SAVE_KEY)) || null; } catch { return null; }
}
function saveState() { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); }
function userTeam() { return state.teams[state.teamName]; }
function currentFixtures() { return state.fixtures.filter((fixture) => fixture.round === state.round); }
function notify(message, tone = "good") {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.dataset.tone = tone;
  toast.hidden = false;
  window.setTimeout(() => { toast.hidden = true; }, 2600);
}

function render() {
  if (!state) return renderStart();
  renderGame();
}

function renderStart() {
  app.innerHTML = `
    <main class="start-screen">
      <section class="start-copy">
        <p class="eyebrow">Static edition / GitHub Pages</p>
        <h1>Your club.<br><em>Your call.</em></h1>
        <p class="intro">Build a squad, make the hard calls in the market, and guide a season from the browser. Your career is saved locally on this device.</p>
      </section>
      <section class="start-panel">
        <p class="panel-kicker">New career</p>
        <label>Manager name<input id="manager-name" value="Coach" maxlength="28" /></label>
        <label>Choose your club<select id="team-name">${TEAM_NAMES.map((name) => `<option>${name}</option>`).join("")}</select></label>
        <button class="primary" data-action="start">Start career <span>-></span></button>
        ${loadState() ? '<button class="secondary" data-action="continue">Continue saved game</button>' : ""}
        <p class="fine-print">No account. No server. No transfer window closes unexpectedly.</p>
      </section>
    </main>
    <div id="toast" hidden></div>`;
}

function renderGame() {
  const team = userTeam();
  const tabs = ["squad", "market", "fixtures", "standings"];
  app.innerHTML = `
    <header class="topbar">
      <a class="brand" href="game.html">FM<span>/</span>01</a>
      <div class="manager"><span>${escapeHtml(state.managerName)}</span><strong>${escapeHtml(state.teamName)}</strong></div>
      <div class="header-actions"><span class="budget">${money(team.budget)}</span><button class="ghost" data-action="save">Save</button><button class="ghost" data-action="quit">Quit</button></div>
    </header>
    <main class="game-shell">
      <section class="game-heading"><div><p class="eyebrow">Season ${Math.min(state.round + 1, 14)} / Round ${Math.min(state.round + 1, 14)}</p><h1>${escapeHtml(state.teamName)}</h1></div><button class="primary match-button" data-action="match">${state.round >= 14 ? "Season complete" : "Play next match"}<span>-></span></button></section>
      <nav class="tabs">${tabs.map((tab) => `<button class="tab ${state.activeTab === tab ? "active" : ""}" data-tab="${tab}">${tab}</button>`).join("")}</nav>
      <section class="content">${renderTab()}</section>
    </main><div id="toast" hidden></div>`;
}

function renderTab() {
  if (state.activeTab === "squad") return renderSquad();
  if (state.activeTab === "market") return renderMarket();
  if (state.activeTab === "fixtures") return renderFixtures();
  return renderStandings();
}

function renderSquad() {
  const team = userTeam();
  return `<div class="section-head"><div><p class="eyebrow">The dressing room</p><h2>First team squad</h2></div><div class="ratings"><span>ATT <b>${teamOverall(team)}</b></span><span>MID <b>${teamOverall(team)}</b></span><span>DEF <b>${teamOverall(team)}</b></span></div></div><div class="table-wrap"><table><thead><tr><th>Player</th><th>Pos</th><th>ATT</th><th>MID</th><th>DEF</th><th>OVR</th><th>Value</th><th></th></tr></thead><tbody>${team.players.map((player) => `<tr><td><strong>${escapeHtml(player.name)}</strong></td><td><span class="position">${player.position}</span></td><td>${player.att}</td><td>${player.mid}</td><td>${player.dfn}</td><td><strong>${player.overall}</strong></td><td>${money(player.value)}</td><td><button class="small danger" data-action="sell" data-player="${player.id}">Sell</button></td></tr>`).join("")}</tbody></table></div>`;
}

function renderMarket() {
  const players = [...state.market];
  Object.values(state.teams).filter((team) => team.name !== state.teamName).forEach((team) => players.push(...team.players.slice(0, 5).map((player) => ({ ...player, owner: team.name }))));
  return `<div class="section-head"><div><p class="eyebrow">Recruitment</p><h2>Transfer market</h2></div><span class="muted">${players.length} players available</span></div><div class="market-grid">${players.map((player) => `<article class="player-card"><div class="player-top"><span class="position">${player.position}</span><span class="muted">OVR ${player.overall}</span></div><h3>${escapeHtml(player.name)}</h3><p>${player.owner ? escapeHtml(player.owner) : "Free agent"}</p><strong>${money(player.value)}</strong><button class="small primary" data-action="buy" data-player="${player.id}" data-owner="${player.owner || ""}">${player.owner ? "Make offer" : "Buy free"}</button></article>`).join("")}</div>`;
}

function renderFixtures() {
  return `<div class="section-head"><div><p class="eyebrow">The road ahead</p><h2>Fixtures</h2></div></div><div class="fixture-list">${state.fixtures.map((fixture) => `<div class="fixture-row ${fixture.round === state.round ? "next" : ""}"><span>Round ${fixture.round + 1}</span><strong>${escapeHtml(fixture.home)}</strong><b>${fixture.played ? `${fixture.homeScore} - ${fixture.awayScore}` : "vs"}</b><strong>${escapeHtml(fixture.away)}</strong><small>${fixture.played ? "FULL TIME" : fixture.round === state.round ? "NEXT" : "UPCOMING"}</small></div>`).join("")}</div>`;
}

function renderStandings() {
  const teams = Object.values(state.teams).sort((a, b) => b.points - a.points || (b.goalsFor - b.goalsAgainst) - (a.goalsFor - a.goalsAgainst));
  return `<div class="section-head"><div><p class="eyebrow">League table</p><h2>Standings</h2></div></div><div class="table-wrap"><table><thead><tr><th>#</th><th>Club</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>PTS</th></tr></thead><tbody>${teams.map((team, index) => `<tr class="${team.name === state.teamName ? "highlight" : ""}"><td>${index + 1}</td><td><strong>${escapeHtml(team.name)}</strong></td><td>${team.played}</td><td>${team.wins}</td><td>${team.draws}</td><td>${team.losses}</td><td>${team.goalsFor - team.goalsAgainst}</td><td><strong>${team.points}</strong></td></tr>`).join("")}</tbody></table></div>`;
}

function getPlayer(id, ownerName = state.teamName) { return state.teams[ownerName]?.players.find((player) => player.id === id) || state.market.find((player) => player.id === id); }
function simulateFixture(fixture) {
  const home = state.teams[fixture.home];
  const away = state.teams[fixture.away];
  fixture.homeScore = 0; fixture.awayScore = 0; fixture.scorers = [];
  const homeChance = teamOverall(home) / (teamOverall(home) + teamOverall(away));
  for (let minute = 1; minute <= 90; minute += 1) {
    if (Math.random() > 0.955) {
      const isHome = Math.random() < homeChance;
      const scoringTeam = isHome ? home : away;
      const scorer = randomItem(scoringTeam.players.filter((player) => ["ATT", "MID"].includes(player.position)));
      if (isHome) fixture.homeScore += 1; else fixture.awayScore += 1;
      scorer.goals += 1;
      fixture.scorers.push(`${scorer.name} (${minute}')`);
    }
  }
  fixture.played = true;
  [home, away].forEach((team) => { team.played += 1; });
  home.goalsFor += fixture.homeScore; home.goalsAgainst += fixture.awayScore;
  away.goalsFor += fixture.awayScore; away.goalsAgainst += fixture.homeScore;
  if (fixture.homeScore > fixture.awayScore) { home.wins += 1; home.points += 3; away.losses += 1; }
  else if (fixture.awayScore > fixture.homeScore) { away.wins += 1; away.points += 3; home.losses += 1; }
  else { home.draws += 1; away.draws += 1; home.points += 1; away.points += 1; }
}

function playNextMatch() {
  if (state.round >= 14) return notify("The season is complete.", "warn");
  const fixtures = currentFixtures();
  fixtures.forEach(simulateFixture);
  state.round += 1;
  saveState();
  render();
  const userFixture = fixtures.find((fixture) => [fixture.home, fixture.away].includes(state.teamName));
  notify(`${userFixture.home} ${userFixture.homeScore} - ${userFixture.awayScore} ${userFixture.away}`, "good");
}

function sellPlayer(id) {
  const team = userTeam();
  const player = team.players.find((candidate) => candidate.id === id);
  if (!player) return;
  const buyer = randomItem(Object.values(state.teams).filter((candidate) => candidate.name !== state.teamName));
  const price = Math.round(player.value * (0.85 + Math.random() * 0.3));
  team.players = team.players.filter((candidate) => candidate.id !== id);
  team.budget += price;
  buyer.players.push(player);
  saveState(); render(); notify(`${player.name} sold for ${money(price)}.`, "good");
}

function buyPlayer(id, ownerName) {
  const team = userTeam();
  const owner = ownerName ? state.teams[ownerName] : null;
  const player = owner ? owner.players.find((candidate) => candidate.id === id) : state.market.find((candidate) => candidate.id === id);
  if (!player) return;
  const price = owner ? Math.round(player.value * (0.9 + Math.random() * 0.2)) : 0;
  if (owner && team.budget < price) return notify("Your budget cannot cover that offer.", "bad");
  if (owner) owner.players = owner.players.filter((candidate) => candidate.id !== id); else state.market = state.market.filter((candidate) => candidate.id !== id);
  team.players.push(player); team.budget -= price;
  saveState(); render(); notify(`${player.name} joined your squad.`, "good");
}

app.addEventListener("click", (event) => {
  const target = event.target.closest("button, a");
  if (!target) return;
  if (target.dataset.tab) { state.activeTab = target.dataset.tab; render(); return; }
  const action = target.dataset.action;
  if (action === "start") { state = newGame(document.querySelector("#manager-name").value.trim() || "Coach", document.querySelector("#team-name").value); saveState(); render(); }
  if (action === "continue") { state = loadState(); render(); }
  if (action === "save") { saveState(); notify("Career saved on this device.", "good"); }
  if (action === "quit") { state = null; localStorage.removeItem(SAVE_KEY); render(); }
  if (action === "match") playNextMatch();
  if (action === "sell") sellPlayer(target.dataset.player);
  if (action === "buy") buyPlayer(target.dataset.player, target.dataset.owner);
});

render();
