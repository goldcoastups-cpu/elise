#!/usr/bin/env python3
"""The crew's job page. Reads the jobs list and the append-only log, writes
only to the log, so it never needs write access to Harry's board."""
import sys, os
SB_URL = sys.argv[1].rstrip("/"); SB_KEY = sys.argv[2].strip()
HTML = r"""<!doctype html>
<html lang="en-AU"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>ELISE Jobs</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='%23141312'/><rect x='17' y='15' width='30' height='9' rx='2.5' fill='%23F2EDE4'/><rect x='17' y='27.5' width='23' height='9' rx='2.5' fill='%232FD44A'/><rect x='17' y='40' width='30' height='9' rx='2.5' fill='%23F2EDE4'/></svg>">
<style>
:root{--bg:#1B1A18;--card:#232120;--rule:#35322E;--ink:#F2EDE4;--ink2:#A49C8F;
  --ink3:#6E675D;--accent:#46BCCE;--go:#2FD44A;--pri:#E0A33C;--stop:#FF6B6B}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-text-size-adjust:100%}
body{padding:0 0 40px}
.wrap{max-width:720px;margin:0 auto;padding:0 16px}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--rule);
  padding:12px 0 10px}
.brand{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.brand b{font-size:18px;letter-spacing:.16em}
.me{margin-left:auto;appearance:none;border:1px solid var(--rule);background:transparent;
  color:var(--ink);font:inherit;font-size:12px;font-weight:700;letter-spacing:.06em;
  padding:6px 10px;border-radius:999px;cursor:pointer;text-transform:uppercase}
.me:hover{border-color:var(--accent);color:var(--accent)}
.tabs{display:flex;gap:6px;margin-top:10px}
.tab{flex:1;appearance:none;border:1px solid var(--rule);background:transparent;color:var(--ink2);
  font:inherit;font-size:13px;font-weight:700;padding:8px 6px;border-radius:8px;cursor:pointer;
  letter-spacing:.06em;text-transform:uppercase}
.tab b{display:block;font-size:15px;margin-top:2px;letter-spacing:0}
.tab[aria-selected="true"]{background:var(--card);color:var(--ink);border-color:var(--accent)}
/* Sections carry weight, not just a grey label. One header treatment
   throughout, with the count as a figure rather than prose. */
.sec{display:flex;align-items:baseline;gap:9px;margin:26px 0 0;
  padding-bottom:7px;border-bottom:1.5px solid var(--rule)}
.sec h2{margin:0;font-size:12px;letter-spacing:.15em;text-transform:uppercase;
  font-weight:800;color:var(--ink2)}
.sec .n{font-size:12px;font-weight:700;color:var(--ink3);font-variant-numeric:tabular-nums}
.sec .hint{margin-left:auto;font-size:11px;color:var(--ink3);letter-spacing:.03em}
.sec.pri h2{color:var(--pri)}
.sec.daily h2{color:var(--accent)}

/* A job is a line on a docket. Big square box you can hit with a glove on,
   the words at a readable size, and the age of the thing where you can see
   it - a job sitting since the 3rd is a different problem from one raised
   this morning. */
.job{display:grid;grid-template-columns:26px 1fr;gap:12px;align-items:start;
  width:100%;text-align:left;background:transparent;border:none;
  border-bottom:1px solid var(--rule);color:inherit;font:inherit;cursor:pointer;
  padding:13px 0 13px 0;position:relative}
.job:last-child{border-bottom:none}
.box{width:26px;height:26px;border:2px solid var(--ink3);border-radius:4px;
  display:grid;place-items:center;font-size:15px;line-height:1;color:transparent;
  margin-top:1px;transition:background .12s,border-color .12s}
.job:hover .box{border-color:var(--ink2)}
.job.done .box{background:var(--go);border-color:var(--go);color:#0E1F0D}
.jt{font-size:15px;line-height:1.4;overflow-wrap:anywhere;display:block}
.job.done .jt{color:var(--ink3);text-decoration:line-through;
  text-decoration-color:var(--ink3);text-decoration-thickness:1px}

/* Priority earns a physical edge rather than a glyph you have to hunt for. */
.job.pri{padding-left:13px}
.job.pri::before{content:"";position:absolute;left:0;top:11px;bottom:11px;
  width:3px;border-radius:2px;background:var(--pri)}
.job.pri .jt{color:var(--ink)}

.meta{display:flex;flex-wrap:wrap;align-items:center;gap:7px;margin-top:6px}
.who{font-size:11px;font-weight:700;letter-spacing:.07em;color:var(--ink3);
  text-transform:uppercase}
/* How long it has been carried. Hot once it has been sitting a week. */
.age{font-size:10.5px;font-weight:700;letter-spacing:.04em;color:var(--ink3);
  border:1px solid var(--rule);border-radius:3px;padding:1px 5px;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.age.warm{color:var(--pri);border-color:color-mix(in srgb,var(--pri) 45%,transparent)}
.age.hot{color:var(--stop);border-color:color-mix(in srgb,var(--stop) 45%,transparent)}
.tagnew{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:var(--accent);
  border:1px solid color-mix(in srgb,var(--accent) 45%,transparent);
  border-radius:3px;padding:1px 5px;text-transform:uppercase}
.ev{display:block;font-size:12px;color:var(--ink3);margin-top:6px;line-height:1.45}
.ev b{color:var(--ink2);font-weight:700}
.evimg{margin-top:7px}
.evimg img{width:56px;height:56px;object-fit:cover;border-radius:5px;
  border:1px solid var(--rule);display:block}

/* The daily run-through is a block of its own: an inset rule rather than a
   floating card, so it reads as part of the day without competing with the
   priority work above it. */
.dwrap{border-left:2px solid color-mix(in srgb,var(--accent) 40%,transparent);
  padding-left:13px;margin-top:4px}

/* Priority is a state you set, not a form field, so it reads as a switch. */
.prib{display:flex;align-items:center;gap:10px;width:100%;margin-top:16px;
  appearance:none;font:inherit;font-size:14.5px;font-weight:600;cursor:pointer;
  padding:11px 13px;border-radius:7px;border:1px solid var(--rule);
  background:transparent;color:var(--ink2);text-align:left}
.pdot{width:16px;height:16px;border-radius:50%;border:2px solid var(--ink3);flex:0 0 auto}
.prib[aria-pressed="true"]{border-color:var(--pri);color:var(--pri)}
.prib[aria-pressed="true"] .pdot{background:var(--pri);border-color:var(--pri)}

/* Who is on the job today, under the list - context, not a thing to act on. */
.crew{margin-top:28px;padding-top:14px;border-top:1px solid var(--rule)}
.crew h3{margin:0 0 10px;font-size:12px;letter-spacing:.15em;text-transform:uppercase;
  font-weight:800;color:var(--ink3)}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{display:inline-flex;flex-direction:column;gap:1px;border:1px solid var(--rule);
  border-left:3px solid var(--rule);border-radius:7px;padding:7px 11px;min-width:0}
.chip b{font-size:12.5px;font-weight:700;letter-spacing:.05em}
.chip span{font-size:10.5px;color:var(--ink3);letter-spacing:.03em}
.chip.me{border-color:var(--accent)}
.chip.me b{color:var(--accent)}
.crew .none{font-size:13px;color:var(--ink3);line-height:1.5}
.dwrap .job{padding-top:10px;padding-bottom:10px}
.dwrap .jt{font-size:14.5px}

.empty{padding:30px 0;text-align:center;color:var(--ink3);font-size:14px;line-height:1.5}
.empty b{display:block;color:var(--ink2);font-size:15px;margin-bottom:4px}
.addbtn{width:100%;margin-top:18px;appearance:none;border:1px dashed var(--rule);
  background:transparent;color:var(--ink2);font:inherit;font-size:14px;font-weight:600;
  padding:13px;border-radius:8px;cursor:pointer}
.addbtn:hover{border-color:var(--accent);color:var(--accent)}
footer{margin-top:24px;padding-top:12px;border-top:1px solid var(--rule);font-size:11px;
  color:var(--ink3);letter-spacing:.04em;display:flex;justify-content:space-between;gap:10px}

.scrim{position:fixed;inset:0;background:rgba(10,9,8,.66);z-index:50;display:flex;
  align-items:flex-end;justify-content:center}
.scrim[hidden]{display:none}
.sheet{width:100%;max-width:560px;max-height:92vh;max-height:88dvh;overflow-y:auto;
  background:var(--card);border:1px solid var(--rule);border-radius:12px 12px 0 0;padding:16px}
.sheet h2{margin:0 0 4px;font-size:15px;letter-spacing:.1em;text-transform:uppercase}
.sheet p.q{margin:0 0 14px;font-size:14.5px;line-height:1.4;color:var(--ink2)}
.sheet label{display:block;font-size:11px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--ink3);font-weight:700;margin:12px 0 5px}
.sheet input[type=text],.sheet textarea{width:100%;font:inherit;font-size:16px;padding:10px;
  border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--ink)}
.sheet textarea{min-height:74px;resize:vertical}
.names{display:flex;flex-wrap:wrap;gap:7px;margin-top:4px}
.name{appearance:none;border:1px solid var(--rule);background:transparent;color:var(--ink);
  font:inherit;font-size:14px;font-weight:600;padding:9px 13px;border-radius:999px;cursor:pointer}
.name:hover,.name[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}
.shot{display:flex;gap:10px;align-items:center;margin-top:6px}
.shot img{width:62px;height:62px;object-fit:cover;border-radius:6px;border:1px solid var(--rule)}
.acts{position:sticky;bottom:0;background:var(--card);padding-top:14px;margin-top:16px;
  padding-bottom:calc(4px + env(safe-area-inset-bottom,0px));border-top:1px solid var(--rule);
  display:flex;gap:8px}
.btn{flex:1;appearance:none;font:inherit;font-size:15px;font-weight:700;padding:12px;
  border-radius:7px;border:1px solid var(--rule);background:transparent;color:var(--ink);cursor:pointer}
.btn.go{background:var(--go);border-color:var(--go);color:#10210F}
.btn:disabled{opacity:.5}
.msg{font-size:12.5px;color:var(--stop);margin-top:8px;min-height:16px}
@media(prefers-color-scheme:light){:root:not([data-theme="dark"]){--bg:#F7F4EE;--card:#FFF;
  --rule:#DED7C9;--ink:#1F1D1A;--ink2:#5F594F;--ink3:#8C8578;--stop:#B3261E}}
</style></head>
<body>
<div class="wrap">
  <header>
    <div class="brand"><b>ELISE</b>
      <button class="me" id="meBtn">Who am I?</button></div>
    <div class="tabs" role="tablist">
      <button class="tab" id="t0" aria-selected="true">Today<b id="d0">&nbsp;</b></button>
      <button class="tab" id="t1" aria-selected="false">Tomorrow<b id="d1">&nbsp;</b></button>
    </div>
  </header>
  <div id="list"></div>
  <button class="addbtn" id="addBtn">+ Add a job</button>
  <div id="crew"></div>
  <footer><span id="stamp">Loading&hellip;</span><span>Updates on its own</span></footer>
</div>

<div class="scrim" id="whoScrim" hidden>
  <div class="sheet">
    <h2>Who are you?</h2>
    <p class="q">Tap your name. This phone will remember it, so you only do this once.</p>
    <div class="names" id="names"></div>
    <label for="otherName">Not listed</label>
    <input type="text" id="otherName" placeholder="Type your first name" autocomplete="given-name">
    <div class="acts"><button class="btn go" id="whoSave">That's me</button></div>
    <div class="msg" id="whoMsg"></div>
  </div>
</div>

<div class="scrim" id="jobScrim" hidden>
  <div class="sheet">
    <h2 id="jobHead">Mark it done</h2>
    <p class="q" id="jobText"></p>
    <label for="jobNote">What did you do? (optional)</label>
    <textarea id="jobNote" placeholder="Anything worth recording"></textarea>
    <label>Photo (optional)</label>
    <div class="shot">
      <input type="file" id="shotIn" accept="image/*" capture="environment" hidden>
      <button class="btn" id="shotBtn" style="flex:0 0 auto;padding:10px 16px">Take a photo</button>
      <img id="shotImg" hidden alt="">
    </div>
    <button class="prib" id="priBtn" type="button">
      <span class="pdot"></span><span id="priLabel">Make it priority</span>
    </button>
    <div class="acts">
      <button class="btn" id="jobCancel">Cancel</button>
      <button class="btn" id="priSave" hidden>Save priority</button>
      <button class="btn go" id="jobDone">Mark done</button>
    </div>
    <div class="msg" id="jobMsg"></div>
  </div>
</div>

<div class="scrim" id="addScrim" hidden>
  <div class="sheet">
    <h2>Add a job</h2>
    <p class="q">It'll show on the board for Harry straight away.</p>
    <label for="addText">What needs doing</label>
    <input type="text" id="addText" placeholder="e.g. Clear debris off B2 stair" maxlength="140">
    <div class="acts">
      <button class="btn" id="addCancel">Cancel</button>
      <button class="btn go" id="addSave">Add it</button>
    </div>
    <div class="msg" id="addMsg"></div>
  </div>
</div>
<script>
(function(){
"use strict";
var URL_="__SB_URL__", KEY="__SB_KEY__";
var H={apikey:KEY,Authorization:"Bearer "+KEY};
var JH={apikey:KEY,Authorization:"Bearer "+KEY,"Content-Type":"application/json"};
var BUCKET="job-photos";
var day=0, rows=[], me="", pending=null, shotFile=null, daily=null, dlog={}, crew=[], priWant=false;
var trades=null;

function p2(n){return ("0"+n).slice(-2)}
function iso(d){return d.getFullYear()+"-"+p2(d.getMonth()+1)+"-"+p2(d.getDate())}
function dateFor(o){var d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()+o);return d}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var DAYS=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
    MONS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function nice(d){return DAYS[d.getDay()]+" "+d.getDate()+" "+MONS[d.getMonth()]}
function el(id){return document.getElementById(id)}
function photoURL(id){return URL_+"/storage/v1/object/public/"+BUCKET+"/"+id+".jpg"}
function newId(){return Date.now().toString(36)+Math.random().toString(36).slice(2,9)}

/* ---------- who am I ---------- */
function loadMe(){ try{ return localStorage.getItem("elise.me")||""; }catch(e){ return ""; } }
function saveMe(n){ try{ localStorage.setItem("elise.me", n); }catch(e){} me=n; paintMe(); }
function paintMe(){ el("meBtn").textContent = me || "Who am I?"; }

function askWho(){
  var box=el("names"); box.innerHTML="Loading&hellip;";
  el("whoScrim").hidden=false; el("whoMsg").textContent="";
  el("otherName").value = "";
  fetch(URL_+"/rest/v1/v_crew?select=name&order=last_on_site.desc&limit=30",{headers:H})
    .then(function(r){return r.json()})
    .then(function(list){
      box.innerHTML = (list||[]).map(function(c){
        return '<button class="name" type="button" data-n="'+esc(c.name)+'"'+
               (c.name===me?' aria-pressed="true"':'')+'>'+esc(c.name)+'</button>';
      }).join("") || '<span style="color:var(--ink3);font-size:13px">No names on record yet &mdash; type yours below.</span>';
      Array.prototype.forEach.call(box.querySelectorAll("[data-n]"),function(b){
        b.addEventListener("click",function(){
          saveMe(b.getAttribute("data-n"));
          el("whoScrim").hidden=true; render();
        });
      });
    }).catch(function(){ box.innerHTML='<span style="color:var(--ink3);font-size:13px">Couldn\'t load the crew list &mdash; type your name below.</span>'; });
}
el("meBtn").addEventListener("click", askWho);
el("whoSave").addEventListener("click", function(){
  var n=el("otherName").value.trim().toUpperCase();
  if(!n){ el("whoMsg").textContent="Tap a name or type yours."; return; }
  saveMe(n); el("whoScrim").hidden=true; render();
});

/* ---------- the list ---------- */
function load(){
  var from=iso(dateFor(0)), to=iso(dateFor(1));
  el("d0").textContent=nice(dateFor(0)); el("d1").textContent=nice(dateFor(1));
  var jobs=[
    fetch(URL_+"/rest/v1/v_job_status?job_date=gte."+from+"&job_date=lte."+to+
          "&select=*&order=priority.desc,item_text",{headers:H})
      .then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); }),
    /* the daily run-through's ticks for these two days */
    fetch(URL_+"/rest/v1/job_log?job_date=gte."+from+"&job_date=lte."+to+
          "&item_id=like.daily-*&select=item_id,action,who,note,photo_id,at,job_date"+
          "&order=at.desc",{headers:H}).then(function(r){ return r.ok?r.json():[]; }),
    /* who is on site these two days */
    fetch(URL_+"/rest/v1/v_labour_day?job_date=gte."+from+"&job_date=lte."+to+
          "&select=*",{headers:H}).then(function(r){ return r.ok?r.json():[]; })
  ];
  var needCfg = (!daily || !trades);
  if(needCfg) jobs.push(
    fetch(URL_+"/rest/v1/config?id=in.(daily,board)&select=id,data",{headers:H})
      .then(function(r){ return r.ok?r.json():[]; }));
  var cfgAt = needCfg ? 3 : -1;
  Promise.all(jobs).then(function(res){
    rows=res[0]||[];
    dlog={};
    (res[1]||[]).forEach(function(l){ if(!dlog[l.item_id]) dlog[l.item_id]=l; });
    crew=res[2]||[];
    if(cfgAt>0 && res[cfgAt]) res[cfgAt].forEach(function(c){
      if(c.id==="daily") daily=c.data;
      if(c.id==="board" && c.data && c.data.trades) trades=c.data.trades;
    });
    render();
    var n=new Date();
    el("stamp").textContent="Checked "+p2(n.getHours())+":"+p2(n.getMinutes());
  }).catch(function(){
    el("stamp").textContent="Can't reach the board \u2014 showing the last load";
  });
}

/* The standing list, materialised for one day. Each day gets its own ids
   (daily-stairs-2026-11-11) so yesterday's tick never carries into today -
   a daily is only done if it was done today. */
function dailyFor(dateStr){
  var items=(daily&&daily.items)||[];
  return items.map(function(it){
    var id="daily-"+it.n+"-"+dateStr, l=dlog[id];
    var isDone = !!(l && l.action==="done");
    return {item_id:id, item_text:it.text, job_date:dateStr, priority:false,
            assigned:null, carried_from:null, crew_added:false, isDaily:true,
            done:isDone,
            done_by:   isDone ? l.who      : null,
            done_at:   isDone ? l.at       : null,
            done_note: isDone ? (l.note||null)     : null,
            done_photo:isDone ? (l.photo_id||null) : null};
  });
}

function shortDay(d){
  var x = (d instanceof Date) ? d : new Date(d);
  return x.getDate()+" "+MONS[x.getMonth()];
}
/* Days a job has been carried. This is the thing worth seeing - the date it
   was raised tells you far less than the fact it has been open eight days. */
function ageOf(from){
  if(!from) return null;
  var a=new Date(from+"T00:00:00"), b=new Date(); b.setHours(0,0,0,0);
  var d=Math.round((b-a)/86400000);
  return d>0 ? d : null;
}

function jobRow(j){
  var cls="job"+(j.done?" done":"")+(j.priority&&!j.done?" pri":"");
  var meta=[];

  if(j.assigned) meta.push('<span class="who">'+esc(j.assigned)+'</span>');
  if(j.crew_added) meta.push('<span class="tagnew">Added on site</span>');
  var age=j.done?null:ageOf(j.carried_from);
  if(age) meta.push('<span class="age'+(age>=14?" hot":age>=7?" warm":"")+'">'+
                    age+' day'+(age===1?'':'s')+'</span>');

  var ev="";
  if(j.done){
    var when=j.done_at?new Date(j.done_at):null;
    var line=(j.done_by?'<b>'+esc(j.done_by)+'</b>':'');
    if(when) line+=(line?' ':'')+shortDay(when)+', '+
      (function(h,m){var ap=h<12?'am':'pm',t=h%12||12;return t+':'+p2(m)+ap})(when.getHours(),when.getMinutes());
    if(j.done_note) line+=(line?' &mdash; ':'')+esc(j.done_note);
    ev='<span class="ev">'+line+'</span>';
    if(j.done_photo) ev+='<span class="evimg"><img src="'+photoURL(esc(j.done_photo))+'" alt="" loading="lazy"></span>';
  }

  return '<button class="'+cls+'" data-id="'+esc(j.item_id)+'" type="button">'+
    '<span class="box">&#10003;</span>'+
    '<span><span class="jt">'+esc(j.item_text)+'</span>'+
    (meta.length?'<span class="meta">'+meta.join("")+'</span>':'')+ev+'</span></button>';
}

function sec(cls,title,count,hint){
  return '<div class="sec'+(cls?" "+cls:"")+'"><h2>'+esc(title)+'</h2>'+
    '<span class="n">'+count+'</span>'+
    (hint?'<span class="hint">'+esc(hint)+'</span>':'')+'</div>';
}

function render(){
  paintMe();
  var want=iso(dateFor(day));
  var mine=rows.filter(function(j){return j.job_date===want});
  var pri =mine.filter(function(j){return !j.done && j.priority});
  var todo=mine.filter(function(j){return !j.done && !j.priority});
  var done=mine.filter(function(j){return j.done});
  var dl  =dailyFor(want);
  var dDone=dl.filter(function(x){return x.done}).length;

  var html="";

  /* Priority first - the starred work is what the day turns on. */
  if(pri.length) html += sec("pri","Priority",pri.length) + pri.map(jobRow).join("");

  /* Then the daily run-through, which is the same every morning. */
  if(dl.length){
    html += sec("daily","Daily", dDone+" of "+dl.length, (daily&&daily.note)||"") +
            '<div class="dwrap">'+dl.map(jobRow).join("")+'</div>';
  }

  if(todo.length) html += sec("","To do",todo.length) + todo.map(jobRow).join("");
  if(done.length) html += sec("","Completed",done.length) + done.map(jobRow).join("");

  if(!mine.length && !dl.length){
    html = '<div class="empty"><b>Nothing on the list</b>No jobs for this day yet. '+
           'Add one below if something needs doing.</div>';
  } else if(!pri.length && !todo.length){
    html += '<div class="empty"><b>Job list is clear</b>'+
            (dDone<dl.length?'Daily run-through still to finish.':'Everything ticked off.')+'</div>';
  }

  el("list").innerHTML=html;
  Array.prototype.forEach.call(el("list").querySelectorAll("[data-id]"),function(b){
    b.addEventListener("click",function(){ openJob(b.getAttribute("data-id")); });
  });
  paintCrew(want);
}

/* Who is on the job. Context for the list above it, not something to act on,
   so it sits at the bottom and stays quiet. */
/* Trade colour for a labour supplier. ELISE is in the board's trade table so
   it gets the same olive it has everywhere else; the two labour-hire firms
   are not trades and carry their own colours. */
var SUPPLIER_COLOUR = { WORKCON:"#4FA3D1", HARWELL:"#C96A2E" };
function supplierColour(name){
  var n=String(name||"").trim().toUpperCase();
  if(!n) return "";
  if(SUPPLIER_COLOUR[n]) return SUPPLIER_COLOUR[n];
  var hit=(trades||[]).filter(function(t){
    return String(t[1]||"").toUpperCase()===n || String(t[0]||"").toUpperCase()===n;
  })[0];
  return (hit && hit[2]) ? hit[2] : "";
}

function paintCrew(want){
  var on=crew.filter(function(c){ return c.job_date===want; });
  var box=el("crew");
  if(!on.length){
    box.innerHTML='<div class="crew"><h3>On site</h3>'+
      '<p class="none">Nobody logged for this day yet. Names appear once the '+
      'hours go in of an evening.</p></div>';
    return;
  }
  box.innerHTML='<div class="crew"><h3>On site <span style="color:var(--ink3);'+
    'font-weight:700">'+on.length+'</span></h3><div class="chips">'+
    on.map(function(c){
      var sub=[c.area,c.task].filter(Boolean)[0]||"";
      var tint=supplierColour(c.supplier);
      var line=[c.supplier,sub].filter(Boolean).join(" \u00b7 ");
      return '<span class="chip'+(c.name===me?" me":"")+'"'+
             (tint?' style="border-left-color:'+tint+'"':'')+'><b>'+esc(c.name)+'</b>'+
             (line?'<span>'+esc(line)+'</span>':'')+'</span>';
    }).join("")+'</div></div>';
}

[0,1].forEach(function(i){
  el("t"+i).addEventListener("click",function(){
    day=i; el("t0").setAttribute("aria-selected",i===0?"true":"false");
    el("t1").setAttribute("aria-selected",i===1?"true":"false"); render();
  });
});

/* ---------- ticking one off ---------- */
function openJob(id){
  if(!me){ askWho(); return; }
  var j=rows.filter(function(x){return x.item_id===id})[0]
        || dailyFor(iso(dateFor(day))).filter(function(x){return x.item_id===id})[0];
  if(!j) return;
  pending=j; shotFile=null;
  el("jobHead").textContent = j.done ? "Reopen this job" : "Mark it done";
  el("jobText").textContent = j.item_text;
  el("jobNote").value=""; el("jobMsg").textContent="";
  el("shotImg").hidden=true; el("shotImg").removeAttribute("src");
  el("jobDone").textContent = j.done ? "Reopen it" : "Mark done";
  el("jobDone").className = j.done ? "btn" : "btn go";
  priWant = !!j.priority;
  paintPri();
  el("jobScrim").hidden=false;
}
function paintPri(){
  var b=el("priBtn");
  b.setAttribute("aria-pressed", priWant?"true":"false");
  el("priLabel").textContent = priWant ? "Priority" : "Make it priority";
  /* Marking something priority is not the same as finishing it, so the save
     for it appears on its own as soon as the toggle differs. */
  el("priSave").hidden = !pending || (priWant === !!pending.priority);
}

async function logRows(batch){
  var r = await fetch(URL_+"/rest/v1/job_log",{method:"POST",headers:JH,
          body:JSON.stringify(batch)});
  if(!r.ok) throw new Error(await r.text());
}

el("priSave").addEventListener("click", async function(){
  if(!pending) return;
  var b=el("priSave"); b.disabled=true;
  el("jobMsg").style.color="var(--ink3)"; el("jobMsg").textContent="Saving\u2026";
  try{
    await logRows([{item_id:pending.item_id, job_date:pending.job_date,
      action: priWant?"pri":"unpri", item_text:pending.item_text,
      who:me, note:"", photo_id:""}]);
    el("jobScrim").hidden=true; load();
  }catch(e){
    el("jobMsg").style.color="var(--stop)";
    el("jobMsg").textContent="Didn't save. Try again.";
  }
  b.disabled=false;
});
el("priBtn").addEventListener("click",function(){ priWant=!priWant; paintPri(); });
el("jobCancel").addEventListener("click",function(){ el("jobScrim").hidden=true; });
el("shotBtn").addEventListener("click",function(){ el("shotIn").click(); });
el("shotIn").addEventListener("change",function(){
  var f=el("shotIn").files && el("shotIn").files[0]; if(!f) return;
  shotFile=f;
  var fr=new FileReader();
  fr.onload=function(){ var im=el("shotImg"); im.src=fr.result; im.hidden=false; };
  fr.readAsDataURL(f);
});

/* Shrink before upload - a phone photo is several megabytes and the crew are
   on site wifi or a couple of bars of 4G. */
function shrink(file){
  return new Promise(function(res){
    var fr=new FileReader();
    fr.onload=function(){
      var img=new Image();
      img.onload=function(){
        var max=1280, w=img.width, h=img.height;
        if(w>max||h>max){ if(w>h){h=Math.round(h*max/w);w=max;} else {w=Math.round(w*max/h);h=max;} }
        var c=document.createElement("canvas"); c.width=w; c.height=h;
        c.getContext("2d").drawImage(img,0,0,w,h);
        c.toBlob(function(b){ res(b||file); },"image/jpeg",.82);
      };
      img.onerror=function(){ res(file); };
      img.src=fr.result;
    };
    fr.onerror=function(){ res(file); };
    fr.readAsDataURL(file);
  });
}

el("jobDone").addEventListener("click", async function(){
  if(!pending) return;
  var btn=el("jobDone"); btn.disabled=true;
  el("jobMsg").style.color="var(--ink3)"; el("jobMsg").textContent="Saving…";
  var photoId="";
  try{
    if(shotFile){
      el("jobMsg").textContent="Uploading the photo…";
      var blob=await shrink(shotFile);
      photoId=newId();
      var up=await fetch(URL_+"/storage/v1/object/"+BUCKET+"/"+photoId+".jpg",{
        method:"POST", headers:{apikey:KEY,Authorization:"Bearer "+KEY,"Content-Type":"image/jpeg"},
        body:blob });
      if(!up.ok){ photoId=""; el("jobMsg").style.color="var(--stop)";
        el("jobMsg").textContent="Photo wouldn't upload — saving without it."; }
    }
    var batch=[];
    /* a priority change is its own line in the record, so you can see who
       raised it and when, not just that it is starred now */
    if(priWant !== !!pending.priority){
      batch.push({item_id:pending.item_id, job_date:pending.job_date,
        action: priWant?"pri":"unpri", item_text:pending.item_text,
        who:me, note:"", photo_id:""});
    }
    batch.push({item_id:pending.item_id, job_date:pending.job_date,
      action: pending.done ? "reopen" : "done", item_text:pending.item_text,
      who:me, note:el("jobNote").value.trim(), photo_id:photoId});
    var r=await fetch(URL_+"/rest/v1/job_log",{method:"POST",headers:JH,
      body:JSON.stringify(batch)});
    if(!r.ok) throw new Error(await r.text());
    el("jobScrim").hidden=true; load();
  }catch(e){
    el("jobMsg").style.color="var(--stop)";
    el("jobMsg").textContent="Didn't save. Try again in a moment.";
  }
  btn.disabled=false;
});

/* ---------- adding one ---------- */
el("addBtn").addEventListener("click",function(){
  if(!me){ askWho(); return; }
  el("addText").value=""; el("addMsg").textContent=""; el("addScrim").hidden=false;
});
el("addCancel").addEventListener("click",function(){ el("addScrim").hidden=true; });
el("addSave").addEventListener("click", async function(){
  var t=el("addText").value.trim();
  if(!t){ el("addMsg").textContent="Type what needs doing."; return; }
  var b=el("addSave"); b.disabled=true; el("addMsg").style.color="var(--ink3)";
  el("addMsg").textContent="Saving…";
  try{
    var r=await fetch(URL_+"/rest/v1/job_log",{method:"POST",headers:JH,
      body:JSON.stringify([{item_id:"crew-"+newId(), job_date:iso(dateFor(day)),
        action:"add", item_text:t, who:me, note:"", photo_id:""}])});
    if(!r.ok) throw new Error();
    el("addScrim").hidden=true; load();
  }catch(e){ el("addMsg").style.color="var(--stop)"; el("addMsg").textContent="Didn't save. Try again."; }
  b.disabled=false;
});

me=loadMe();
load();
if(!me) setTimeout(askWho, 600);
setInterval(load, 60000);
document.addEventListener("visibilitychange",function(){
  if(document.visibilityState==="visible") load();
});
})();
</script>
</body></html>
"""
out = HTML.replace("__SB_URL__", SB_URL).replace("__SB_KEY__", SB_KEY)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "w").write(out)
print("wrote index.html", len(out), "bytes")
