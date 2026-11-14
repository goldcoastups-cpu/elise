/* ==========================================================================
   ELISE - SANDBOX LAYER (test pages only)
   --------------------------------------------------------------------------
   Lets the test boards be driven properly without any risk to the real data.
   Every change is kept in this browser under one localStorage key and merged
   over the live rows at render time. Nothing here ever writes to Supabase.
   Clearing the sandbox puts the day back exactly as the board has it.
   ========================================================================== */
(function(global){
"use strict";

var KEY = "elise_sandbox_v1";

function readAll(){
  try{ return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; }
  catch(e){ return {}; }
}
function writeAll(o){
  try{ localStorage.setItem(KEY, JSON.stringify(o)); return true; }
  catch(e){ return false; }   /* private window, full disk - carry on in memory */
}
var mem = readAll();

function day(date){
  if(!mem[date]) mem[date] = {edits:{}, added:[], deleted:[]};
  var d = mem[date];
  if(!d.edits) d.edits = {};
  if(!d.added) d.added = [];
  if(!d.deleted) d.deleted = [];
  return d;
}

var SB = {
  /* merge the sandbox over whatever came back from the database */
  apply: function(rows, date){
    var d = day(date);
    var out = (rows || [])
      .filter(function(r){ return d.deleted.indexOf(r.id) < 0; })
      .map(function(r){
        var e = d.edits[r.id];
        if(!e) return r;
        var c = {}; for(var k in r) c[k] = r[k];
        for(var k2 in e) c[k2] = e[k2];
        c.__edited = true;
        return c;
      });
    d.added.forEach(function(a){
      if(d.deleted.indexOf(a.id) >= 0) return;
      var c = {}; for(var k in a) c[k] = a[k];
      c.__added = true;
      out.push(c);
    });
    out.sort(function(a,b){ return (a.start_min - b.start_min) || 0; });
    return out;
  },

  /* record a change to one field or several */
  edit: function(date, row, patch){
    var d = day(date);
    if(row.__added){
      for(var i = 0; i < d.added.length; i++){
        if(d.added[i].id === row.id){
          for(var k in patch) d.added[i][k] = patch[k];
        }
      }
    } else {
      var e = d.edits[row.id] || (d.edits[row.id] = {});
      for(var k2 in patch) e[k2] = patch[k2];
    }
    writeAll(mem);
  },

  add: function(date, row){
    var d = day(date);
    row.id = "sb-" + Date.now().toString(36);
    row.date = date;
    row.project = "ELISE";
    d.added.push(row);
    writeAll(mem);
    return row.id;
  },

  remove: function(date, row){
    var d = day(date);
    if(row.__added){
      d.added = d.added.filter(function(a){ return a.id !== row.id; });
    } else {
      if(d.deleted.indexOf(row.id) < 0) d.deleted.push(row.id);
      delete d.edits[row.id];
    }
    writeAll(mem);
  },

  /* how many changes are sitting on this day */
  count: function(date){
    var d = day(date);
    return Object.keys(d.edits).length + d.added.length + d.deleted.length;
  },

  reset: function(date){
    delete mem[date];
    writeAll(mem);
  },

  resetAll: function(){
    mem = {};
    writeAll(mem);
  }
};

global.SB = SB;
})(window);
