/* ==========================================================================
   ELISE - TEST BOARD KIT
   --------------------------------------------------------------------------
   Everything the two test boards share: the read-only Supabase calls, the
   sandbox merge, the date bar, the clock, and the edit sheet.
   Reads come from the live tables with the anon key. Writes go nowhere near
   the database - they land in the sandbox (sandbox.js) and live in this
   browser only, so the real board cannot be damaged by anything here.
   ========================================================================== */
(function(global){
"use strict";

var CFG  = global.ELISE_CONFIG || {};
var REST = (CFG.url || "").replace(/\/+$/, "") + "/rest/v1/";
var KEY  = CFG.key || "";
var PROJ = "ELISE";

function api(path){
  return fetch(REST + path, {headers:{apikey:KEY, Authorization:"Bearer " + KEY}})
    .then(function(r){ if(!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
}
function esc(s){
  return String(s == null ? "" : s).replace(/[&<>"]/g, function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];
  });
}
function two(n){ return (n < 10 ? "0" : "") + n; }
function hm(m){ return two(Math.floor(m/60)) + ":" + two(((m%60)+60)%60); }
function mins(s){ var p = String(s||"").split(":"); return (+p[0]||0)*60 + (+p[1]||0); }
function iso(d){ return d.getFullYear()+"-"+two(d.getMonth()+1)+"-"+two(d.getDate()); }
function nowMin(){ var n = new Date(); return n.getHours()*60 + n.getMinutes(); }
var ROLLOVER = 990;                       /* 4:30pm, same as the board */
function boardDate(){
  var n = new Date();
  if(n.getHours()*60 + n.getMinutes() >= ROLLOVER) n.setDate(n.getDate() + 1);
  return iso(n);
}
var WD = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
var MN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function asDate(s){ var p = String(s).split("-"); return new Date(+p[0], +p[1]-1, +p[2]); }
function dayName(s){ var d = asDate(s); return WD[d.getDay()] + " " + d.getDate() + " " + MN[d.getMonth()]; }
function shift(s, n){ var d = asDate(s); d.setDate(d.getDate() + n); return iso(d); }

var DEF_TRADES = [["EC","Elise","#A8A05C"],["GLF","G+L Form","#FF8A00"],
  ["ECC","East Coast Concrete","#5A6670"],["EEC","Encon PT","#D92B20"],
  ["AP","Advanced Precast","#00C875"],["NEU","Neumann Steel","#1E4FA3"],
  ["NS","Newnham Scaffolding","#FFCB00"],["EVS","Evolution Shotcrete","#7F5347"],
  ["RZE","Rize Reinforcements","#FF2D87"],["BUT","Butlers","#784BD1"],
  ["S4U","Skips 4 U","#8B1E3F"],["OTH","Other","#B9B2A6"]];
var LKIND = {LOAD:"Load in",BAYS:"Loading bays",SPIN:"Spin up",SNGL:"Single height",
  DECK:"Deck lift",BACK:"Backload",BOOM:"Boom pump",KIB:"Kibble / pour",FLY:"Formwork fly",
  SET:"Set up / dismantle",BIN:"Bins out",PLANT:"Plant / gear",HAND:"Hand unload",
  FORK:"Forklift off",CRANE:"Crane off",CONC:"Concrete truck",PUMP:"Pump",
  SEMI:"Semi / float",HIAB:"Hiab / self-loader",MOVE:"Move"};

var state = {
  date: (location.hash || "").replace(/^#/, "") || boardDate(),
  open: 360, close: 1080, per: 10, per15: ["AP"], breaks: [[600,30],[780,30]],
  trades: {}, order: [], raw: [], rows: [], err: "", note: ""
};
DEF_TRADES.forEach(function(t){ state.trades[t[0]] = [t[1], t[2]]; state.order.push(t[0]); });

function trade(c){ return state.trades[c] || [c || "Other", "#B9B2A6"]; }
/* AP take 15 minutes a lift, everyone else the board's increment */
function perLift(co){ return (state.per15 || []).indexOf(co) >= 0 ? 15 : (state.per || 10); }
function onColour(hex){
  var h = String(hex || "").replace("#","");
  if(h.length !== 6) return "#FFFFFF";
  function li(v){ v = parseInt(v,16)/255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }
  var L = .2126*li(h.slice(0,2)) + .7152*li(h.slice(2,4)) + .0722*li(h.slice(4,6));
  return L > .42 ? "#1A1917" : "#FFFFFF";
}

/* ---------- loading ---------- */
function loadConfig(){
  return api("config?select=data&id=eq.board&project=eq." + PROJ).then(function(rows){
    var d = rows[0] && rows[0].data;
    if(!d) return;
    if(typeof d.open  === "number") state.open  = d.open;
    if(typeof d.close === "number") state.close = d.close;
    if(typeof d.per   === "number") state.per   = d.per;
    if(Array.isArray(d.per15)) state.per15 = d.per15;
    if(Array.isArray(d.breaks)) state.breaks = d.breaks;
    if(Array.isArray(d.trades) && d.trades.length){
      state.trades = {}; state.order = [];
      d.trades.forEach(function(t){ state.trades[t[0]] = [t[1], t[2]]; state.order.push(t[0]); });
    }
  }).catch(function(){});
}
function merge(){ state.rows = global.SB.apply(state.raw, state.date); }
function loadDay(){
  return api("lifts?select=*&project=eq." + PROJ + "&date=eq." + state.date +
             "&order=start_min.asc").then(function(rows){
    state.raw = rows || []; state.err = ""; merge();
  }).catch(function(e){
    state.err = "Could not reach the board data (" + e.message + ").";
    state.raw = []; merge();
  });
}

/* The board rolls to tomorrow after 4:30pm and tomorrow is often a Sunday
   with nothing on it, so open on the next day that has bookings - but only
   when no date was asked for, so the arrows still show an empty day empty. */
var hadHash = !!(location.hash || "").replace(/^#/, "");
var autoJumped = false;
function fillIfEmpty(){
  if(autoJumped || hadHash || state.rows.length) return Promise.resolve();
  autoJumped = true;
  var was = state.date;
  return api("lifts?select=date&project=eq." + PROJ + "&date=gte." + was +
             "&order=date.asc&limit=1")
    .then(function(rows){ return rows[0] && rows[0].date; })
    .catch(function(){ return null; })
    .then(function(d){
      if(!d || d === was) return;
      state.note = "Nothing on " + dayName(was) + " — showing " + dayName(d) + ".";
      state.date = d;
      if(location.hash.replace(/^#/,"") !== d) location.hash = d;
      return loadDay();
    });
}

/* ---------- chrome ---------- */
var renderPage = function(){};
function paint(){
  var dl = document.getElementById("dlab");
  if(dl) dl.innerHTML = esc(dayName(state.date)) + "<small>" + esc(state.date) + "</small>";
  var n = global.SB.count(state.date);
  var b = document.getElementById("sbadge");
  if(b){
    b.textContent = n ? n + (n === 1 ? " change" : " changes") : "Sandbox";
    b.classList.toggle("dirty", !!n);
  }
  var rb = document.getElementById("sreset");
  if(rb) rb.hidden = !n;
  renderPage();
}
function refresh(){ merge(); paint(); }
function go(d){
  state.note = "";
  state.date = d;
  if(location.hash.replace(/^#/,"") !== d) location.hash = d;
  loadDay().then(paint);
}

/* ---------- the edit sheet ---------- */
var editing = null;
function field(label, inner){
  return '<label class="fl"><span>' + label + '</span>' + inner + '</label>';
}
function openSheet(row, isNew){
  editing = row;
  var tr = trade(row.co), c = tr[1];
  var opts = state.order.map(function(k){
    return '<option value="' + k + '"' + (k === row.co ? " selected" : "") + '>' +
           esc(trade(k)[0]) + '</option>';
  }).join("");
  var durs = [10,20,30,45,60,90,120,180].map(function(d){
    return '<option value="' + d + '"' + (d === (row.dur||10) ? " selected" : "") + '>' +
           d + ' min</option>';
  }).join("");
  var s = document.getElementById("sheet");
  s.innerHTML =
    '<div class="sh"><span class="pill" id="spill" style="background:' + c + ';color:' +
      onColour(c) + '">' + esc(row.co || "OTH") + '</span>' +
      '<span class="tag">' + (isNew ? "New" : (row.__added ? "Added here" :
        (row.__edited ? "Changed here" : "From the board"))) + '</span>' +
      '<span class="tm2">' + hm(row.start_min || state.open) + '</span></div>' +
    '<div class="form">' +
      field("Description", '<input id="f_desc" type="text" value="' +
            esc(row.descr || "") + '" placeholder="What is going up">') +
      '<div class="two">' +
        field("Start", '<input id="f_time" type="time" step="600" value="' +
              hm(row.start_min || state.open) + '">') +
        field("For", '<select id="f_dur">' + durs + '</select>') +
      '</div>' +
      field("Mob", '<select id="f_co">' + opts + '</select>') +
      '<div class="two">' +
        field("Lifts", '<input id="f_qty" type="number" inputmode="numeric" min="0" value="' +
              (row.qty || 0) + '">') +
        field("Kilos", '<input id="f_kg" type="number" inputmode="numeric" min="0" value="' +
              (row.kg || 0) + '">') +
      '</div>' +
      '<div class="segs">' +
        '<div class="seg" id="f_type" data-v="' + (row.type === "del" ? "del" : "lift") + '">' +
          '<button type="button" data-s="lift">Crane lift</button>' +
          '<button type="button" data-s="del">Delivery</button></div>' +
        '<div class="seg" id="f_status" data-v="' + (row.status === "con" ? "con" : "req") + '">' +
          '<button type="button" data-s="req">Requested</button>' +
          '<button type="button" data-s="con">Confirmed</button></div>' +
      '</div>' +
    '</div>' +
    (row.notes ? '<div class="notes"><b>From the board</b>' + esc(row.notes) + '</div>' : '') +
    '<div class="acts">' +
      '<button class="btn go" type="button" id="f_save">' + (isNew ? "Add it" : "Save") + '</button>' +
      (isNew ? '' : '<button class="btn del" type="button" id="f_del">Delete</button>') +
      '<button class="btn" type="button" id="f_close">Close</button>' +
    '</div>';

  /* segmented controls */
  Array.prototype.forEach.call(s.querySelectorAll(".seg"), function(seg){
    function sync(){
      Array.prototype.forEach.call(seg.querySelectorAll("button"), function(b){
        b.classList.toggle("on", b.getAttribute("data-s") === seg.getAttribute("data-v"));
      });
    }
    seg.addEventListener("click", function(e){
      var b = e.target.closest("button");
      if(!b) return;
      seg.setAttribute("data-v", b.getAttribute("data-s"));
      sync();
    });
    sync();
  });
  document.getElementById("f_co").addEventListener("change", function(){
    var cc = trade(this.value)[1], p = document.getElementById("spill");
    p.style.background = cc; p.style.color = onColour(cc); p.textContent = this.value;
  });
  document.getElementById("f_save").addEventListener("click", function(){
    var patch = {
      descr: document.getElementById("f_desc").value.trim(),
      start_min: mins(document.getElementById("f_time").value),
      dur: +document.getElementById("f_dur").value,
      co: document.getElementById("f_co").value,
      qty: +document.getElementById("f_qty").value || 0,
      kg:  +document.getElementById("f_kg").value || 0,
      type: document.getElementById("f_type").getAttribute("data-v"),
      status: document.getElementById("f_status").getAttribute("data-v")
    };
    patch.crane = patch.type === "del" ? "none" : "tower";
    if(isNew){
      patch.kind = patch.type === "del" ? "SEMI" : "DECK";
      patch.from_loc = "GROUND"; patch.to_loc = patch.type === "del" ? "GROUND" : "LIVE DECK";
      patch.notes = ""; patch.booked_by = "SANDBOX"; patch.pair = "";
      global.SB.add(state.date, patch);
    } else {
      global.SB.edit(state.date, row, patch);
    }
    closeSheet(); refresh();
  });
  var dl = document.getElementById("f_del");
  if(dl) dl.addEventListener("click", function(){
    global.SB.remove(state.date, row);
    closeSheet(); refresh();
  });
  document.getElementById("f_close").addEventListener("click", closeSheet);
  document.getElementById("scrim").classList.add("on");
  s.classList.add("on");
}
function closeSheet(){
  editing = null;
  document.getElementById("sheet").classList.remove("on");
  document.getElementById("scrim").classList.remove("on");
}
function addNew(){
  var t = Math.min(state.close - 30, Math.max(state.open,
    Math.ceil(nowMin() / state.per) * state.per));
  openSheet({co:"OTH", descr:"", start_min:t, dur:20, qty:0, kg:0,
             type:"lift", status:"req"}, true);
}

/* ---------- boot ---------- */
function boot(render){
  renderPage = render;
  document.getElementById("scrim").addEventListener("click", closeSheet);
  document.addEventListener("keydown", function(e){ if(e.key === "Escape") closeSheet(); });
  document.getElementById("prev").addEventListener("click", function(){ go(shift(state.date,-1)); });
  document.getElementById("next").addEventListener("click", function(){ go(shift(state.date, 1)); });
  var add = document.getElementById("sadd");
  if(add) add.addEventListener("click", addNew);
  var rst = document.getElementById("sreset");
  if(rst) rst.addEventListener("click", function(){
    if(!global.SB.count(state.date)) return;
    global.SB.reset(state.date);
    refresh();
  });
  window.addEventListener("hashchange", function(){
    var d = (location.hash || "").replace(/^#/,"");
    if(d && d !== state.date) go(d);
  });
  function tick(){
    var n = new Date(), c = document.getElementById("clk");
    if(c) c.textContent = two(n.getHours()) + ":" + two(n.getMinutes());
  }
  tick(); setInterval(tick, 20000);
  loadConfig().then(loadDay).then(fillIfEmpty).then(paint);
  setInterval(function(){ loadDay().then(paint); }, 90000);
  document.addEventListener("visibilitychange", function(){
    if(!document.hidden) loadDay().then(paint);
  });
}

global.TK = {
  state:state, PROJ:PROJ, LKIND:LKIND,
  api:api, esc:esc, two:two, hm:hm, mins:mins, iso:iso, nowMin:nowMin,
  dayName:dayName, shift:shift, trade:trade, onColour:onColour, perLift:perLift,
  boot:boot, refresh:refresh, paint:paint, go:go,
  openSheet:openSheet, closeSheet:closeSheet, addNew:addNew
};
})(window);
