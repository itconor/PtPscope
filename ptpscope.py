# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────────────────────
# PTPScope — GPS PTP Grandmaster for Raspberry Pi
# Single-file Flask application with embedded templates
# ─────────────────────────────────────────────────────────────────────────────
BUILD = "PTPScope-1.3.5"

# ═══════════════════════════════════════════════════════════════════════════════
#  HTML TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

# ── Dashboard ─────────────────────────────────────────────────────────────────
DASHBOARD_TPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>PTPScope — Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="csrf-token" content="{{csrf_token()}}">
<style nonce="{{csp_nonce()}}">
:root{--bg:#07142b;--sur:#0d2346;--bor:#17345f;--acc:#17a8ff;--ok:#22c55e;--wn:#f59e0b;--al:#ef4444;--tx:#eef5ff;--mu:#8aa4c8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top, #12376f 0%, var(--bg) 38%, #05101f 100%);color:var(--tx);font-size:14px;position:relative;min-height:100vh}
body::before{content:"";position:fixed;right:28px;bottom:22px;width:280px;height:280px;background:url("/static/ptpscope_icon.png") no-repeat center/contain;opacity:.045;pointer-events:none;filter:drop-shadow(0 0 24px rgba(23,168,255,.10));z-index:0}
body>*{position:relative;z-index:1}
a{color:var(--acc);text-decoration:none}
header{background:linear-gradient(180deg, rgba(10,31,65,.96), rgba(9,24,48,.96));border-bottom:1px solid var(--bor);padding:12px 20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;box-shadow:0 10px 24px rgba(0,0,0,.18)}
header h1{font-size:17px;font-weight:700}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;background:#1e3a5f;color:var(--acc)}
.nav-active{background:var(--acc)!important;color:#fff!important}
nav{display:flex;gap:6px;margin-left:auto;flex-wrap:wrap}
.btn{display:inline-block;padding:5px 12px;border-radius:8px;font-size:13px;cursor:pointer;border:none;text-decoration:none;font-weight:600;color:var(--tx)}.btn:hover{filter:brightness(1.05)}
.bp{background:var(--acc);color:#fff}.bd{background:var(--al);color:#fff}.bg{background:var(--bor);color:var(--tx)}
.bs{padding:3px 9px;font-size:12px}
main{padding:16px;max-width:1440px;margin:0 auto}
.fl{list-style:none;margin-bottom:10px}.fl li{padding:8px 12px;border-radius:6px;background:#1e3a5f;border-left:3px solid var(--acc);margin-bottom:5px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.card{background:var(--sur);border:1px solid var(--bor);border-radius:12px;overflow:hidden;box-shadow:0 3px 10px rgba(0,0,0,.16);transition:transform .14s, box-shadow .14s}
.card:hover{transform:translateY(-1px);box-shadow:0 8px 18px rgba(0,0,0,.22)}
.ch{padding:9px 13px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--bor);background:linear-gradient(180deg,#143766,#102b54)}
.ch-title{font-size:13px;font-weight:700;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.dok{background:var(--ok)}.dwn{background:var(--wn)}.dal{background:var(--al);animation:p 1s infinite}.did{background:var(--mu)}.dlr{background:#38bdf8}
@keyframes p{0%,100%{opacity:1}50%{opacity:.3}}
.lbar-wrap{padding:8px 13px;border-bottom:1px solid var(--bor);display:flex;align-items:center;gap:8px}
.lbar-track{flex:1;height:7px;background:#123764;border-radius:4px;overflow:hidden}
.lbar-fill{height:7px;border-radius:4px;transition:width .4s,background .4s;min-width:2px}
.lbar-val{font-size:12px;font-weight:600;min-width:62px;text-align:right;font-variant-numeric:tabular-nums}
.rows{padding:8px 13px}
.row{display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid var(--bor);font-size:12px;gap:8px}
.row:last-child{border:none}
.rl{color:var(--mu);flex-shrink:0}.rv{text-align:right;word-break:break-word;font-variant-numeric:tabular-nums}
.logbox{background:var(--sur);border:1px solid var(--bor);border-radius:8px;padding:12px;font-family:monospace;font-size:11px;height:190px;overflow-y:auto;margin-top:12px;white-space:pre-wrap;word-break:break-all}
.st-hdr{font-size:12px;font-weight:600;color:var(--mu);letter-spacing:.06em;text-transform:uppercase;margin:14px 0 8px}
</style>
<link rel="icon" type="image/x-icon" href="/static/ptpscope_icon.png">
</head><body>
{{topnav("dashboard")|safe}}
<main>
{% with msgs = get_flashed_messages() %}{% if msgs %}<ul class="fl">{% for m in msgs %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
<div class="grid">
  {% if role != 'ptp_master' %}
  <!-- GPS Card (standalone + gps_source) -->
  <div class="card" id="gps-card">
    <div class="ch"><span class="dot did" id="gps-dot"></span><span class="ch-title">GPS Receiver</span><span class="badge" id="gps-fix-badge">—</span></div>
    <div class="lbar-wrap"><div class="lbar-track"><div class="lbar-fill" id="gps-bar" style="width:0%;background:var(--mu)"></div></div><div class="lbar-val" id="gps-hdop-val">—</div></div>
    <div class="rows">
      <div class="row"><span class="rl">Latitude</span><span class="rv" id="gps-lat">—</span></div>
      <div class="row"><span class="rl">Longitude</span><span class="rv" id="gps-lon">—</span></div>
      <div class="row"><span class="rl">Altitude</span><span class="rv" id="gps-alt">—</span></div>
      <div class="row"><span class="rl">Satellites</span><span class="rv" id="gps-sats">—</span></div>
      <div class="row"><span class="rl">Speed</span><span class="rv" id="gps-speed">—</span></div>
      <div class="row"><span class="rl">UTC Time</span><span class="rv" id="gps-utc">—</span></div>
      <div class="row"><span class="rl">PPS</span><span class="rv"><span class="dot did" id="gps-pps" style="display:inline-block"></span></span></div>
      <div class="row"><span class="rl">HDOP</span><span class="rv" id="gps-hdop">—</span></div>
    </div>
  </div>
  {% endif %}
  {% if role == 'ptp_master' %}
  <!-- GPS Source Card (ptp_master — shows remote GPS node heartbeat data) -->
  <div class="card" id="gps-src-card">
    <div class="ch"><span class="dot did" id="gps-src-dot"></span><span class="ch-title">GPS Source</span><span class="badge" id="gps-src-site-badge">—</span></div>
    <div class="lbar-wrap"><div class="lbar-track"><div class="lbar-fill" id="gps-src-bar" style="width:0%;background:var(--mu)"></div></div><div class="lbar-val" id="gps-src-hdop-val">—</div></div>
    <div class="rows">
      <div class="row"><span class="rl">Connection</span><span class="rv" id="gps-src-age">—</span></div>
      <div class="row"><span class="rl">GPS Fix</span><span class="rv" id="gps-src-fix">—</span></div>
      <div class="row"><span class="rl">Satellites</span><span class="rv" id="gps-src-sats">—</span></div>
      <div class="row"><span class="rl">HDOP</span><span class="rv" id="gps-src-hdop">—</span></div>
      <div class="row"><span class="rl">UTC Time</span><span class="rv" id="gps-src-utc">—</span></div>
      <div class="row"><span class="rl">Latitude</span><span class="rv" id="gps-src-lat">—</span></div>
      <div class="row"><span class="rl">Longitude</span><span class="rv" id="gps-src-lon">—</span></div>
      <div class="row"><span class="rl">PPS</span><span class="rv"><span class="dot did" id="gps-src-pps" style="display:inline-block"></span></span></div>
      <div class="row"><span class="rl">NTP Stratum</span><span class="rv" id="gps-src-stratum">—</span></div>
      <div class="row"><span class="rl">NTP Offset</span><span class="rv" id="gps-src-offset">—</span></div>
    </div>
  </div>
  {% endif %}
  {% if role != 'gps_source' %}
  <!-- PTP Card (standalone + ptp_master) -->
  <div class="card" id="ptp-card">
    <div class="ch"><span class="dot did" id="ptp-dot"></span><span class="ch-title">PTP Grandmaster</span><span class="badge" id="ptp-state-badge">—</span></div>
    <div class="lbar-wrap"><div class="lbar-track"><div class="lbar-fill" id="ptp-bar" style="width:0%;background:var(--mu)"></div></div><div class="lbar-val" id="ptp-offset-val">—</div></div>
    <div class="rows">
      <div class="row"><span class="rl">Port State</span><span class="rv" id="ptp-port">—</span></div>
      <div class="row"><span class="rl">Clock Class</span><span class="rv" id="ptp-class">—</span></div>
      <div class="row"><span class="rl">PTP Offset</span><span class="rv" id="ptp-offset">—</span></div>
      <div class="row"><span class="rl">PHC Offset</span><span class="rv" id="ptp-phc-offset">—</span></div>
      <div class="row"><span class="rl">Path Delay</span><span class="rv" id="ptp-delay">—</span></div>
      <div class="row"><span class="rl">GM Identity</span><span class="rv" id="ptp-gm" style="font-family:monospace;font-size:11px">—</span></div>
      <div class="row"><span class="rl">Domain</span><span class="rv" id="ptp-domain">—</span></div>
      <div class="row"><span class="rl">Transport</span><span class="rv" id="ptp-transport">—</span></div>
      <div class="row"><span class="rl">Slaves</span><span class="rv" id="ptp-slaves">—</span></div>
      <div class="row"><span class="rl">PID</span><span class="rv" id="ptp-pid" style="font-family:monospace">—</span></div>
    </div>
  </div>
  {% endif %}
  <!-- Chrony Card (all roles) -->
  <div class="card" id="chrony-card">
    <div class="ch"><span class="dot did" id="chrony-dot"></span><span class="ch-title">System Clock (Chrony)</span><span class="badge" id="chrony-stratum-badge">—</span></div>
    <div class="lbar-wrap"><div class="lbar-track"><div class="lbar-fill" id="chrony-bar" style="width:0%;background:var(--mu)"></div></div><div class="lbar-val" id="chrony-offset-val">—</div></div>
    <div class="rows">
      <div class="row"><span class="rl">Reference</span><span class="rv" id="chrony-ref">—</span></div>
      <div class="row"><span class="rl">Stratum</span><span class="rv" id="chrony-stratum">—</span></div>
      <div class="row"><span class="rl">System Offset</span><span class="rv" id="chrony-offset">—</span></div>
      <div class="row"><span class="rl">RMS Offset</span><span class="rv" id="chrony-rms">—</span></div>
      <div class="row"><span class="rl">Frequency</span><span class="rv" id="chrony-freq">—</span></div>
      <div class="row"><span class="rl">Skew</span><span class="rv" id="chrony-skew">—</span></div>
      <div class="row"><span class="rl">Root Delay</span><span class="rv" id="chrony-rdelay">—</span></div>
      <div class="row"><span class="rl">Root Dispersion</span><span class="rv" id="chrony-rdisp">—</span></div>
      <div class="row"><span class="rl">Leap Status</span><span class="rv" id="chrony-leap">—</span></div>
      <div class="row"><span class="rl">Sources</span><span class="rv" id="chrony-sources">—</span></div>
    </div>
  </div>
  <!-- System Card (all roles) -->
  <div class="card" id="sys-card">
    <div class="ch"><span class="dot dok" id="sys-dot"></span><span class="ch-title">{% if role == 'ptp_master' %}PTP Host{% elif role == 'gps_source' %}GPS Host{% else %}Raspberry Pi{% endif %}</span><span class="badge" id="sys-model-badge">—</span></div>
    <div class="lbar-wrap"><div class="lbar-track"><div class="lbar-fill" id="sys-bar" style="width:0%;background:var(--mu)"></div></div><div class="lbar-val" id="sys-temp-val">—</div></div>
    <div class="rows">
      <div class="row"><span class="rl">Uptime</span><span class="rv" id="sys-uptime">—</span></div>
      <div class="row"><span class="rl">CPU Temp</span><span class="rv" id="sys-temp">—</span></div>
      <div class="row"><span class="rl">Load Average</span><span class="rv" id="sys-load">—</span></div>
      <div class="row"><span class="rl">Memory</span><span class="rv" id="sys-mem">—</span></div>
      <div class="row"><span class="rl">Disk</span><span class="rv" id="sys-disk">—</span></div>
      <div class="row"><span class="rl">Hostname</span><span class="rv" id="sys-hostname">—</span></div>
      <div class="row"><span class="rl">IP Address</span><span class="rv" id="sys-ip" style="font-family:monospace">—</span></div>
      <div class="row"><span class="rl">Kernel</span><span class="rv" id="sys-kernel" style="font-family:monospace;font-size:11px">—</span></div>
    </div>
  </div>
  {% if role == 'gps_source' %}
  <!-- Hub Connection Card (gps_source only) -->
  <div class="card" id="hub-conn-card">
    <div class="ch"><span class="dot did" id="hub-conn-dot"></span><span class="ch-title">Hub Connection</span><span class="badge" id="hub-conn-badge">—</span></div>
    <div class="rows">
      <div class="row"><span class="rl">PTP Master</span><span class="rv" id="hub-conn-url" style="font-family:monospace;font-size:11px;word-break:break-all">—</span></div>
      <div class="row"><span class="rl">State</span><span class="rv" id="hub-conn-state">—</span></div>
      <div class="row"><span class="rl">Last Sent</span><span class="rv" id="hub-conn-last">—</span></div>
      <div class="row"><span class="rl">Latency</span><span class="rv" id="hub-conn-latency">—</span></div>
      <div class="row"><span class="rl">Total Sent</span><span class="rv" id="hub-conn-total">—</span></div>
      <div class="row"><span class="rl">Total Failures</span><span class="rv" id="hub-conn-fails">—</span></div>
      <div class="row"><span class="rl">Fail Streak</span><span class="rv" id="hub-conn-streak">—</span></div>
    </div>
  </div>
  {% endif %}
</div>
<!-- Recent log -->
<div class="st-hdr">Recent Log</div>
<div class="logbox" id="dash-log">Waiting for data...</div>
</main>
<script nonce="{{csp_nonce()}}">
function _csrfFetch(url,opts){
  opts=opts||{};if(!opts.headers)opts.headers={};
  var t=document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)?.[1]||(document.querySelector('meta[name="csrf-token"]')||{}).content||"";
  opts.headers["X-CSRFToken"]=t;return fetch(url,opts);
}
function setText(id,v){var e=document.getElementById(id);if(e)e.textContent=v!=null?v:'—';}
function updateDot(id,state){
  var e=document.getElementById(id);if(!e)return;
  e.className='dot '+(state==='ok'?'dok':state==='warn'?'dwn':state==='error'?'dal':state==='learning'?'dlr':'did');
}
function updateBar(id,pct,color){
  var e=document.getElementById(id);if(!e)return;
  e.style.width=Math.max(0,Math.min(100,pct))+'%';e.style.background=color||'var(--acc)';
}
function hdopPct(v){if(v>=20)return 0;return Math.max(0,100-v*5);}
function hdopColor(v){return v<=1?'var(--ok)':v<=2?'var(--ok)':v<=5?'var(--wn)':'var(--al)';}
function offsetPct(v){var a=Math.abs(v);if(a>5000)return 100;return Math.min(100,a/50);}
function offsetColor(v){var a=Math.abs(v);return a<100?'var(--ok)':a<1000?'var(--wn)':'var(--al)';}
function tempPct(v){return Math.max(0,Math.min(100,(v-30)/55*100));}
function tempColor(v){return v<60?'var(--ok)':v<75?'var(--wn)':'var(--al)';}
function chronoOffPct(v){var a=Math.abs(v);if(a>1000)return 100;return Math.min(100,a/10);}
function chronoOffColor(v){var a=Math.abs(v);return a<1?'var(--ok)':a<10?'var(--wn)':'var(--al)';}
function fmtUptime(s){var d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return(d?d+'d ':'')+(h?h+'h ':'')+m+'m';}
function pollStatus(){
  fetch('/api/status').then(function(r){return r.json();}).then(function(d){
    // GPS (standalone + gps_source)
    if(d.gps){
      var g=d.gps;
      updateDot('gps-dot',g.state);
      setText('gps-fix-badge',g.fix_quality);
      setText('gps-lat',g.latitude!==0?g.latitude.toFixed(6):'—');
      setText('gps-lon',g.longitude!==0?g.longitude.toFixed(6):'—');
      setText('gps-alt',g.altitude!==0?g.altitude.toFixed(1)+' m':'—');
      setText('gps-sats',g.satellites_used+' / '+g.satellites_view);
      setText('gps-speed',g.speed_knots.toFixed(1)+' kn');
      setText('gps-utc',g.utc_time||'—');
      setText('gps-hdop',g.hdop<99?g.hdop.toFixed(1):'—');
      setText('gps-hdop-val','HDOP '+(g.hdop<99?g.hdop.toFixed(1):'—'));
      updateDot('gps-pps',g.pps_ok?'ok':'error');
      updateBar('gps-bar',hdopPct(g.hdop),hdopColor(g.hdop));
    }
    // GPS Source card (ptp_master role — remote GPS node heartbeat)
    if(d.gps_source){
      var gs=d.gps_source,gg=gs.gps||{},gc=gs.chrony||{};
      updateDot('gps-src-dot',gs.state);
      setText('gps-src-site-badge',gs.site||'—');
      setText('gps-src-age',gs.last_hb_ago!==null?gs.last_hb_ago+'s ago':'No data');
      setText('gps-src-fix',gg.fix_quality||'—');
      setText('gps-src-sats',gg.satellites_used!==undefined?gg.satellites_used+' / '+gg.satellites_view:'—');
      setText('gps-src-hdop',gg.hdop!==undefined&&gg.hdop<99?gg.hdop.toFixed(1):'—');
      setText('gps-src-hdop-val','HDOP '+(gg.hdop!==undefined&&gg.hdop<99?gg.hdop.toFixed(1):'—'));
      setText('gps-src-utc',gg.utc_time||'—');
      setText('gps-src-lat',gg.latitude?gg.latitude.toFixed(6):'—');
      setText('gps-src-lon',gg.longitude?gg.longitude.toFixed(6):'—');
      updateDot('gps-src-pps',gg.pps_ok?'ok':'error');
      setText('gps-src-stratum',gc.stratum!==undefined?gc.stratum:'—');
      setText('gps-src-offset',gc.system_offset_us!==undefined?gc.system_offset_us.toFixed(3)+' \u00b5s':'—');
      if(gg.hdop!==undefined)updateBar('gps-src-bar',hdopPct(gg.hdop),hdopColor(gg.hdop));
    }
    // PTP (standalone + ptp_master)
    if(d.ptp){
      var p=d.ptp;
      updateDot('ptp-dot',p.state);
      setText('ptp-state-badge',p.port_state);
      setText('ptp-port',p.port_state);
      setText('ptp-class',p.clock_class||'—');
      setText('ptp-offset',p.offset_ns+' ns');
      setText('ptp-phc-offset',p.phc_offset_ns!==undefined?p.phc_offset_ns+' ns':'—');
      setText('ptp-delay',p.path_delay_ns+' ns');
      setText('ptp-gm',p.gm_id||'—');
      setText('ptp-domain',p.domain);
      setText('ptp-transport',p.transport);
      setText('ptp-slaves',p.slave_count);
      setText('ptp-pid',p.running?p.pid:'Stopped');
      setText('ptp-offset-val',p.offset_ns+' ns');
      updateBar('ptp-bar',offsetPct(p.offset_ns),offsetColor(p.offset_ns));
    }
    // Chrony (all roles)
    var c=d.chrony;
    updateDot('chrony-dot',c.state);
    setText('chrony-stratum-badge','Stratum '+c.stratum);
    setText('chrony-ref',c.ref_id||'—');
    setText('chrony-stratum',c.stratum);
    setText('chrony-offset',c.system_offset_us.toFixed(3)+' \u00b5s');
    setText('chrony-rms',c.rms_offset_us.toFixed(3)+' \u00b5s');
    setText('chrony-freq',c.frequency_ppm.toFixed(6)+' ppm');
    setText('chrony-skew',c.skew_ppm.toFixed(6)+' ppm');
    setText('chrony-rdelay',c.root_delay_us.toFixed(1)+' \u00b5s');
    setText('chrony-rdisp',c.root_dispersion_us.toFixed(1)+' \u00b5s');
    setText('chrony-leap',c.leap_status||'—');
    setText('chrony-sources',c.sources_count);
    setText('chrony-offset-val',c.system_offset_us.toFixed(3)+' \u00b5s');
    updateBar('chrony-bar',chronoOffPct(c.system_offset_us),chronoOffColor(c.system_offset_us));
    // Hub Connection (gps_source role)
    if(d.hub_conn){
      var hc=d.hub_conn;
      updateDot('hub-conn-dot',hc.state);
      setText('hub-conn-badge',hc.state);
      setText('hub-conn-url','{{cfg.node.hub_url|e}}'||'(not configured)');
      setText('hub-conn-state',hc.state);
      setText('hub-conn-last',hc.last_sent_ago!==null?hc.last_sent_ago+'s ago':'Never');
      setText('hub-conn-latency',hc.latency_ms?hc.latency_ms.toFixed(1)+' ms':'—');
      setText('hub-conn-total',hc.total_sent);
      setText('hub-conn-fails',hc.fail_count);
      setText('hub-conn-streak',hc.fail_streak||0);
    }
    // System (all roles)
    var s=d.system;
    updateDot('sys-dot',s.cpu_temp<75?'ok':s.cpu_temp<85?'warn':'error');
    setText('sys-model-badge',s.pi_model||'Host');
    setText('sys-uptime',fmtUptime(s.uptime_seconds));
    setText('sys-temp',s.cpu_temp.toFixed(1)+' \u00b0C');
    setText('sys-load',s.load);
    setText('sys-mem',s.mem_used_mb+' / '+s.mem_total_mb+' MB');
    setText('sys-disk',s.disk_used_gb.toFixed(1)+' / '+s.disk_total_gb.toFixed(1)+' GB');
    setText('sys-hostname',s.hostname);
    setText('sys-ip',s.ip_address);
    setText('sys-kernel',s.kernel);
    setText('sys-temp-val',s.cpu_temp.toFixed(1)+' \u00b0C');
    updateBar('sys-bar',tempPct(s.cpu_temp),tempColor(s.cpu_temp));
    // Log
    if(d.log&&d.log.length){
      var lb=document.getElementById('dash-log');
      if(lb){lb.textContent=d.log.join('\n');lb.scrollTop=lb.scrollHeight;}
    }
  }).catch(function(){});
}
setInterval(pollStatus,2000);
pollStatus();
// PTP start/stop
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-ptp-action]');if(!b)return;
  var action=b.dataset.ptpAction;
  _csrfFetch('/api/ptp/'+action,{method:'POST'}).then(function(){pollStatus();});
});
</script>
</body></html>"""


# ── Configuration ─────────────────────────────────────────────────────────────
CONFIG_TPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>PTPScope — Configuration</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="csrf-token" content="{{csrf_token()}}">
<style nonce="{{csp_nonce()}}">
:root{--bg:#07142b;--sur:#0d2346;--bor:#17345f;--acc:#17a8ff;--ok:#22c55e;--wn:#f59e0b;--al:#ef4444;--tx:#eef5ff;--mu:#8aa4c8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top, #12376f 0%, var(--bg) 38%, #05101f 100%);color:var(--tx);font-size:14px;position:relative}
body::before{content:"";position:fixed;right:28px;bottom:22px;width:280px;height:280px;background:url("/static/ptpscope_icon.png") no-repeat center/contain;opacity:.045;pointer-events:none;filter:drop-shadow(0 0 24px rgba(23,168,255,.10));z-index:0}
body>*{position:relative;z-index:1}
a{color:var(--acc);text-decoration:none}
header{background:linear-gradient(180deg, rgba(10,31,65,.96), rgba(9,24,48,.96));border-bottom:1px solid var(--bor);padding:12px 20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;box-shadow:0 10px 24px rgba(0,0,0,.18)}
header h1{font-size:17px;font-weight:700}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;background:#1e3a5f;color:var(--acc)}
.nav-active{background:var(--acc)!important;color:#fff!important}
nav{display:flex;gap:6px;margin-left:auto;flex-wrap:wrap}
.btn{display:inline-block;padding:5px 12px;border-radius:8px;font-size:13px;cursor:pointer;border:none;text-decoration:none;font-weight:600;color:var(--tx)}.btn:hover{filter:brightness(1.05)}
.bp{background:var(--acc);color:#fff}.bd{background:var(--al);color:#fff}.bg{background:var(--bor);color:var(--tx)}
.bs{padding:3px 9px;font-size:12px}
.pg{display:flex;min-height:calc(100vh - 46px)}
.sb{width:182px;flex-shrink:0;background:var(--sur);border-right:1px solid var(--bor);padding:10px 0;position:sticky;top:0;height:calc(100vh - 46px);overflow-y:auto}
.tb{display:flex;align-items:center;gap:8px;width:100%;padding:9px 15px;background:none;border:none;border-left:3px solid transparent;color:var(--mu);font-size:13px;cursor:pointer;text-align:left;transition:background .12s,color .12s}
.tb:hover{background:#1a2030;color:var(--tx)}
.tb.on{background:#1a2030;color:var(--tx);border-left-color:var(--acc);font-weight:600}
.ct{flex:1;padding:26px;max-width:680px}
.pn{display:none}.pn.on{display:block}
label{display:block;margin-top:13px;color:var(--mu);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
input[type=text],input[type=number],input[type=password],select,textarea{width:100%;margin-top:4px;padding:8px 10px;background:#173a69;border:1px solid var(--bor);border-radius:6px;color:var(--tx);font-size:14px}
textarea{min-height:80px;font-family:monospace;font-size:13px;resize:vertical}
.cr{display:flex;align-items:center;gap:8px;margin-top:10px}input[type=checkbox]{width:16px;height:16px;accent-color:var(--acc)}
.sec{margin-top:22px;padding-top:14px;border-top:1px solid var(--bor);font-weight:600;font-size:14px}
.sec:first-of-type{margin-top:0;padding-top:0;border-top:none}
.help{font-size:12px;color:var(--mu);margin-top:4px;line-height:1.5;font-style:italic}
.act{margin-top:22px;padding-top:16px;border-top:1px solid var(--bor);display:flex;gap:8px}
.fl{list-style:none;margin-bottom:14px}.fl li{padding:8px 12px;border-radius:6px;background:#1e3a5f;border-left:3px solid var(--acc);margin-bottom:5px;font-size:13px}
</style>
<link rel="icon" type="image/x-icon" href="/static/ptpscope_icon.png">
</head><body>
{{topnav("config")|safe}}
<div class="pg">
<div class="sb">
  <button class="tb on" id="b-ptp" onclick="st('ptp')">PTP</button>
  <button class="tb" id="b-gps" onclick="st('gps')">GPS</button>
  <button class="tb" id="b-chrony" onclick="st('chrony')">Chrony</button>
  <button class="tb" id="b-network" onclick="st('network')">Network</button>
  <button class="tb" id="b-security" onclick="st('security')">Security</button>
  <button class="tb" id="b-node" onclick="st('node')">Node</button>
  <button class="tb" id="b-update" onclick="st('update');setTimeout(checkForUpdates,200)">Update</button>
</div>
<div class="ct">
{% with msgs = get_flashed_messages() %}{% if msgs %}<ul class="fl">{% for m in msgs %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
<form method="post" action="/config">
<input type="hidden" name="_csrf_token" value="{{csrf_token()}}">
<input type="hidden" name="_panel" id="active-panel" value="ptp">
<!-- PTP Panel -->
<div class="pn on" id="p-ptp">
<div class="sec">PTP Grandmaster</div>
<label>Domain (0-127)<input type="number" name="ptp_domain" value="{{cfg.ptp.domain}}" min="0" max="127"></label>
<label>Network Interface
<select name="ptp_interface">
{% for iface in net_ifaces %}<option value="{{iface}}" {{'selected' if cfg.ptp.interface==iface}}>{{iface}}</option>
{% endfor %}
</select></label>
<label>Transport
<select name="ptp_transport">
<option value="UDPv4" {{'selected' if cfg.ptp.transport=='UDPv4'}}>UDPv4</option>
<option value="UDPv6" {{'selected' if cfg.ptp.transport=='UDPv6'}}>UDPv6</option>
<option value="L2" {{'selected' if cfg.ptp.transport=='L2'}}>IEEE 802.3 (L2)</option>
</select></label>
<label>Priority 1<input type="number" name="ptp_priority1" value="{{cfg.ptp.priority1}}" min="0" max="255"></label>
<label>Priority 2<input type="number" name="ptp_priority2" value="{{cfg.ptp.priority2}}" min="0" max="255"></label>
<label>Clock Class
<select name="ptp_clock_class">
<option value="6" {{'selected' if cfg.ptp.clock_class==6}}>6 — Locked to PRC (GPS)</option>
<option value="7" {{'selected' if cfg.ptp.clock_class==7}}>7 — Previously locked</option>
<option value="13" {{'selected' if cfg.ptp.clock_class==13}}>13 — Locked, app-specific</option>
<option value="52" {{'selected' if cfg.ptp.clock_class==52}}>52 — Degraded A</option>
<option value="187" {{'selected' if cfg.ptp.clock_class==187}}>187 — Default</option>
<option value="248" {{'selected' if cfg.ptp.clock_class==248}}>248 — Free-running</option>
</select></label>
<label>Clock Accuracy
<select name="ptp_clock_accuracy">
<option value="32" {{'selected' if cfg.ptp.clock_accuracy==0x20}}>0x20 — 25 ns</option>
<option value="33" {{'selected' if cfg.ptp.clock_accuracy==0x21}}>0x21 — 100 ns</option>
<option value="34" {{'selected' if cfg.ptp.clock_accuracy==0x22}}>0x22 — 250 ns</option>
<option value="35" {{'selected' if cfg.ptp.clock_accuracy==0x23}}>0x23 — 1 &micro;s</option>
<option value="36" {{'selected' if cfg.ptp.clock_accuracy==0x24}}>0x24 — 2.5 &micro;s</option>
<option value="49" {{'selected' if cfg.ptp.clock_accuracy==0x31}}>0x31 — &gt;10 s (unknown)</option>
</select></label>
<label>Time Source
<select name="ptp_time_source">
<option value="32" {{'selected' if cfg.ptp.time_source==0x20}}>0x20 — GPS</option>
<option value="48" {{'selected' if cfg.ptp.time_source==0x30}}>0x30 — Terrestrial Radio</option>
<option value="80" {{'selected' if cfg.ptp.time_source==0x50}}>0x50 — NTP</option>
<option value="160" {{'selected' if cfg.ptp.time_source==0xa0}}>0xa0 — Other</option>
</select></label>
<div class="cr"><input type="checkbox" name="ptp_auto_start" {{'checked' if cfg.ptp.auto_start}}><label style="margin:0">Auto-start ptp4l on boot</label></div>
<div class="act"><button type="submit" class="btn bp">Save PTP Settings</button></div>
</div>
<!-- GPS Panel -->
<div class="pn" id="p-gps">
<div class="sec">GPS Receiver</div>
<label>Serial Port<input type="text" name="gps_serial_port" value="{{cfg.gps.serial_port}}"></label>
<div class="help">/dev/serial0, /dev/ttyAMA0, or /dev/ttyUSB0 for USB GPS</div>
<label>Baud Rate
<select name="gps_baud_rate">
<option value="4800" {{'selected' if cfg.gps.baud_rate==4800}}>4800</option>
<option value="9600" {{'selected' if cfg.gps.baud_rate==9600}}>9600</option>
<option value="38400" {{'selected' if cfg.gps.baud_rate==38400}}>38400</option>
<option value="115200" {{'selected' if cfg.gps.baud_rate==115200}}>115200</option>
</select></label>
<label>PPS GPIO Pin<input type="number" name="gps_pps_gpio" value="{{cfg.gps.pps_gpio}}" min="0" max="27"></label>
<div class="help">Adafruit Ultimate GPS HAT uses GPIO 4 for PPS output</div>
<div class="cr"><input type="checkbox" name="gps_enable_gpsd" {{'checked' if cfg.gps.enable_gpsd}}><label style="margin:0">Enable GPSD (alternative GPS daemon)</label></div>
<div class="act"><button type="submit" class="btn bp">Save GPS Settings</button></div>
</div>
<!-- Chrony Panel -->
<div class="pn" id="p-chrony">
<div class="sec">Chrony / NTP</div>
<div class="cr"><input type="checkbox" name="chrony_gps_refclock" {{'checked' if cfg.chrony.gps_refclock}}><label style="margin:0">GPS SHM refclock (via GPSD)</label></div>
<div class="cr"><input type="checkbox" name="chrony_pps_refclock" {{'checked' if cfg.chrony.pps_refclock}}><label style="margin:0">PPS refclock (/dev/pps0)</label></div>
<label>GPS Source IP<input type="text" name="chrony_gps_server_ip" value="{{cfg.chrony.gps_server_ip}}" placeholder="e.g. 192.168.1.50"></label>
<div class="help">PTP Master: enter the GPS Source Pi's IP to use as preferred NTP server</div>
<label>NTP Servers (one per line)<textarea name="chrony_ntp_servers">{{cfg.chrony.ntp_servers}}</textarea></label>
<div class="cr"><input type="checkbox" name="chrony_makestep" {{'checked' if cfg.chrony.makestep}}><label style="margin:0">Allow large initial time step (makestep 1 3)</label></div>
<div class="cr"><input type="checkbox" name="chrony_allow_clients" {{'checked' if cfg.chrony.allow_clients}}><label style="margin:0">Allow NTP clients</label></div>
<label>Allowed Subnet<input type="text" name="chrony_allow_subnet" value="{{cfg.chrony.allow_subnet}}"></label>
<div class="help">e.g. 192.168.1.0/24</div>
<div class="act"><button type="submit" class="btn bp">Save &amp; Apply Chrony Settings</button></div>
<div class="help">Saves to PTPScope config and writes /etc/chrony/chrony.conf, then restarts chrony.</div>
</div>
<!-- Network Panel -->
<div class="pn" id="p-network">
<div class="sec">Web Interface</div>
<label>Web UI Port<input type="number" name="web_port" value="{{cfg.web_port}}" min="1" max="65535"></label>
<label>Bind Address<input type="text" name="bind_address" value="{{cfg.bind_address}}"></label>
<div class="help">0.0.0.0 for all interfaces, 127.0.0.1 for localhost only</div>
<div class="act"><button type="submit" class="btn bp">Save Network Settings</button></div>
</div>
<!-- Security Panel -->
<div class="pn" id="p-security">
<div class="sec">Authentication</div>
<div class="cr"><input type="checkbox" name="auth_enabled" {{'checked' if cfg.auth.enabled}}><label style="margin:0">Enable login</label></div>
<label>Username<input type="text" name="auth_username" value="{{cfg.auth.username}}"></label>
<label>New Password<input type="password" name="auth_password" placeholder="Leave blank to keep current"></label>
<label>Session Timeout (hours)<input type="number" name="session_timeout_hrs" value="{{cfg.session_timeout_hrs}}" min="1" max="720"></label>
<div class="act"><button type="submit" class="btn bp">Save Security Settings</button></div>
</div>
<!-- Node Panel -->
<div class="pn" id="p-node">
<div class="sec">Node Role</div>
<label>Role
<select name="node_role" onchange="updateNodeRole(this.value)">
<option value="standalone" {{'selected' if cfg.node.role=='standalone' else ''}}>Standalone — GPS, PTP and Chrony all on this machine</option>
<option value="gps_source" {{'selected' if cfg.node.role=='gps_source' else ''}}>GPS Source — Raspberry Pi with GPS HAT, sends heartbeats</option>
<option value="ptp_master" {{'selected' if cfg.node.role=='ptp_master' else ''}}>PTP Master — hardware PTP NIC machine, receives heartbeats</option>
</select></label>
<div class="help" id="node-role-help">—</div>
<div id="node-remote-fields">
<label>Site Name<input type="text" name="node_site_name" value="{{cfg.node.site_name}}"></label>
<div class="help">Unique name for this node, e.g. "gps-pi" or "ptp-master"</div>
<label>Secret Key<input type="text" name="node_secret_key" value="{{cfg.node.secret_key}}" id="node-secret-input" autocomplete="off"></label>
<div class="help">Shared HMAC secret — must match on both nodes. Leave blank to disable authentication.</div>
<button type="button" class="btn bg bs" id="node-gen-secret-btn" style="margin-top:6px">Generate Key</button>
<div id="node-hub-url-wrap">
<label>PTP Master URL<input type="text" name="node_hub_url" value="{{cfg.node.hub_url}}"></label>
<div class="help">URL of the PTP Master web UI, e.g. http://192.168.1.100:5001 — only used on GPS Source node.</div>
</div>
</div>
<div class="help" style="margin-top:14px;color:var(--wn)">&#9888; Restart PTPScope after changing the role for it to take effect.</div>
<div class="act"><button type="submit" class="btn bp">Save Node Settings</button></div>
</div>
</form>

<!-- Update Panel (outside form — no submit needed) -->
<div class="pn" id="p-update">
<div class="sec">🔄 Software Update</div>
<p class="help" style="margin-bottom:12px">PTPScope checks GitHub for updates every 6 hours. Use the button below to check right now.</p>
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
  <button id="upd-check-btn" type="button" class="btn bp" style="font-size:13px">🔍 Check for Updates</button>
  <span id="upd-status" style="font-size:12px;color:var(--mu)">Current: <strong style="color:var(--tx)">{{build}}</strong></span>
</div>
<div id="upd-result" style="margin-top:12px;font-size:13px;display:none"></div>
</div>

</div>
</div>
<script nonce="{{csp_nonce()}}">
function st(id){
  document.querySelectorAll('.pn').forEach(function(p){p.classList.remove('on');});
  document.querySelectorAll('.tb').forEach(function(b){b.classList.remove('on');});
  var p=document.getElementById('p-'+id),b=document.getElementById('b-'+id);
  if(p)p.classList.add('on');if(b)b.classList.add('on');
  document.getElementById('active-panel').value=id;
  history.replaceState(null,'','#'+id);
}
(function(){var h=location.hash.slice(1);if(h)st(h);})();
// Node role logic
var _nodeRoleHelp={
  standalone:'Standalone mode: GPS, PTP, and Chrony all run on this machine (original behaviour).',
  gps_source:'GPS Source mode: reads GPS/PPS, runs Chrony as a stratum-1 NTP server, and sends heartbeats to the PTP Master every 10 s.',
  ptp_master:'PTP Master mode: runs ptp4l + phc2sys as a PTP Grandmaster, receives GPS heartbeats from the GPS Source node.'
};
function updateNodeRole(v){
  var rf=document.getElementById('node-remote-fields');
  var hw=document.getElementById('node-hub-url-wrap');
  var help=document.getElementById('node-role-help');
  if(help)help.textContent=_nodeRoleHelp[v]||'';
  if(rf)rf.style.display=v==='standalone'?'none':'block';
  if(hw)hw.style.display=v==='gps_source'?'block':'none';
}
updateNodeRole('{{cfg.node.role}}');
document.getElementById('node-gen-secret-btn').addEventListener('click',function(){
  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var arr=crypto.getRandomValues(new Uint8Array(40));
  var key=Array.from(arr).map(function(b){return chars[b%chars.length];}).join('');
  document.getElementById('node-secret-input').value=key;
});

// ── Self-update UI ──────────────────────────────────────────────────────────
function _csrf(){
  return (document.querySelector('meta[name="csrf-token"]')||{}).content
      || (document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)||[])[1]
      || '';
}

function checkForUpdates(){
  var btn=document.getElementById('upd-check-btn');
  var res=document.getElementById('upd-result');
  if(!btn||!res) return;
  btn.disabled=true; btn.textContent='Checking…';
  res.style.display='none';
  fetch('/api/version_check/refresh',{method:'POST',headers:{'X-CSRFToken':_csrf()}})
    .then(function(r){return r.json();}).then(function(){
      setTimeout(function(){
        fetch('/api/version_check').then(function(r){return r.json();}).then(function(d){
          btn.disabled=false; btn.textContent='🔍 Check for Updates';
          res.style.display='';
          if(d.error && !d.latest){
            res.innerHTML='<span style="color:var(--wn)">⚠ Could not check: <code style="font-size:11px;color:#fde68a">'+d.error+'</code></span>';
          } else if(d.update_available){
            _showUpd(d.latest, d.current);
          } else {
            res.innerHTML='<span style="color:var(--ok)">✓ You are on the latest version ('+d.current+').</span>';
          }
        });
      }, 4000);
    }).catch(function(){
      btn.disabled=false; btn.textContent='🔍 Check for Updates';
      res.style.display=''; res.innerHTML='<span style="color:var(--al)">Request failed — check network.</span>';
    });
}

function _showUpd(latest, current){
  var res=document.getElementById('upd-result');
  if(!res) return;
  res.style.display='';
  res.innerHTML=
    '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:10px 14px;background:#1c3a10;border:1px solid #4ade80;border-radius:8px">'
    +'<span style="color:#fde68a">⬆ <strong style="color:#fff">PTPScope '+latest+'</strong> is available'
    +(current?' <span style="color:var(--mu);font-size:11px">(you are on '+current+')</span>':'')
    +'</span>'
    +'<button class="btn" style="background:#166534;color:#fff;font-size:12px" data-action="upd-confirm" data-ver="'+latest+'" data-current="'+(current||'')+'">⬆ Apply Update &amp; Restart</button>'
    +'</div>';
}

function _confirmUpd(ver, current){
  var res=document.getElementById('upd-result');
  if(!res) return;
  res.innerHTML=
    '<div style="padding:10px 14px;background:#2a1505;border:1px solid #f97316;border-radius:8px">'
    +'<p style="color:#fde68a;font-size:13px;margin:0 0 10px">⚠ Apply <strong style="color:#fff">PTPScope '+ver+'</strong> and restart?'
    +' <span style="font-size:11px;color:var(--mu)">The page will reload automatically (~15 s).</span></p>'
    +'<div style="display:flex;gap:10px;flex-wrap:wrap">'
    +'<button class="btn" style="background:#166534;color:#fff;font-size:12px" data-action="upd-apply" data-ver="'+ver+'">✓ Apply Update</button>'
    +'<button class="btn" style="background:#374151;color:#fff;font-size:12px" data-action="upd-cancel" data-ver="'+ver+'" data-current="'+(current||'')+'">✗ Cancel</button>'
    +'</div></div>';
}

function _doUpd(ver){
  var res=document.getElementById('upd-result');
  if(!res) return;
  res.innerHTML='<span style="color:var(--acc)">⏳ Downloading and applying update…</span>';
  fetch('/api/update/apply',{method:'POST',headers:{'X-CSRFToken':_csrf()}})
    .then(function(r){return r.json();}).then(function(d){
      if(d.ok){
        res.innerHTML='<span style="color:var(--ok)">✓ Updated ('+d.from_version+' → '+d.to_version+'). Restarting… <span id="upd-cd">--</span></span>';
        var t0=Date.now();
        function poll(){
          var s=Math.round((Date.now()-t0)/1000);
          var el=document.getElementById('upd-cd');
          if(el) el.textContent=s+'s';
          fetch('/',{method:'HEAD',cache:'no-store'})
            .then(function(r){if(r.ok)location.reload(); else throw 0;})
            .catch(function(){
              if(Date.now()-t0<90000) setTimeout(poll,3000);
              else if(el) el.parentElement.innerHTML='<span style="color:var(--wn)">⚠ No response after 90 s — try reloading.</span>';
            });
        }
        setTimeout(poll,5000);
      } else {
        res.innerHTML='<span style="color:var(--al)">✗ '+(d.error||'Unknown error')+'</span>';
      }
    }).catch(function(e){
      res.innerHTML='<span style="color:var(--al)">✗ '+e.message+'</span>';
    });
}

document.addEventListener('click',function(e){
  var btn=e.target.closest('#upd-result [data-action]');
  if(!btn) return;
  var a=btn.dataset.action, v=btn.dataset.ver, c=btn.dataset.current;
  if(a==='upd-confirm') _confirmUpd(v,c);
  else if(a==='upd-apply') _doUpd(v);
  else if(a==='upd-cancel') _showUpd(v,c);
});
var _ub=document.getElementById('upd-check-btn');
if(_ub) _ub.addEventListener('click',checkForUpdates);
</script>
</body></html>"""


# ── Logs ──────────────────────────────────────────────────────────────────────
LOGS_TPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>PTPScope — Logs</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="csrf-token" content="{{csrf_token()}}">
<style nonce="{{csp_nonce()}}">
:root{--bg:#07142b;--sur:#0d2346;--bor:#17345f;--acc:#17a8ff;--ok:#22c55e;--wn:#f59e0b;--al:#ef4444;--tx:#eef5ff;--mu:#8aa4c8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top, #12376f 0%, var(--bg) 38%, #05101f 100%);color:var(--tx);font-size:14px;position:relative;min-height:100vh}
body::before{content:"";position:fixed;right:28px;bottom:22px;width:280px;height:280px;background:url("/static/ptpscope_icon.png") no-repeat center/contain;opacity:.045;pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
a{color:var(--acc);text-decoration:none}
header{background:linear-gradient(180deg, rgba(10,31,65,.96), rgba(9,24,48,.96));border-bottom:1px solid var(--bor);padding:12px 20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;box-shadow:0 10px 24px rgba(0,0,0,.18)}
header h1{font-size:17px;font-weight:700}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;background:#1e3a5f;color:var(--acc)}
.nav-active{background:var(--acc)!important;color:#fff!important}
nav{display:flex;gap:6px;margin-left:auto;flex-wrap:wrap}
.btn{display:inline-block;padding:5px 12px;border-radius:8px;font-size:13px;cursor:pointer;border:none;text-decoration:none;font-weight:600;color:var(--tx)}.btn:hover{filter:brightness(1.05)}
.bp{background:var(--acc);color:#fff}.bd{background:var(--al);color:#fff}.bg{background:var(--bor);color:var(--tx)}
.bs{padding:3px 9px;font-size:12px}
main{padding:16px;max-width:1440px;margin:0 auto}
.tabs{display:flex;gap:6px;margin-bottom:12px}
.tab{padding:6px 14px;border-radius:8px;background:var(--bor);color:var(--mu);border:none;cursor:pointer;font-size:13px;font-weight:600}
.tab.active{background:var(--acc);color:#fff}
.logbox{background:var(--sur);border:1px solid var(--bor);border-radius:8px;padding:12px;font-family:monospace;font-size:11px;height:calc(100vh - 200px);overflow-y:auto;white-space:pre-wrap;word-break:break-all}
.log-bar{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.cr{display:flex;align-items:center;gap:6px}input[type=checkbox]{width:16px;height:16px;accent-color:var(--acc)}
</style>
<link rel="icon" type="image/x-icon" href="/static/ptpscope_icon.png">
</head><body>
{{topnav("logs")|safe}}
<main>
<div class="tabs">
  <button class="tab active" id="tab-ptp4l" onclick="switchTab('ptp4l')">PTP4L Output</button>
  <button class="tab" id="tab-app" onclick="switchTab('app')">Application Log</button>
</div>
<div class="log-bar">
  <div class="cr"><input type="checkbox" id="autoscroll" checked><label style="font-size:12px;color:var(--mu);margin:0">Auto-scroll</label></div>
  <button class="btn bg bs" id="clear-btn">Clear</button>
</div>
<div class="logbox" id="log-ptp4l">Loading ptp4l output...</div>
<div class="logbox" id="log-app" style="display:none">Loading app log...</div>
</main>
<script nonce="{{csp_nonce()}}">
function _csrfFetch(url,opts){
  opts=opts||{};if(!opts.headers)opts.headers={};
  var t=(document.querySelector('meta[name="csrf-token"]')||{}).content||"";
  opts.headers["X-CSRFToken"]=t;return fetch(url,opts);
}
var activeTab='ptp4l';
function switchTab(t){
  activeTab=t;
  document.querySelectorAll('.tab').forEach(function(b){b.classList.remove('active');});
  document.getElementById('tab-'+t).classList.add('active');
  document.getElementById('log-ptp4l').style.display=t==='ptp4l'?'block':'none';
  document.getElementById('log-app').style.display=t==='app'?'block':'none';
}
function pollLogs(){
  fetch('/api/logs').then(function(r){return r.json();}).then(function(d){
    var lp=document.getElementById('log-ptp4l');
    var la=document.getElementById('log-app');
    if(lp&&d.ptp4l)lp.textContent=d.ptp4l.join('\n');
    if(la&&d.app)la.textContent=d.app.join('\n');
    var auto=document.getElementById('autoscroll');
    if(auto&&auto.checked){
      var active=activeTab==='ptp4l'?lp:la;
      if(active)active.scrollTop=active.scrollHeight;
    }
  }).catch(function(){});
}
setInterval(pollLogs,2000);
pollLogs();
document.getElementById('clear-btn').addEventListener('click',function(){
  _csrfFetch('/api/logs/clear',{method:'POST'}).then(pollLogs);
});
</script>
</body></html>"""


# ── History ───────────────────────────────────────────────────────────────────
HISTORY_TPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>PTPScope — History</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style nonce="{{csp_nonce()}}">
:root{--bg:#07142b;--sur:#0d2346;--bor:#17345f;--acc:#17a8ff;--ok:#22c55e;--wn:#f59e0b;--al:#ef4444;--tx:#eef5ff;--mu:#8aa4c8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top, #12376f 0%, var(--bg) 38%, #05101f 100%);color:var(--tx);font-size:14px;position:relative;min-height:100vh}
body::before{content:"";position:fixed;right:28px;bottom:22px;width:280px;height:280px;background:url("/static/ptpscope_icon.png") no-repeat center/contain;opacity:.045;pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
a{color:var(--acc);text-decoration:none}
header{background:linear-gradient(180deg, rgba(10,31,65,.96), rgba(9,24,48,.96));border-bottom:1px solid var(--bor);padding:12px 20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;box-shadow:0 10px 24px rgba(0,0,0,.18)}
header h1{font-size:17px;font-weight:700}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;background:#1e3a5f;color:var(--acc)}
.nav-active{background:var(--acc)!important;color:#fff!important}
nav{display:flex;gap:6px;margin-left:auto;flex-wrap:wrap}
.btn{display:inline-block;padding:5px 12px;border-radius:8px;font-size:13px;cursor:pointer;border:none;text-decoration:none;font-weight:600;color:var(--tx)}.btn:hover{filter:brightness(1.05)}
.bp{background:var(--acc);color:#fff}.bg{background:var(--bor);color:var(--tx)}
.bs{padding:3px 9px;font-size:12px}
main{padding:16px;max-width:1440px;margin:0 auto}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
select{padding:8px 10px;background:#173a69;border:1px solid var(--bor);border-radius:6px;color:var(--tx);font-size:14px}
.range-btns{display:flex;gap:4px}
.range-btn{padding:5px 12px;border-radius:6px;background:var(--bor);color:var(--mu);border:none;cursor:pointer;font-size:12px;font-weight:600}
.range-btn.active{background:var(--acc);color:#fff}
.chart-wrap{background:var(--sur);border:1px solid var(--bor);border-radius:12px;padding:14px;margin-top:10px}
canvas{width:100%;height:200px;display:block}
.chart-status{text-align:center;color:var(--mu);font-size:12px;margin-top:8px}
</style>
<link rel="icon" type="image/x-icon" href="/static/ptpscope_icon.png">
</head><body>
{{topnav("history")|safe}}
<main>
<div class="toolbar">
  <select id="metric-sel">
    <option value="clock_offset_ns">Clock Offset (ns)</option>
    <option value="path_delay_ns">Path Delay (ns)</option>
    <option value="chrony_offset_us">Chrony Offset (&micro;s)</option>
    <option value="chrony_freq_ppm">Chrony Frequency (ppm)</option>
    <option value="gps_hdop">GPS HDOP</option>
    <option value="gps_satellites">GPS Satellites</option>
    <option value="cpu_temp">CPU Temperature (&deg;C)</option>
  </select>
  <div class="range-btns">
    <button class="range-btn active" data-h="1">1h</button>
    <button class="range-btn" data-h="6">6h</button>
    <button class="range-btn" data-h="24">24h</button>
  </div>
</div>
<div class="chart-wrap">
  <canvas id="chart"></canvas>
  <div class="chart-status" id="chart-status"></div>
</div>
</main>
<script nonce="{{csp_nonce()}}">
var colorMap={clock_offset_ns:'#60a5fa',path_delay_ns:'#a78bfa',chrony_offset_us:'#34d399',chrony_freq_ppm:'#fbbf24',gps_hdop:'#f87171',gps_satellites:'#38bdf8',cpu_temp:'#fb923c'};
function drawMetricChart(canvas,points,color){
  var W=canvas.offsetWidth||400,H=200;
  canvas.width=W;canvas.height=H;
  var ctx=canvas.getContext('2d');
  var pad={t:8,r:8,b:24,l:52};
  var cw=W-pad.l-pad.r,ch=H-pad.t-pad.b;
  ctx.clearRect(0,0,W,H);
  if(!points||points.length<2){
    ctx.fillStyle='rgba(255,255,255,0.25)';ctx.font='11px sans-serif';ctx.textAlign='center';
    ctx.fillText(points&&points.length===1?'Only 1 point — wait for more data':'No data',W/2,H/2);
    return;
  }
  var vals=points.map(function(p){return p[1];});
  var times=points.map(function(p){return p[0];});
  var minV=Math.min.apply(null,vals),maxV=Math.max.apply(null,vals);
  var rng=maxV-minV||1;
  minV-=rng*0.08;maxV+=rng*0.08;rng=maxV-minV;
  var minT=times[0],maxT=times[times.length-1],tRng=maxT-minT||1;
  ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;
  ctx.fillStyle='rgba(255,255,255,0.35)';ctx.font='9px monospace';ctx.textAlign='right';
  for(var g=0;g<=4;g++){
    var gy=pad.t+ch*g/4;
    ctx.beginPath();ctx.moveTo(pad.l,gy);ctx.lineTo(pad.l+cw,gy);ctx.stroke();
    ctx.fillText((maxV-rng*g/4).toFixed(1),pad.l-3,gy+3);
  }
  ctx.fillStyle='rgba(255,255,255,0.3)';ctx.textAlign='center';
  for(var tx=0;tx<=4;tx++){
    var gx=pad.l+cw*tx/4,gt=minT+tRng*tx/4,d=new Date(gt*1000);
    ctx.fillText(('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2),gx,H-4);
  }
  ctx.beginPath();
  points.forEach(function(p,i){
    var x=pad.l+(p[0]-minT)/tRng*cw,y=pad.t+(1-(p[1]-minV)/rng)*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  var lx=pad.l+(points[points.length-1][0]-minT)/tRng*cw;
  ctx.lineTo(lx,pad.t+ch);ctx.lineTo(pad.l,pad.t+ch);ctx.closePath();
  ctx.fillStyle=color.replace(/^#/,'').length===6
    ?'rgba('+parseInt(color.slice(1,3),16)+','+parseInt(color.slice(3,5),16)+','+parseInt(color.slice(5,7),16)+',0.13)'
    :'rgba(96,165,250,0.13)';
  ctx.fill();
  ctx.beginPath();
  points.forEach(function(p,i){
    var x=pad.l+(p[0]-minT)/tRng*cw,y=pad.t+(1-(p[1]-minV)/rng)*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  ctx.strokeStyle=color;ctx.lineWidth=1.5;ctx.lineJoin='round';ctx.stroke();
}
function loadChart(){
  var metric=document.getElementById('metric-sel').value;
  var hours=parseFloat((document.querySelector('.range-btn.active')||{dataset:{h:1}}).dataset.h);
  var status=document.getElementById('chart-status');
  status.textContent='Loading...';
  fetch('/api/metrics?metric='+encodeURIComponent(metric)+'&hours='+hours)
    .then(function(r){return r.json();})
    .then(function(d){
      status.textContent=d.points?d.points.length+' points':'';
      drawMetricChart(document.getElementById('chart'),d.points,colorMap[metric]||'#60a5fa');
    })
    .catch(function(){status.textContent='Failed to load';});
}
document.querySelectorAll('.range-btn').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.range-btn').forEach(function(x){x.classList.remove('active');});
    b.classList.add('active');loadChart();
  });
});
document.getElementById('metric-sel').addEventListener('change',loadChart);
loadChart();
</script>
</body></html>"""


# ── Login ─────────────────────────────────────────────────────────────────────
LOGIN_TPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Login — PTPScope</title>
<meta name="csrf-token" content="{{csrf_token()}}">
<style nonce="{{csp_nonce()}}">
:root{--bg:#0d0f14;--sur:#161a22;--bor:#252b38;--acc:#4f9cf9;--tx:#e2e8f0;--mu:#64748b}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top, #12376f 0%, var(--bg) 38%, #05101f 100%);color:var(--tx);font-size:14px;display:flex;align-items:center;justify-content:center;min-height:100vh;position:relative}
body::before{content:"";position:fixed;right:28px;bottom:22px;width:320px;height:320px;background:url("/static/ptpscope_icon.png") no-repeat center/contain;opacity:.05;pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
.box{background:var(--sur);border:1px solid var(--bor);border-radius:12px;padding:32px;width:100%;max-width:380px;box-shadow:0 20px 60px rgba(0,0,0,.28)}
h1{font-size:20px;margin-bottom:6px;text-align:center}
.sub{color:var(--mu);font-size:13px;text-align:center;margin-bottom:24px}
label{display:block;margin-top:14px;color:var(--mu);font-size:12px;font-weight:600;text-transform:uppercase}
input[type=text],input[type=password]{width:100%;margin-top:4px;padding:9px 11px;background:#173a69;border:1px solid var(--bor);border-radius:7px;color:var(--tx);font-size:14px}
.btn{width:100%;margin-top:20px;padding:10px;background:var(--acc);color:#fff;border:none;border-radius:7px;font-size:14px;font-weight:600;cursor:pointer}
.err{margin-top:12px;padding:9px 12px;background:#3a0f0f;border-left:3px solid #ef4444;border-radius:5px;font-size:13px;color:#fca5a5}
.ok{margin-top:12px;padding:9px 12px;background:#1a2a0f;border-left:3px solid #22c55e;border-radius:5px;font-size:13px;color:#86efac}
</style>
<link rel="icon" type="image/x-icon" href="/static/ptpscope_icon.png">
</head><body>
<div class="box">
  <h1>PTPScope</h1>
  <div class="sub" style="margin-bottom:8px">GPS PTP Grandmaster</div>
  <div class="sub">{{build}}</div>
  {% if locked %}
  <div class="err">Too many failed attempts. Try again in {{locked_mins}} minute{{'s' if locked_mins!=1}}.</div>
  {% else %}
  {% if error %}<div class="err">{{error}}</div>{% endif %}
  {% if first_login %}<div class="ok">First login — please set a new password.</div>{% endif %}
  <form method="post" autocomplete="on"><input type="hidden" name="_csrf_token" value="{{csrf_token()}}">
    <label>Username<input type="text" name="username" value="{{username or ''}}" autofocus autocomplete="username"></label>
    <label>Password<input type="password" name="password" autocomplete="current-password"></label>
    {% if first_login %}
    <label>New Password<input type="password" name="new_password" autocomplete="new-password" placeholder="Min 8 characters"></label>
    <label>Confirm Password<input type="password" name="confirm_password" autocomplete="new-password"></label>
    {% endif %}
    <button class="btn" type="submit">{% if first_login %}Set Password & Sign In{% else %}Sign In{% endif %}</button>
  </form>
  {% endif %}
  <div style="margin-top:18px;text-align:center;font-size:11px;color:var(--mu)">PTPScope {{build}}</div>
</div></body></html>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  PYTHON BACKEND
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import time
import json
import re
import signal
import socket
import struct
import hashlib
import hmac as _hmac
import secrets
import base64
import logging
import functools
import threading
import subprocess
import collections
import sqlite3 as _sqlite3
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

# ── Optional imports ──────────────────────────────────────────────────────────
serial_mod = None
try:
    import serial as serial_mod
except ImportError:
    pass

from flask import (Flask, render_template_string, request, redirect,
                   url_for, flash, session, jsonify, Response, g)
from markupsafe import Markup

# ── Constants ─────────────────────────────────────────────────────────────────
GPS_DEFAULT_PORT     = "/dev/serial0"
GPS_DEFAULT_BAUD     = 9600
GPS_PPS_GPIO         = 4
GPS_POLL_INTERVAL    = 1.0

PTP_CONF_PATH        = "/tmp/ptpscope_ptp4l.conf"

_GH_RAW_VER_URL      = "https://raw.githubusercontent.com/itconor/PtPscope/main/ptpscope.py"
_GH_API_RELEASES_URL = "https://api.github.com/repos/itconor/PtPscope/releases/latest"
PTP_DEFAULT_DOMAIN   = 0
PTP_DEFAULT_IFACE    = "eth0"
PTP_DEFAULT_TRANSPORT = "UDPv4"
PTP_POLL_INTERVAL    = 1.0

CHRONY_POLL_INTERVAL = 5.0
SYS_POLL_INTERVAL    = 10.0

METRICS_RETENTION_DAYS = 90
METRICS_FLUSH_INTERVAL = 60

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "ptpscope_config.json")
METRICS_DB  = os.path.join(BASE_DIR, "ptpscope_metrics.db")
STATIC_DIR  = os.path.join(BASE_DIR, "static")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GpsConfig:
    serial_port: str = "/dev/serial0"
    baud_rate: int = 9600
    pps_gpio: int = 4
    enable_gpsd: bool = False

@dataclass
class PtpConfig:
    domain: int = 0
    interface: str = "eth0"
    transport: str = "UDPv4"
    priority1: int = 128
    priority2: int = 128
    clock_class: int = 6
    clock_accuracy: int = 0x21
    time_source: int = 0x20
    auto_start: bool = True

@dataclass
class ChronyConfig:
    gps_refclock: bool = True
    pps_refclock: bool = True
    ntp_servers: str = ""
    gps_server_ip: str = ""          # PTP Master: GPS Source IP for "server <ip> iburst prefer"
    makestep: bool = True             # makestep 1 3 — allow large initial correction
    allow_clients: bool = False
    allow_subnet: str = "192.168.1.0/24"

@dataclass
class AuthConfig:
    enabled: bool = False
    username: str = "admin"
    password_hash: str = ""
    first_login: bool = True

@dataclass
class NodeConfig:
    role: str = "standalone"   # standalone | gps_source | ptp_master
    site_name: str = ""
    secret_key: str = ""
    hub_url: str = ""          # gps_source: URL of ptp_master web UI

@dataclass
class AppConfig:
    gps: GpsConfig = field(default_factory=GpsConfig)
    ptp: PtpConfig = field(default_factory=PtpConfig)
    chrony: ChronyConfig = field(default_factory=ChronyConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    node: NodeConfig = field(default_factory=NodeConfig)
    web_port: int = 5001
    bind_address: str = "0.0.0.0"
    session_timeout_hrs: int = 12


def load_config() -> AppConfig:
    cfg = AppConfig()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                d = json.load(f)
            g = d.get("gps", {})
            cfg.gps = GpsConfig(
                serial_port=g.get("serial_port", "/dev/serial0"),
                baud_rate=int(g.get("baud_rate", 9600)),
                pps_gpio=int(g.get("pps_gpio", 4)),
                enable_gpsd=bool(g.get("enable_gpsd", False)),
            )
            p = d.get("ptp", {})
            cfg.ptp = PtpConfig(
                domain=int(p.get("domain", 0)),
                interface=p.get("interface", "eth0"),
                transport=p.get("transport", "UDPv4"),
                priority1=int(p.get("priority1", 128)),
                priority2=int(p.get("priority2", 128)),
                clock_class=int(p.get("clock_class", 6)),
                clock_accuracy=int(p.get("clock_accuracy", 0x21)),
                time_source=int(p.get("time_source", 0x20)),
                auto_start=bool(p.get("auto_start", True)),
            )
            c = d.get("chrony", {})
            # GPS/PPS refclocks only make sense on nodes with GPS hardware
            _has_gps = cfg.node.role in ("gps_source", "standalone")
            cfg.chrony = ChronyConfig(
                gps_refclock=bool(c.get("gps_refclock", _has_gps)),
                pps_refclock=bool(c.get("pps_refclock", _has_gps)),
                ntp_servers=c.get("ntp_servers", ""),
                gps_server_ip=c.get("gps_server_ip", ""),
                makestep=bool(c.get("makestep", True)),
                allow_clients=bool(c.get("allow_clients", False)),
                allow_subnet=c.get("allow_subnet", "192.168.1.0/24"),
            )
            a = d.get("auth", {})
            cfg.auth = AuthConfig(
                enabled=bool(a.get("enabled", False)),
                username=a.get("username", "admin"),
                password_hash=a.get("password_hash", ""),
                first_login=bool(a.get("first_login", True)),
            )
            cfg.web_port = int(d.get("web_port", 5001))
            cfg.bind_address = d.get("bind_address", "0.0.0.0")
            cfg.session_timeout_hrs = int(d.get("session_timeout_hrs", 12))
            n = d.get("node", {})
            cfg.node = NodeConfig(
                role=n.get("role", "standalone"),
                site_name=n.get("site_name", ""),
                secret_key=n.get("secret_key", ""),
                hub_url=n.get("hub_url", ""),
            )
        except Exception as e:
            print(f"[Config] Error loading config: {e}")
    return cfg


def save_config(cfg: AppConfig):
    d = {
        "gps": asdict(cfg.gps),
        "ptp": asdict(cfg.ptp),
        "chrony": asdict(cfg.chrony),
        "auth": asdict(cfg.auth),
        "node": asdict(cfg.node),
        "web_port": cfg.web_port,
        "bind_address": cfg.bind_address,
        "session_timeout_hrs": cfg.session_timeout_hrs,
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(d, f, indent=2)
        os.chmod(CONFIG_PATH, 0o600)
    except Exception as e:
        print(f"[Config] Error saving config: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  METRICS DB
# ═══════════════════════════════════════════════════════════════════════════════

class MetricsDB:
    def __init__(self, path: str):
        self._path = path
        self._lock = threading.Lock()
        self._conn: Optional[_sqlite3.Connection] = None
        self._init_db()

    def _connect(self) -> _sqlite3.Connection:
        conn = _sqlite3.connect(self._path, check_same_thread=False, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self):
        try:
            with self._lock:
                conn = self._connect()
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS metric_history (
                        metric  TEXT NOT NULL,
                        ts      REAL NOT NULL,
                        value   REAL NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_mh_lookup
                        ON metric_history(metric, ts);
                """)
                conn.commit()
                self._conn = conn
        except Exception as e:
            print(f"[MetricsDB] Init error: {e}")

    def write(self, rows: list):
        if not rows:
            return
        try:
            with self._lock:
                if self._conn is None:
                    self._conn = self._connect()
                self._conn.executemany(
                    "INSERT INTO metric_history(metric, ts, value) VALUES(?,?,?)",
                    rows
                )
                self._conn.commit()
        except Exception as e:
            print(f"[MetricsDB] Write error: {e}")
            self._conn = None

    def query(self, metric: str, hours: float = 24.0) -> list:
        since = time.time() - hours * 3600
        try:
            with self._lock:
                if self._conn is None:
                    self._conn = self._connect()
                cur = self._conn.execute(
                    "SELECT ts, value FROM metric_history "
                    "WHERE metric=? AND ts>=? ORDER BY ts ASC",
                    (metric, since)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"[MetricsDB] Query error: {e}")
            self._conn = None
            return []

    def prune(self, days: int = METRICS_RETENTION_DAYS):
        cutoff = time.time() - days * 86400
        try:
            with self._lock:
                if self._conn is None:
                    self._conn = self._connect()
                self._conn.execute("DELETE FROM metric_history WHERE ts<?", (cutoff,))
                self._conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                self._conn.commit()
        except Exception as e:
            print(f"[MetricsDB] Prune error: {e}")
            self._conn = None


# ═══════════════════════════════════════════════════════════════════════════════
#  SECURITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _hash_password(pw: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 260000)
    return salt.hex() + ":" + dk.hex()

def _verify_password(pw: str, stored: str) -> bool:
    if ":" not in stored:
        return False
    salt_hex, dk_hex = stored.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 260000)
    return _hmac.compare_digest(dk.hex(), dk_hex)

def _csrf_token() -> str:
    if "_csrf" not in session:
        session["_csrf"] = hashlib.sha256(os.urandom(32)).hexdigest()
    return session["_csrf"]

def _csrf_valid() -> bool:
    token = session.get("_csrf", "")
    if not token:
        return False
    submitted = request.form.get("_csrf_token", "") or request.headers.get("X-CSRFToken", "")
    return _hmac.compare_digest(token, submitted)

def _csp_nonce() -> str:
    if not hasattr(g, "_csp_nonce"):
        g._csp_nonce = base64.b64encode(os.urandom(16)).decode()
    return g._csp_nonce

# CSP hash computation for inline onclick handlers
def _compute_csp_hashes() -> str:
    src_text = open(__file__, encoding="utf-8").read()
    hashes = set()
    for tpl in re.findall(r'[A-Z_]+_TPL\s*=\s*r"""(.*?)"""', src_text, re.DOTALL):
        for handler in re.findall(r'on(?:click|change)="([^"]+)"', tpl):
            digest = hashlib.sha256(handler.encode()).digest()
            hashes.add(f"'sha256-{base64.b64encode(digest).decode()}'")
        for handler in re.findall(r"on(?:click|change)='([^']+)'", tpl):
            digest = hashlib.sha256(handler.encode()).digest()
            hashes.add(f"'sha256-{base64.b64encode(digest).decode()}'")
    return " ".join(sorted(hashes))


def csrf_protect(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            if app_config.auth.enabled and not _csrf_valid():
                return jsonify({"error": "CSRF validation failed"}), 403
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not app_config.auth.enabled:
            return f(*args, **kwargs)
        if not session.get("logged_in"):
            return redirect(url_for("login_page", next=request.path))
        timeout_hrs = app_config.session_timeout_hrs or 12
        login_ts = session.get("login_ts", 0)
        if time.time() - login_ts > timeout_hrs * 3600:
            session.clear()
            flash("Session expired. Please log in again.")
            return redirect(url_for("login_page", next=request.path))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
#  NTP SHM WRITER — feeds GPS time directly to chrony, replacing GPSD
# ═══════════════════════════════════════════════════════════════════════════════

class NtpShmWriter:
    """Write GPS timestamps to chrony's NTP shared memory segment (SHM 0).

    This replaces GPSD's role in the NTP pipeline.  PTPScope reads the GPS
    serial port directly, so GPSD can never access it.  Instead, PTPScope
    writes to the same SysV SHM segment that chrony's ``refclock SHM 0``
    reads, giving chrony a coarse-time GPS reference that PPS can lock to.

    SHM layout (from chrony refclock_shm.c / gpsd shmexport.c):
        On 64-bit platforms (aarch64, x86_64) time_t is 8 bytes:
        int      mode          offset  0   (4 bytes, must be 1)
        int      count         offset  4   (4 bytes)
        time_t   clockSec      offset  8   (8 bytes on 64-bit!)
        int      clockUSec     offset 16   (4 bytes)
        — 4 bytes padding —              (struct alignment)
        time_t   recvSec       offset 24   (8 bytes on 64-bit!)
        int      recvUSec      offset 32   (4 bytes)
        int      leap          offset 36   (4 bytes, 0 = normal)
        int      precision     offset 40   (4 bytes, -1 = ~0.5 s)
        int      nsamples      offset 44   (4 bytes, 3 for chrony)
        int      valid         offset 48   (4 bytes, 1 when ready)
        On 32-bit (armv7l) time_t is 4 bytes, all fields are int, valid @ 36.
    """

    SHM_KEY = 0x4e545030   # NTP0 — matches chrony "refclock SHM 0"
    SHM_SIZE = 96

    # Detect 64-bit platform: time_t is 8 bytes, struct has padding
    import ctypes as _ct
    _IS_64BIT = _ct.sizeof(_ct.c_long) == 8
    # valid field offset: 48 on 64-bit, 36 on 32-bit
    _VALID_OFF = 48 if _IS_64BIT else 36
    # struct pack format: 'l' = time_t (long), 'i' = int
    # 64-bit: ii l i xxxx l i iiii  (xxxx = 4-byte padding after clockUSec)
    # 32-bit: iiiiiiiiii
    _HDR_FMT = "ii" if _IS_64BIT else "ii"

    def __init__(self, log_fn):
        self.log = log_fn
        self._shm = None
        self._count = 0
        self._attached = False

    def attach(self):
        """Attach to (or create) the NTP SHM 0 segment with world-readable perms."""
        if self._attached:
            return True
        try:
            import sysv_ipc
            # Remove any stale segment with wrong perms (e.g. 600 from old GPSD)
            try:
                old = sysv_ipc.SharedMemory(self.SHM_KEY)
                old.remove()
                self.log("[SHM] Removed stale SHM segment (wrong perms)")
            except sysv_ipc.ExistentialError:
                pass
            # Create fresh with world-readable perms so chrony (_chrony user) can read
            self._shm = sysv_ipc.SharedMemory(
                self.SHM_KEY, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL,
                mode=0o666, size=self.SHM_SIZE
            )
            self._attached = True
            self.log("[SHM] Attached to NTP SHM 0")
            return True
        except ImportError:
            # Fall back to ctypes if sysv_ipc not installed
            return self._attach_ctypes()
        except Exception as e:
            self.log(f"[SHM] Failed to attach: {e}")
            return False

    def _attach_ctypes(self) -> bool:
        """Attach using ctypes (no external deps)."""
        try:
            import ctypes
            import ctypes.util
            libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
            # Try to get existing segment first
            shmid = libc.shmget(self.SHM_KEY, self.SHM_SIZE, 0)
            if shmid >= 0:
                # Segment exists — delete it so we can recreate with correct perms.
                # Old GPSD-created segments have 600 perms; chrony needs 666.
                libc.shmctl(shmid, 0, None)  # IPC_RMID = 0
                self.log("[SHM] Removed stale SHM segment (wrong perms)")
            # Create fresh with world-readable perms
            IPC_CREAT = 0o1000
            IPC_EXCL  = 0o2000
            shmid = libc.shmget(self.SHM_KEY, self.SHM_SIZE,
                                IPC_CREAT | IPC_EXCL | 0o666)
            if shmid < 0:
                # Race: someone else created it; just open it
                shmid = libc.shmget(self.SHM_KEY, self.SHM_SIZE, 0)
            if shmid < 0:
                self.log(f"[SHM] shmget failed (errno {ctypes.get_errno()})")
                return False
            # shmat(shmid, NULL, 0)
            libc.shmat.restype = ctypes.c_void_p
            addr = libc.shmat(shmid, None, 0)
            if addr == ctypes.c_void_p(-1).value:
                self.log(f"[SHM] shmat failed (errno {ctypes.get_errno()})")
                return False
            self._shm = addr
            self._attached = True
            self._use_ctypes = True
            self.log("[SHM] Attached to NTP SHM 0 (ctypes)")
            return True
        except Exception as e:
            self.log(f"[SHM] ctypes attach failed: {e}")
            return False

    def write(self, clock_sec: int, clock_usec: int,
              recv_sec: int, recv_usec: int):
        """Write a GPS time sample to SHM for chrony to read.

        The struct layout depends on the platform word size:
          64-bit (aarch64/x86_64): time_t = 8 bytes, valid at offset 48
          32-bit (armv7l):         time_t = 4 bytes, valid at offset 36
        """
        if not self._attached:
            return
        import struct
        self._count += 1

        if self._IS_64BIT:
            # struct shmTime on 64-bit:
            #   int mode(4) + int count(4) + time_t clockSec(8) +
            #   int clockUSec(4) + 4-pad + time_t recvSec(8) +
            #   int recvUSec(4) + int leap(4) + int precision(4) +
            #   int nsamples(4) + int valid(4)
            # Use native struct packing with '@' to get correct alignment
            fmt = "@ii q i xxxx q i iiii"
            data_size = struct.calcsize(fmt)
        else:
            # 32-bit: all fields are int (4 bytes)
            fmt = "@iiiiiiiiii"
            data_size = struct.calcsize(fmt)

        if hasattr(self, '_use_ctypes') and self._use_ctypes:
            import ctypes
            # Step 1: set valid=0
            _zero = struct.pack("i", 0)
            _zbuf = (ctypes.c_byte * 4)(*_zero)
            ctypes.memmove(self._shm + self._VALID_OFF, _zbuf, 4)
            # Step 2: write all fields (valid=0 in the packed data)
            packed = struct.pack(fmt,
                                 1,               # mode
                                 self._count,      # count
                                 clock_sec,        # clockTimeStampSec (time_t)
                                 clock_usec,       # clockTimeStampUSec
                                                   # (4-byte padding on 64-bit)
                                 recv_sec,         # receiveTimeStampSec (time_t)
                                 recv_usec,        # receiveTimeStampUSec
                                 0,               # leap
                                 -1,              # precision
                                 3,               # nsamples
                                 0)               # valid (set to 1 below)
            buf = (ctypes.c_byte * len(packed))(*packed)
            ctypes.memmove(self._shm, buf, self._VALID_OFF)  # write up to valid
            # Step 3: set valid=1
            _one = struct.pack("i", 1)
            _obuf = (ctypes.c_byte * 4)(*_one)
            ctypes.memmove(self._shm + self._VALID_OFF, _obuf, 4)
        else:
            # sysv_ipc path
            # Step 1: clear valid
            self._shm.write(struct.pack("i", 0), self._VALID_OFF)
            # Step 2: write fields
            packed = struct.pack(fmt,
                                 1, self._count,
                                 clock_sec, clock_usec,
                                 recv_sec, recv_usec,
                                 0, -1, 3, 0)
            self._shm.write(packed[:self._VALID_OFF], 0)
            # Step 3: set valid=1
            self._shm.write(struct.pack("i", 1), self._VALID_OFF)


# ═══════════════════════════════════════════════════════════════════════════════
#  GPS READER
# ═══════════════════════════════════════════════════════════════════════════════

class GPSReader:
    def __init__(self, log_fn):
        self.log = log_fn
        self.fix_type = 0
        self.fix_quality = "No Fix"
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed_knots = 0.0
        self.satellites_used = 0
        self.satellites_view = 0
        self.hdop = 99.9
        self.utc_time = ""
        self.utc_date = ""
        self.pps_ok = False
        self.pps_last = 0.0
        self.last_update = 0.0
        self.state = "idle"
        self._serial = None
        self._shm = NtpShmWriter(log_fn)

    def _nmea_checksum_valid(self, sentence: str) -> bool:
        if "*" not in sentence:
            return False
        body, chk = sentence.rsplit("*", 1)
        body = body.lstrip("$")
        calc = 0
        for c in body:
            calc ^= ord(c)
        try:
            return calc == int(chk.strip(), 16)
        except ValueError:
            return False

    def _nmea_to_decimal(self, value: str, direction: str) -> float:
        if not value:
            return 0.0
        try:
            if direction in ("N", "S"):
                deg = float(value[:2])
                minutes = float(value[2:])
            else:
                deg = float(value[:3])
                minutes = float(value[3:])
            result = deg + minutes / 60.0
            if direction in ("S", "W"):
                result = -result
            return result
        except (ValueError, IndexError):
            return 0.0

    def _parse_gga(self, fields):
        try:
            if len(fields) < 10:
                return
            if fields[1]:
                raw = fields[1]
                self.utc_time = f"{raw[:2]}:{raw[2:4]}:{raw[4:6]}"
            fix = int(fields[6]) if fields[6] else 0
            self.fix_type = fix
            if fix == 0:
                self.fix_quality = "No Fix"
            elif fix == 1:
                self.fix_quality = "GPS Fix"
            elif fix == 2:
                self.fix_quality = "DGPS Fix"
            elif fix == 4:
                self.fix_quality = "RTK Fixed"
            elif fix == 5:
                self.fix_quality = "RTK Float"
            else:
                self.fix_quality = f"Fix ({fix})"
            self.satellites_used = int(fields[7]) if fields[7] else 0
            self.hdop = float(fields[8]) if fields[8] else 99.9
            self.latitude = self._nmea_to_decimal(fields[2], fields[3])
            self.longitude = self._nmea_to_decimal(fields[4], fields[5])
            self.altitude = float(fields[9]) if fields[9] else 0.0
            self.last_update = time.time()
        except (ValueError, IndexError):
            pass

    def _parse_rmc(self, fields):
        try:
            if len(fields) < 10:
                return
            if fields[1]:
                raw = fields[1]
                self.utc_time = f"{raw[:2]}:{raw[2:4]}:{raw[4:6]}"
            if fields[9]:
                raw = fields[9]
                self.utc_date = f"20{raw[4:6]}-{raw[2:4]}-{raw[0:2]}"
            self.speed_knots = float(fields[7]) if fields[7] else 0.0
        except (ValueError, IndexError):
            pass

    def _parse_gsv(self, fields):
        try:
            if len(fields) >= 4:
                self.satellites_view = int(fields[3]) if fields[3] else 0
        except (ValueError, IndexError):
            pass

    def _write_shm(self):
        """Write current GPS time to NTP SHM 0 for chrony.

        Called after each valid GGA parse.  Constructs a UTC timestamp from
        the parsed utc_time + utc_date fields and writes it alongside the
        local receive time so chrony can compute offset.
        """
        if self.fix_type < 1 or not self.utc_time:
            return
        if not self._shm._attached:
            self._shm.attach()
        if not self._shm._attached:
            return
        try:
            # Build GPS clock time from parsed NMEA fields
            h, m, s = int(self.utc_time[:2]), int(self.utc_time[3:5]), int(self.utc_time[6:8])
            if self.utc_date:
                # utc_date format: "2026-03-29"
                from datetime import datetime, timezone
                dt = datetime(int(self.utc_date[:4]), int(self.utc_date[5:7]),
                              int(self.utc_date[8:10]), h, m, s, tzinfo=timezone.utc)
            else:
                # No date yet — use today's date
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                dt = now.replace(hour=h, minute=m, second=s, microsecond=0)
            clock_sec = int(dt.timestamp())
            clock_usec = 0
            # Receive time = local monotonic wall clock
            now_ts = time.time()
            recv_sec = int(now_ts)
            recv_usec = int((now_ts - recv_sec) * 1_000_000)
            self._shm.write(clock_sec, clock_usec, recv_sec, recv_usec)
        except Exception:
            pass

    def _check_pps(self):
        pps_path = "/sys/class/pps/pps0/assert"
        try:
            with open(pps_path, "r") as f:
                line = f.read().strip()
            if line:
                ts_str = line.split("#")[0].strip()
                ts = float(ts_str)
                self.pps_last = ts
                self.pps_ok = (time.time() - ts) < 2.0
            else:
                self.pps_ok = False
        except (FileNotFoundError, ValueError, PermissionError):
            self.pps_ok = False

    def _update_state(self):
        if self.fix_type >= 1 and self.pps_ok:
            self.state = "ok"
        elif self.fix_type >= 1:
            self.state = "warn"
        elif time.time() - self.last_update > 10:
            self.state = "error"
        else:
            self.state = "idle"

    def run(self, stop_event: threading.Event, gps_cfg: GpsConfig):
        self.log(f"[GPS] Starting reader on {gps_cfg.serial_port} @ {gps_cfg.baud_rate}")
        while not stop_event.is_set():
            try:
                if serial_mod is None:
                    self.log("[GPS] pyserial not installed — GPS disabled")
                    self.state = "error"
                    stop_event.wait(30)
                    continue
                self._serial = serial_mod.Serial(
                    gps_cfg.serial_port, gps_cfg.baud_rate, timeout=1
                )
                self.log("[GPS] Serial port opened")
                while not stop_event.is_set():
                    try:
                        raw = self._serial.readline()
                        if not raw:
                            continue
                        line = raw.decode("ascii", errors="ignore").strip()
                        if not line.startswith("$"):
                            continue
                        if not self._nmea_checksum_valid(line):
                            continue
                        body = line.split("*")[0]
                        fields = body.split(",")
                        tag = fields[0]
                        if tag in ("$GPGGA", "$GNGGA"):
                            self._parse_gga(fields)
                            self._write_shm()
                        elif tag in ("$GPRMC", "$GNRMC"):
                            self._parse_rmc(fields)
                        elif tag in ("$GPGSV", "$GNGSV", "$GLGSV"):
                            self._parse_gsv(fields)
                        self._check_pps()
                        self._update_state()
                    except Exception:
                        pass
            except Exception as e:
                self.log(f"[GPS] Serial error: {e}")
                self.state = "error"
                if self._serial:
                    try:
                        self._serial.close()
                    except Exception:
                        pass
                    self._serial = None
                stop_event.wait(5)
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        self.log("[GPS] Reader stopped")

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "fix_type": self.fix_type,
            "fix_quality": self.fix_quality,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed_knots": self.speed_knots,
            "satellites_used": self.satellites_used,
            "satellites_view": self.satellites_view,
            "hdop": self.hdop,
            "utc_time": self.utc_time,
            "utc_date": self.utc_date,
            "pps_ok": self.pps_ok,
            "last_update": self.last_update,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  PTP MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

RE_OFFSET = re.compile(r"master offset\s+(-?\d+)")
RE_DELAY  = re.compile(r"path delay\s+(-?\d+)")
RE_STATE  = re.compile(r"port \d+.*?:\s*(\w+)\s+to\s+(\w+)")
RE_GM     = re.compile(r"selected best master clock\s+([0-9a-f.]+)", re.I)
RE_PHC    = re.compile(r"CLOCK_REALTIME phc offset\s+(-?\d+)")

class PTPManager:
    def __init__(self, log_fn):
        self.log = log_fn
        self.running = False
        self.port_state = "—"
        self.clock_class = 0
        self.offset_ns = 0
        self.path_delay_ns = 0
        self.gm_id = ""
        self.domain = 0
        self.transport = ""
        self.slave_count = 0
        self.phc_offset_ns = 0
        self.pid = 0
        self.state = "idle"
        self.ptp4l_log = collections.deque(maxlen=500)
        self._proc = None
        self._phc2sys_proc = None
        self._reader_thread = None
        self._line_queue = collections.deque(maxlen=1000)

    def _detect_timestamping(self, interface: str) -> str:
        try:
            result = subprocess.run(
                ["ethtool", "-T", interface],
                capture_output=True, text=True, timeout=5
            )
            out = result.stdout
            # Intel/Broadcom NICs report "hardware-transmit" / "hardware-receive"
            # Mellanox ConnectX cards report SOF_TIMESTAMPING_TX_HARDWARE / RX_HARDWARE
            has_tx = "hardware-transmit" in out or "SOF_TIMESTAMPING_TX_HARDWARE" in out
            has_rx = "hardware-receive" in out or "SOF_TIMESTAMPING_RX_HARDWARE" in out
            if has_tx and has_rx:
                return "hardware"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return "software"

    def generate_config(self, ptp_cfg: PtpConfig):
        ts_mode = self._detect_timestamping(ptp_cfg.interface)
        self.log(f"[PTP] Timestamping mode: {ts_mode}")
        transport_map = {"UDPv4": "UDPv4", "UDPv6": "UDPv6", "L2": "L2"}
        conf = f"""[global]
domainNumber          {ptp_cfg.domain}
priority1             {ptp_cfg.priority1}
priority2             {ptp_cfg.priority2}
clockClass            {ptp_cfg.clock_class}
clockAccuracy         {hex(ptp_cfg.clock_accuracy)}
timeSource            {hex(ptp_cfg.time_source)}
network_transport     {transport_map.get(ptp_cfg.transport, 'UDPv4')}
slaveOnly             0
gmCapable             1
free_running          0
freq_est_interval     1
logging_level         6
verbose               1
summary_interval      0
tx_timestamp_timeout  10
time_stamping         {ts_mode}
pi_proportional_const 0.7
pi_integral_const     0.3
[{ptp_cfg.interface}]
"""
        with open(PTP_CONF_PATH, "w") as f:
            f.write(conf)
        self.log(f"[PTP] Config written to {PTP_CONF_PATH}")

    def _stdout_reader(self, proc, label):
        try:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    self._line_queue.append(line)
                    self.ptp4l_log.append(f"[{label}] {line}")
        except Exception:
            pass

    def start(self, ptp_cfg: PtpConfig):
        if self._proc and self._proc.poll() is None:
            self.log("[PTP] ptp4l already running")
            return
        self.generate_config(ptp_cfg)
        self.domain = ptp_cfg.domain
        self.transport = ptp_cfg.transport
        self.clock_class = ptp_cfg.clock_class
        try:
            self._proc = subprocess.Popen(
                ["ptp4l", "-f", PTP_CONF_PATH, "-m"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            self.pid = self._proc.pid
            self.running = True
            self.log(f"[PTP] ptp4l started (PID {self.pid})")
            self._reader_thread = threading.Thread(
                target=self._stdout_reader, args=(self._proc, "ptp4l"), daemon=True
            )
            self._reader_thread.start()
        except FileNotFoundError:
            self.log("[PTP] ptp4l not found — is linuxptp installed?")
            self.state = "error"
            return
        except Exception as e:
            self.log(f"[PTP] Failed to start ptp4l: {e}")
            self.state = "error"
            return
        # Start phc2sys
        ts_mode = self._detect_timestamping(ptp_cfg.interface)
        if ts_mode == "hardware":
            try:
                self._phc2sys_proc = subprocess.Popen(
                    ["phc2sys", "-s", ptp_cfg.interface, "-c", "CLOCK_REALTIME",
                     "-O", "0", "-m"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                threading.Thread(
                    target=self._stdout_reader,
                    args=(self._phc2sys_proc, "phc2sys"), daemon=True
                ).start()
                self.log(f"[PTP] phc2sys started (PID {self._phc2sys_proc.pid})")
            except Exception as e:
                self.log(f"[PTP] phc2sys failed: {e}")

    def stop(self):
        for proc, name in [(self._proc, "ptp4l"), (self._phc2sys_proc, "phc2sys")]:
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    self.log(f"[PTP] {name} stopped")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                    self.log(f"[PTP] {name} killed")
        self._proc = None
        self._phc2sys_proc = None
        self.running = False
        self.port_state = "—"
        self.pid = 0
        self.state = "idle"

    def _parse_lines(self):
        while self._line_queue:
            line = self._line_queue.popleft()
            m = RE_OFFSET.search(line)
            if m:
                self.offset_ns = int(m.group(1))
            m = RE_DELAY.search(line)
            if m:
                self.path_delay_ns = int(m.group(1))
            m = RE_STATE.search(line)
            if m:
                self.port_state = m.group(2)
            m = RE_GM.search(line)
            if m:
                self.gm_id = m.group(1)
            m = RE_PHC.search(line)
            if m:
                self.phc_offset_ns = int(m.group(1))

    def _update_state(self):
        if not self.running:
            self.state = "idle"
        elif self.port_state in ("MASTER", "GRAND_MASTER"):
            self.state = "ok"
        elif self.port_state in ("LISTENING", "UNCALIBRATED", "SLAVE", "PRE_MASTER"):
            self.state = "warn"
        elif self.port_state in ("FAULTY", "DISABLED"):
            self.state = "error"
        else:
            self.state = "warn"

    def run(self, stop_event: threading.Event, ptp_cfg: PtpConfig):
        if ptp_cfg.auto_start:
            self.start(ptp_cfg)
        while not stop_event.is_set():
            if self.running and self._proc and self._proc.poll() is not None:
                self.log("[PTP] ptp4l exited unexpectedly")
                self.running = False
                self.state = "error"
                if ptp_cfg.auto_start:
                    stop_event.wait(5)
                    if not stop_event.is_set():
                        self.log("[PTP] Restarting ptp4l...")
                        self.start(ptp_cfg)
            self._parse_lines()
            self._update_state()
            stop_event.wait(PTP_POLL_INTERVAL)
        self.stop()
        self.log("[PTP] Manager stopped")

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "running": self.running,
            "port_state": self.port_state,
            "clock_class": self.clock_class,
            "offset_ns": self.offset_ns,
            "path_delay_ns": self.path_delay_ns,
            "gm_id": self.gm_id,
            "domain": self.domain,
            "transport": self.transport,
            "slave_count": self.slave_count,
            "phc_offset_ns": self.phc_offset_ns,
            "pid": self.pid,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  CHRONY CONFIG WRITER — applies GUI settings to /etc/chrony/chrony.conf
# ═══════════════════════════════════════════════════════════════════════════════

_CHRONY_CONF_PATHS = ["/etc/chrony/chrony.conf", "/etc/chrony.conf"]
_CHRONY_MARKER = "# ── PTPScope managed block"

def _find_chrony_conf():
    """Return the path to chrony.conf, or None if not found."""
    for p in _CHRONY_CONF_PATHS:
        if os.path.isfile(p):
            return p
    return None

def _apply_chrony_config(chrony_cfg: ChronyConfig, log_fn=None):
    """Write PTPScope chrony settings and restart chrony.

    On systems with a ``conf.d`` directory (Debian/Ubuntu), writes to
    ``/etc/chrony/conf.d/ptpscope.conf`` — this avoids the problem where
    directives appended to chrony.conf after the ``confdir`` line are
    silently ignored by chrony.

    On systems without ``conf.d``, falls back to appending a managed block
    to chrony.conf (delimited by ``_CHRONY_MARKER``).

    Also cleans up any old managed block from chrony.conf when migrating
    to the conf.d approach.

    Returns (ok: bool, message: str).
    """
    conf_path = _find_chrony_conf()
    if not conf_path:
        return False, "chrony.conf not found — is chrony installed?"

    # ── Build the configuration lines ────────────────────────────────────
    lines = []

    # GPS SHM refclock
    if chrony_cfg.gps_refclock:
        lines.append("refclock SHM 0 refid GPS precision 1e-1 offset 0.5 delay 0.2")

    # PPS refclock — only if /dev/pps0 exists (crashes chrony otherwise)
    if chrony_cfg.pps_refclock and os.path.exists("/dev/pps0"):
        lines.append("refclock PPS /dev/pps0 refid PPS precision 1e-7 lock GPS prefer")

    # GPS Source server (PTP Master pointing at a GPS Pi)
    if chrony_cfg.gps_server_ip and chrony_cfg.gps_server_ip.strip():
        lines.append(f"server {chrony_cfg.gps_server_ip.strip()} iburst prefer")

    # NTP servers (one per line from textarea)
    for srv in chrony_cfg.ntp_servers.strip().splitlines():
        srv = srv.strip()
        if srv and not srv.startswith("#"):
            if not srv.startswith(("server ", "pool ", "peer ")):
                srv = f"server {srv} iburst"
            lines.append(srv)

    # makestep — allow large initial time correction
    if chrony_cfg.makestep:
        lines.append("makestep 1 3")

    # Allow NTP clients
    if chrony_cfg.allow_clients and chrony_cfg.allow_subnet.strip():
        lines.append(f"allow {chrony_cfg.allow_subnet.strip()}")

    # ── Determine write target ───────────────────────────────────────────
    # Prefer conf.d if it exists (avoids confdir ordering issue)
    conf_dir = os.path.dirname(conf_path)
    confd_path = os.path.join(conf_dir, "conf.d")
    use_confd = os.path.isdir(confd_path)

    if use_confd:
        target_path = os.path.join(confd_path, "ptpscope.conf")
        content = f"{_CHRONY_MARKER} START — managed by PTPScope GUI\n"
        content += "\n".join(lines) + "\n"
        content += f"{_CHRONY_MARKER} END\n"

        try:
            with open(target_path, "w") as f:
                f.write(content)
        except PermissionError:
            return False, f"Permission denied writing {target_path}"
        except Exception as e:
            return False, f"Failed to write {target_path}: {e}"

        # Clean up any old managed block from chrony.conf itself
        try:
            import re as _re
            with open(conf_path, "r") as f:
                existing = f.read()
            managed_re = _re.compile(
                r'\n?' + _re.escape(_CHRONY_MARKER) + r' START.*?'
                + _re.escape(_CHRONY_MARKER) + r' END[^\n]*\n?',
                _re.DOTALL
            )
            if managed_re.search(existing):
                cleaned = managed_re.sub('', existing).rstrip('\n') + '\n'
                with open(conf_path, "w") as f:
                    f.write(cleaned)
                if log_fn:
                    log_fn(f"[Chrony] Removed old managed block from {conf_path}")
        except Exception:
            pass  # non-fatal — the conf.d file is what matters

        if log_fn:
            log_fn(f"[Chrony] Config written to {target_path}")
    else:
        # Fallback: append managed block to chrony.conf
        try:
            with open(conf_path, "r") as f:
                existing = f.read()
        except PermissionError:
            return False, f"Permission denied reading {conf_path}"
        except Exception as e:
            return False, f"Failed to read {conf_path}: {e}"

        import re as _re
        managed_re = _re.compile(
            r'\n?' + _re.escape(_CHRONY_MARKER) + r' START.*?'
            + _re.escape(_CHRONY_MARKER) + r' END[^\n]*\n?',
            _re.DOTALL
        )
        base = managed_re.sub('', existing).rstrip('\n')
        block_lines = [f"{_CHRONY_MARKER} START — managed by PTPScope GUI"]
        block_lines.extend(lines)
        block_lines.append(f"{_CHRONY_MARKER} END")
        block = "\n".join(block_lines)
        new_conf = base + "\n\n" + block + "\n"

        try:
            import shutil
            shutil.copy2(conf_path, conf_path + ".ptpscope-bak")
            with open(conf_path, "w") as f:
                f.write(new_conf)
        except PermissionError:
            return False, f"Permission denied writing {conf_path}"
        except Exception as e:
            return False, f"Failed to write {conf_path}: {e}"

        if log_fn:
            log_fn(f"[Chrony] Config written to {conf_path}")

    # ── Restart chrony ───────────────────────────────────────────────────
    try:
        r = subprocess.run(
            ["systemctl", "restart", "chrony"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            if log_fn:
                log_fn("[Chrony] Service restarted successfully")
            return True, f"Chrony config applied to {conf_path} and service restarted."
        else:
            # Try chronyd directly (some systems)
            r2 = subprocess.run(
                ["systemctl", "restart", "chronyd"],
                capture_output=True, text=True, timeout=10
            )
            if r2.returncode == 0:
                if log_fn:
                    log_fn("[Chrony] Service (chronyd) restarted successfully")
                return True, f"Chrony config applied to {conf_path} and service restarted."
            msg = r.stderr.strip() or "unknown error"
            if log_fn:
                log_fn(f"[Chrony] Failed to restart: {msg}")
            return True, f"Config written to {conf_path} but restart failed: {msg}. Try: sudo systemctl restart chrony"
    except FileNotFoundError:
        if log_fn:
            log_fn("[Chrony] systemctl not found — config written but not restarted")
        return True, f"Config written to {conf_path}. Restart chrony manually (systemctl not found)."
    except Exception as e:
        return True, f"Config written to {conf_path} but restart failed: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
#  CHRONY MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

class ChronyMonitor:
    def __init__(self, log_fn):
        self.log = log_fn
        self.ref_id = ""
        self.stratum = 0
        self.system_offset_us = 0.0
        self.last_offset_us = 0.0
        self.rms_offset_us = 0.0
        self.frequency_ppm = 0.0
        self.skew_ppm = 0.0
        self.root_delay_us = 0.0
        self.root_dispersion_us = 0.0
        self.leap_status = ""
        self.sources_count = 0
        self.state = "idle"
        self.last_update = 0.0

    def _poll_tracking(self):
        try:
            result = subprocess.run(
                ["chronyc", "-c", "tracking"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return
            fields = result.stdout.strip().split(",")
            if len(fields) < 14:
                return
            self.ref_id = fields[1] if fields[1] else fields[0]
            self.stratum = int(fields[2]) if fields[2] else 0
            # System time offset (seconds -> microseconds)
            self.system_offset_us = float(fields[4]) * 1e6 if fields[4] else 0.0
            self.last_offset_us = float(fields[5]) * 1e6 if fields[5] else 0.0
            self.rms_offset_us = float(fields[6]) * 1e6 if fields[6] else 0.0
            self.frequency_ppm = float(fields[7]) if fields[7] else 0.0
            self.skew_ppm = float(fields[9]) if fields[9] else 0.0
            self.root_delay_us = float(fields[10]) * 1e6 if fields[10] else 0.0
            self.root_dispersion_us = float(fields[11]) * 1e6 if fields[11] else 0.0
            leap_map = {"0": "Normal", "1": "Insert", "2": "Delete", "3": "Not synced"}
            self.leap_status = leap_map.get(fields[13].strip(), fields[13].strip())
            self.last_update = time.time()
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            if isinstance(e, FileNotFoundError):
                self.log("[Chrony] chronyc not found")
            pass

    def _poll_sources(self):
        try:
            result = subprocess.run(
                ["chronyc", "-c", "sources"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return
            lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
            self.sources_count = len(lines)
        except Exception:
            pass

    def _update_state(self):
        if time.time() - self.last_update > 15:
            self.state = "error"
        elif self.stratum <= 1:
            self.state = "ok"
        elif self.stratum <= 4:
            self.state = "warn"
        else:
            self.state = "error"

    def run(self, stop_event: threading.Event):
        self.log("[Chrony] Monitor started")
        while not stop_event.is_set():
            self._poll_tracking()
            self._poll_sources()
            self._update_state()
            stop_event.wait(CHRONY_POLL_INTERVAL)
        self.log("[Chrony] Monitor stopped")

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "ref_id": self.ref_id,
            "stratum": self.stratum,
            "system_offset_us": self.system_offset_us,
            "last_offset_us": self.last_offset_us,
            "rms_offset_us": self.rms_offset_us,
            "frequency_ppm": self.frequency_ppm,
            "skew_ppm": self.skew_ppm,
            "root_delay_us": self.root_delay_us,
            "root_dispersion_us": self.root_dispersion_us,
            "leap_status": self.leap_status,
            "sources_count": self.sources_count,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  SYSTEM STATS
# ═══════════════════════════════════════════════════════════════════════════════

class SystemStats:
    def __init__(self, log_fn):
        self.log = log_fn
        self.cpu_temp = 0.0
        self.load_1 = 0.0
        self.load_5 = 0.0
        self.load_15 = 0.0
        self.uptime_seconds = 0
        self.mem_total_mb = 0
        self.mem_used_mb = 0
        self.disk_total_gb = 0.0
        self.disk_used_gb = 0.0
        self.hostname = ""
        self.ip_address = ""
        self.kernel = ""
        self.pi_model = ""

    def _read_once(self):
        self.hostname = socket.gethostname()
        try:
            result = subprocess.run(["uname", "-r"], capture_output=True, text=True, timeout=3)
            self.kernel = result.stdout.strip()
        except Exception:
            pass
        try:
            with open("/proc/device-tree/model", "r") as f:
                self.pi_model = f.read().strip().rstrip("\x00")
        except FileNotFoundError:
            self.pi_model = "Unknown"

    def _poll(self):
        # CPU temp
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                self.cpu_temp = int(f.read().strip()) / 1000.0
        except (FileNotFoundError, ValueError):
            pass
        # Load
        try:
            with open("/proc/loadavg", "r") as f:
                parts = f.read().strip().split()
                self.load_1 = float(parts[0])
                self.load_5 = float(parts[1])
                self.load_15 = float(parts[2])
        except (FileNotFoundError, ValueError, IndexError):
            pass
        # Uptime
        try:
            with open("/proc/uptime", "r") as f:
                self.uptime_seconds = int(float(f.read().strip().split()[0]))
        except (FileNotFoundError, ValueError):
            pass
        # Memory
        try:
            with open("/proc/meminfo", "r") as f:
                info = f.read()
            total = int(re.search(r"MemTotal:\s+(\d+)", info).group(1)) // 1024
            available = int(re.search(r"MemAvailable:\s+(\d+)", info).group(1)) // 1024
            self.mem_total_mb = total
            self.mem_used_mb = total - available
        except (FileNotFoundError, AttributeError, ValueError):
            pass
        # Disk
        try:
            st = os.statvfs("/")
            self.disk_total_gb = (st.f_blocks * st.f_frsize) / (1024 ** 3)
            self.disk_used_gb = ((st.f_blocks - st.f_bfree) * st.f_frsize) / (1024 ** 3)
        except Exception:
            pass
        # IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 53))
            self.ip_address = s.getsockname()[0]
            s.close()
        except Exception:
            self.ip_address = "127.0.0.1"

    def run(self, stop_event: threading.Event):
        self.log("[System] Stats monitor started")
        self._read_once()
        while not stop_event.is_set():
            self._poll()
            stop_event.wait(SYS_POLL_INTERVAL)
        self.log("[System] Stats monitor stopped")

    def to_dict(self) -> dict:
        return {
            "cpu_temp": self.cpu_temp,
            "load": f"{self.load_1:.2f} {self.load_5:.2f} {self.load_15:.2f}",
            "uptime_seconds": self.uptime_seconds,
            "mem_total_mb": self.mem_total_mb,
            "mem_used_mb": self.mem_used_mb,
            "disk_total_gb": self.disk_total_gb,
            "disk_used_gb": self.disk_used_gb,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "kernel": self.kernel,
            "pi_model": self.pi_model,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  HEARTBEAT SENDER  (runs on gps_source node)
# ═══════════════════════════════════════════════════════════════════════════════

class HeartbeatSender:
    """Posts GPS + chrony + system data to the PTP master every 10 s."""
    INTERVAL = 10.0

    def __init__(self, log_fn):
        self.log = log_fn
        self.state = "idle"
        self.last_sent = 0.0
        self.last_status = 0
        self.latency_ms = 0.0
        self.total_sent = 0
        self.fail_count = 0
        self.fail_streak = 0

    def _sign(self, secret: str, ts: float, body: bytes) -> str:
        key = hashlib.sha256(f"{secret}:ptp-hb-signing".encode()).digest()
        msg = f"{ts:.0f}:".encode() + body
        return _hmac.new(key, msg, hashlib.sha256).hexdigest()

    def run(self, stop_ev: threading.Event, gps_rd, chrony_mon, sys_st, node_cfg):
        import urllib.request as _ureq
        self.log("[HB] Heartbeat sender started")
        while not stop_ev.is_set():
            url = (node_cfg.hub_url or "").rstrip("/")
            if not url:
                stop_ev.wait(self.INTERVAL)
                continue
            try:
                payload = {
                    "site": node_cfg.site_name or socket.gethostname(),
                    "ts": time.time(),
                    "gps": gps_rd.to_dict(),
                    "chrony": chrony_mon.to_dict(),
                    "system": sys_st.to_dict(),
                }
                body = json.dumps(payload).encode()
                ts = time.time()
                sig = self._sign(node_cfg.secret_key, ts, body) if node_cfg.secret_key else ""
                req = _ureq.Request(
                    url + "/api/gps_heartbeat",
                    data=body, method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "X-Ptp-Ts": f"{ts:.0f}",
                        "X-Ptp-Sig": sig,
                        "X-Ptp-Site": payload["site"],
                    }
                )
                t0 = time.monotonic()
                resp = _ureq.urlopen(req, timeout=8)
                resp.read()
                self.latency_ms = (time.monotonic() - t0) * 1000
                self.last_sent = time.time()
                self.last_status = resp.status
                self.total_sent += 1
                self.fail_streak = 0
                self.state = "ok"
            except Exception as e:
                self.fail_count += 1
                self.fail_streak += 1
                self.state = "error"
                self.log(f"[HB] Heartbeat failed: {e}")
            stop_ev.wait(self.INTERVAL)
        self.log("[HB] Heartbeat sender stopped")

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "last_sent_ago": round(time.time() - self.last_sent, 1) if self.last_sent else None,
            "last_status": self.last_status,
            "latency_ms": round(self.latency_ms, 1),
            "total_sent": self.total_sent,
            "fail_count": self.fail_count,
            "fail_streak": self.fail_streak,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  FLASK APP
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__, static_folder=STATIC_DIR)

# Secret key
_secret_path = os.path.join(BASE_DIR, ".flask_secret")
if os.path.exists(_secret_path):
    with open(_secret_path, "rb") as f:
        app.secret_key = f.read()
else:
    app.secret_key = os.urandom(32)
    with open(_secret_path, "wb") as f:
        f.write(app.secret_key)
    os.chmod(_secret_path, 0o600)

# Globals
app_config = load_config()
metrics_db = MetricsDB(METRICS_DB)
app_log = collections.deque(maxlen=1000)

def log_fn(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    app_log.append(entry)
    print(entry, flush=True)

gps_reader     = GPSReader(log_fn)
ptp_manager    = PTPManager(log_fn)
chrony_monitor = ChronyMonitor(log_fn)
sys_stats      = SystemStats(log_fn)
hb_sender      = HeartbeatSender(log_fn)

# GPS heartbeat store (ptp_master side)
_gps_hb_data: dict = {}   # site_name → {ts, gps, chrony, system}
_gps_hb_lock = threading.Lock()


def _get_gps_source_data() -> dict:
    """Return latest GPS node heartbeat data for the ptp_master dashboard."""
    with _gps_hb_lock:
        if not _gps_hb_data:
            return {"state": "offline", "site": "", "last_hb_ago": None,
                    "gps": {}, "chrony": {}}
        site, data = max(_gps_hb_data.items(), key=lambda x: x[1]["ts"])
        age = time.time() - data["ts"]
        state = "ok" if age < 30 else ("warn" if age < 120 else "offline")
        return {
            "state": state,
            "site": site,
            "last_hb_ago": round(age, 1),
            "gps": data.get("gps", {}),
            "chrony": data.get("chrony", {}),
        }

# CSP hashes
_CSP_HANDLER_HASHES = _compute_csp_hashes()

# Login rate limiting
_login_attempts: Dict[str, list] = {}


# ── Navigation builder ────────────────────────────────────────────────────────
def topnav(active: str = "") -> str:
    csrf = _csrf_token()
    role = app_config.node.role
    def _a(page, label, href):
        cls = "btn bg bs nav-active" if active == page else "btn bg bs"
        return f'<a class="{cls}" href="{href}">{label}</a>'

    ptp_btns = ""
    if active == "dashboard" and role != "gps_source":
        if ptp_manager.running:
            ptp_btns = (
                f'<button class="btn bd bs" data-ptp-action="stop">Stop PTP</button>'
                f'<button class="btn bg bs" data-ptp-action="restart">Restart</button>'
            )
        else:
            ptp_btns = f'<button class="btn bp bs" data-ptp-action="start">Start PTP</button>'

    subtitles = {
        "gps_source": "GPS Time Source",
        "ptp_master": "PTP Grandmaster",
    }
    subtitle = subtitles.get(role, "GPS PTP Grandmaster")

    ver = BUILD.split("-")[-1]
    logout_btn = ""
    if app_config.auth.enabled:
        logout_btn = (
            f'<form method="post" action="/logout" style="margin:0">'
            f'<input type="hidden" name="_csrf_token" value="{csrf}">'
            f'<button class="btn bg bs" style="color:var(--mu)">Logout</button></form>'
        )
    return (
        '<header>'
        '<a href="/" style="text-decoration:none;display:flex;align-items:center;gap:12px;min-width:0">'
        '<div style="display:flex;flex-direction:column;line-height:1.05;min-width:0">'
        '<span style="font-weight:800;font-size:24px;color:var(--tx);letter-spacing:-.02em">PTPScope</span>'
        f'<span style="font-size:11px;color:var(--mu);text-transform:uppercase;letter-spacing:.16em">{subtitle}</span>'
        '</div></a>'
        f'<div class="badge">v{ver}</div>'
        '<nav style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin-left:auto">'
        + ptp_btns
        + _a("dashboard", "Dashboard", "/")
        + _a("config", "Configuration", "/config")
        + _a("logs", "Logs", "/logs")
        + _a("history", "History", "/history")
        + logout_btn
        + '</nav></header>'
    )

def topnav_safe(active=""):
    return Markup(topnav(active))


def _detect_interfaces():
    """Return list of non-loopback network interface names."""
    ifaces = []
    try:
        net_dir = "/sys/class/net"
        if os.path.isdir(net_dir):
            for name in sorted(os.listdir(net_dir)):
                if name == "lo":
                    continue
                ifaces.append(name)
    except Exception:
        pass
    return ifaces if ifaces else ["eth0"]


# ── Context processor ─────────────────────────────────────────────────────────
@app.context_processor
def _inject_globals():
    return {
        "topnav": topnav_safe,
        "csrf_token": _csrf_token,
        "csp_nonce": _csp_nonce,
        "build": BUILD,
        "role": app_config.node.role,
        "cfg": app_config,
        "net_ifaces": _detect_interfaces(),
    }


# ── Security headers ──────────────────────────────────────────────────────────
@app.after_request
def _apply_security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    ct = response.content_type or ""
    if "html" in ct:
        nonce = _csp_nonce()
        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            "style-src 'self' 'unsafe-inline'; "
            f"script-src-attr 'unsafe-hashes' {_CSP_HANDLER_HASHES}; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "frame-ancestors 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
    return response


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.get("/")
@login_required
def index():
    return render_template_string(DASHBOARD_TPL)


# ── Configuration ─────────────────────────────────────────────────────────────
@app.get("/config")
@login_required
def config_page():
    return render_template_string(CONFIG_TPL, cfg=app_config)

@app.post("/config")
@login_required
@csrf_protect
def config_save():
    global app_config
    panel = request.form.get("_panel", "ptp")
    if panel == "ptp":
        app_config.ptp.domain = int(request.form.get("ptp_domain", 0))
        app_config.ptp.interface = request.form.get("ptp_interface", "eth0").strip()
        app_config.ptp.transport = request.form.get("ptp_transport", "UDPv4")
        app_config.ptp.priority1 = int(request.form.get("ptp_priority1", 128))
        app_config.ptp.priority2 = int(request.form.get("ptp_priority2", 128))
        app_config.ptp.clock_class = int(request.form.get("ptp_clock_class", 6))
        app_config.ptp.clock_accuracy = int(request.form.get("ptp_clock_accuracy", 0x21))
        app_config.ptp.time_source = int(request.form.get("ptp_time_source", 0x20))
        app_config.ptp.auto_start = "ptp_auto_start" in request.form
    elif panel == "gps":
        app_config.gps.serial_port = request.form.get("gps_serial_port", "/dev/serial0").strip()
        app_config.gps.baud_rate = int(request.form.get("gps_baud_rate", 9600))
        app_config.gps.pps_gpio = int(request.form.get("gps_pps_gpio", 4))
        app_config.gps.enable_gpsd = "gps_enable_gpsd" in request.form
    elif panel == "chrony":
        app_config.chrony.gps_refclock = "chrony_gps_refclock" in request.form
        app_config.chrony.pps_refclock = "chrony_pps_refclock" in request.form
        app_config.chrony.ntp_servers = request.form.get("chrony_ntp_servers", "")
        app_config.chrony.gps_server_ip = request.form.get("chrony_gps_server_ip", "").strip()
        app_config.chrony.makestep = "chrony_makestep" in request.form
        app_config.chrony.allow_clients = "chrony_allow_clients" in request.form
        app_config.chrony.allow_subnet = request.form.get("chrony_allow_subnet", "192.168.1.0/24").strip()
    elif panel == "network":
        app_config.web_port = int(request.form.get("web_port", 5001))
        app_config.bind_address = request.form.get("bind_address", "0.0.0.0").strip()
    elif panel == "security":
        app_config.auth.enabled = "auth_enabled" in request.form
        app_config.auth.username = request.form.get("auth_username", "admin").strip()
        new_pw = request.form.get("auth_password", "").strip()
        if new_pw:
            app_config.auth.password_hash = _hash_password(new_pw)
            app_config.auth.first_login = False
        app_config.session_timeout_hrs = int(request.form.get("session_timeout_hrs", 12))
    elif panel == "node":
        app_config.node.role       = request.form.get("node_role", "standalone").strip()
        app_config.node.site_name  = request.form.get("node_site_name", "").strip()
        app_config.node.secret_key = request.form.get("node_secret_key", "").strip()
        app_config.node.hub_url    = request.form.get("node_hub_url", "").strip()
    save_config(app_config)
    log_fn(f"[Config] {panel} settings updated")

    # ── Apply chrony config to system when saving chrony panel ────────────
    if panel == "chrony":
        ok, msg = _apply_chrony_config(app_config.chrony, log_fn)
        if ok:
            flash(f"Chrony settings saved. {msg}")
        else:
            flash(f"Chrony settings saved but could not apply: {msg}")
    else:
        flash(f"{panel.upper()} settings saved.")

    return redirect(url_for("config_page") + f"#{panel}")


# ── Logs ──────────────────────────────────────────────────────────────────────
@app.get("/logs")
@login_required
def logs_page():
    return render_template_string(LOGS_TPL)


# ── History ───────────────────────────────────────────────────────────────────
@app.get("/history")
@login_required
def history_page():
    return render_template_string(HISTORY_TPL)


# ── Login / Logout ────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if not app_config.auth.enabled:
        return redirect("/")
    ip = request.remote_addr or "unknown"
    # Rate limiting
    now = time.time()
    attempts = _login_attempts.get(ip, [])
    attempts = [t for t in attempts if now - t < 900]  # 15 min window
    _login_attempts[ip] = attempts
    if len(attempts) >= 10:
        return render_template_string(LOGIN_TPL, locked=True, locked_mins=15,
                                      error=None, first_login=False, username="")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        first = app_config.auth.first_login and not app_config.auth.password_hash
        if first:
            new_pw = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")
            if len(new_pw) < 8:
                return render_template_string(LOGIN_TPL, locked=False, error="Password must be 8+ characters",
                                              first_login=True, username=username)
            if new_pw != confirm:
                return render_template_string(LOGIN_TPL, locked=False, error="Passwords do not match",
                                              first_login=True, username=username)
            app_config.auth.username = username or "admin"
            app_config.auth.password_hash = _hash_password(new_pw)
            app_config.auth.first_login = False
            save_config(app_config)
            session["logged_in"] = True
            session["login_ts"] = time.time()
            return redirect(request.args.get("next", "/"))
        if username == app_config.auth.username and _verify_password(password, app_config.auth.password_hash):
            session["logged_in"] = True
            session["login_ts"] = time.time()
            return redirect(request.args.get("next", "/"))
        attempts.append(now)
        _login_attempts[ip] = attempts
        return render_template_string(LOGIN_TPL, locked=False, error="Invalid credentials",
                                      first_login=False, username=username)
    first = app_config.auth.first_login and not app_config.auth.password_hash
    return render_template_string(LOGIN_TPL, locked=False, error=None,
                                  first_login=first, username="")

@app.post("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ═══════════════════════════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/status")
@login_required
def api_status():
    role = app_config.node.role
    log_lines = list(app_log)[-30:]
    result: dict = {
        "role": role,
        "chrony": chrony_monitor.to_dict(),
        "system": sys_stats.to_dict(),
        "log": log_lines,
    }
    if role in ("standalone", "gps_source"):
        result["gps"] = gps_reader.to_dict()
    if role == "gps_source":
        result["hub_conn"] = hb_sender.to_dict()
    if role in ("standalone", "ptp_master"):
        result["ptp"] = ptp_manager.to_dict()
    if role == "ptp_master":
        result["gps_source"] = _get_gps_source_data()
    return jsonify(result)


@app.post("/api/gps_heartbeat")
def api_gps_heartbeat():
    """Receive heartbeat from a gps_source node (no login required — HMAC secured)."""
    if app_config.node.role != "ptp_master":
        return jsonify({"error": "not a ptp_master node"}), 403
    body = request.get_data()
    ts_str = request.headers.get("X-Ptp-Ts", "0")
    sig    = request.headers.get("X-Ptp-Sig", "")
    site   = request.headers.get("X-Ptp-Site", "unknown").strip()[:64]
    if app_config.node.secret_key:
        try:
            ts = float(ts_str)
            if abs(time.time() - ts) > 60:
                return jsonify({"error": "timestamp too old"}), 403
            key = hashlib.sha256(
                f"{app_config.node.secret_key}:ptp-hb-signing".encode()
            ).digest()
            msg      = f"{ts:.0f}:".encode() + body
            expected = _hmac.new(key, msg, hashlib.sha256).hexdigest()
            if not _hmac.compare_digest(expected, sig):
                return jsonify({"error": "invalid signature"}), 403
        except Exception:
            return jsonify({"error": "auth error"}), 403
    try:
        payload = json.loads(body)
    except Exception:
        return jsonify({"error": "invalid JSON"}), 400
    with _gps_hb_lock:
        _gps_hb_data[site] = {
            "ts":     time.time(),
            "site":   site,
            "gps":    payload.get("gps", {}),
            "chrony": payload.get("chrony", {}),
            "system": payload.get("system", {}),
        }
    return jsonify({"ok": True})

@app.post("/api/ptp/start")
@login_required
@csrf_protect
def api_ptp_start():
    ptp_manager.start(app_config.ptp)
    return jsonify({"ok": True})

@app.post("/api/ptp/stop")
@login_required
@csrf_protect
def api_ptp_stop():
    ptp_manager.stop()
    return jsonify({"ok": True})

@app.post("/api/ptp/restart")
@login_required
@csrf_protect
def api_ptp_restart():
    ptp_manager.stop()
    time.sleep(1)
    ptp_manager.start(app_config.ptp)
    return jsonify({"ok": True})

@app.get("/api/logs")
@login_required
def api_logs():
    return jsonify({
        "ptp4l": list(ptp_manager.ptp4l_log),
        "app": list(app_log),
    })

@app.post("/api/logs/clear")
@login_required
@csrf_protect
def api_logs_clear():
    ptp_manager.ptp4l_log.clear()
    app_log.clear()
    return jsonify({"ok": True})

@app.get("/api/metrics")
@login_required
def api_metrics():
    metric = request.args.get("metric", "clock_offset_ns")
    hours = float(request.args.get("hours", 1))
    points = metrics_db.query(metric, hours)
    return jsonify({"metric": metric, "hours": hours, "points": points})


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def _metrics_flush_loop(stop_ev):
    while not stop_ev.is_set():
        stop_ev.wait(METRICS_FLUSH_INTERVAL)
        if stop_ev.is_set():
            break
        now = time.time()
        rows = [
            ("clock_offset_ns", now, float(ptp_manager.offset_ns)),
            ("path_delay_ns", now, float(ptp_manager.path_delay_ns)),
            ("chrony_offset_us", now, chrony_monitor.system_offset_us),
            ("chrony_freq_ppm", now, chrony_monitor.frequency_ppm),
            ("gps_hdop", now, gps_reader.hdop),
            ("gps_satellites", now, float(gps_reader.satellites_used)),
            ("cpu_temp", now, sys_stats.cpu_temp),
            ("pps_ok", now, 1.0 if gps_reader.pps_ok else 0.0),
        ]
        metrics_db.write(rows)


def _daily_prune_loop(stop_ev):
    while not stop_ev.is_set():
        stop_ev.wait(86400)
        if stop_ev.is_set():
            break
        metrics_db.prune(METRICS_RETENTION_DAYS)
        log_fn("[Metrics] Daily prune completed")


# ═══════════════════════════════════════════════════════════════════════════════
#  SELF-UPDATE — check GitHub for new versions and apply from GUI
# ═══════════════════════════════════════════════════════════════════════════════

_UPDATE_STATE: dict = {"latest": None, "checked_at": 0.0, "error": None}

def _ver_tuple(v: str):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except Exception:
        return (0, 0, 0)

def _fetch_latest_version() -> tuple:
    """Return (version_str, error_str).  version_str is '' on failure."""
    import re as _re
    try:
        import requests as _requests
    except ImportError:
        # Fall back to urllib
        import urllib.request, json as _json
        try:
            req = urllib.request.Request(
                _GH_API_RELEASES_URL,
                headers={"Accept": "application/vnd.github+json",
                         "User-Agent": f"PTPScope/{BUILD}"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = _json.loads(resp.read())
            tag = data.get("tag_name", "")
            m = _re.search(r"(\d+\.\d+\.\d+)", tag)
            if m:
                return m.group(1), ""
        except Exception as e:
            pass
        # Fallback: raw file
        for branch in ("main", "master"):
            raw_url = f"https://raw.githubusercontent.com/itconor/PtPscope/{branch}/ptpscope.py"
            try:
                req = urllib.request.Request(raw_url, headers={"User-Agent": f"PTPScope/{BUILD}"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    buf = resp.read(262144)
                m = _re.search(rb"PTPScope-(\d+\.\d+\.\d+)", buf)
                if m:
                    return m.group(1).decode(), ""
            except Exception:
                pass
        return "", "Could not reach GitHub (no requests library; urllib fallback also failed)"

    errors = []
    # Try releases API
    try:
        resp = _requests.get(
            _GH_API_RELEASES_URL, timeout=15,
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": f"PTPScope/{BUILD}"},
        )
        if resp.status_code == 200:
            tag = resp.json().get("tag_name", "")
            m = _re.search(r"(\d+\.\d+\.\d+)", tag)
            if m:
                return m.group(1), ""
        elif resp.status_code == 404:
            errors.append("GitHub: no releases published yet")
        else:
            errors.append(f"GitHub releases API HTTP {resp.status_code}")
    except Exception as e:
        errors.append(f"GitHub releases API: {e}")

    # Fallback: raw file
    for branch in ("main", "master"):
        raw_url = f"https://raw.githubusercontent.com/itconor/PtPscope/{branch}/ptpscope.py"
        try:
            resp = _requests.get(raw_url, timeout=30, stream=True)
            if resp.status_code != 200:
                errors.append(f"raw {branch}: HTTP {resp.status_code}")
                resp.close()
                continue
            buf = b""
            for part in resp.iter_content(8192):
                buf += part
                m = _re.search(rb"PTPScope-(\d+\.\d+\.\d+)", buf)
                if m:
                    resp.close()
                    return m.group(1).decode(), ""
                if len(buf) >= 262144:
                    break
            resp.close()
            errors.append(f"raw {branch}: no version string found")
        except Exception as e:
            errors.append(f"raw {branch}: {e}")

    return "", " | ".join(errors)


def _version_check_loop(stop_ev: threading.Event):
    time.sleep(30)
    while not stop_ev.is_set():
        try:
            ver, err = _fetch_latest_version()
            if ver:
                _UPDATE_STATE["latest"] = ver
                _UPDATE_STATE["error"] = None
            else:
                _UPDATE_STATE["error"] = err or "Could not reach GitHub"
            _UPDATE_STATE["checked_at"] = time.time()
        except Exception as _e:
            _UPDATE_STATE["error"] = f"Version check crashed: {_e}"
        stop_ev.wait(6 * 3600)


@app.get("/api/version_check")
@login_required
def api_version_check():
    current = BUILD.split("-")[-1]
    latest = _UPDATE_STATE.get("latest")
    update = bool(latest and _ver_tuple(latest) > _ver_tuple(current))
    return jsonify({"current": current, "latest": latest,
                    "update_available": update,
                    "checked_at": _UPDATE_STATE.get("checked_at"),
                    "error": _UPDATE_STATE.get("error")})


@app.post("/api/version_check/refresh")
@login_required
@csrf_protect
def api_version_check_refresh():
    """Manually trigger an immediate version check."""
    def _run():
        ver, err = _fetch_latest_version()
        if ver:
            _UPDATE_STATE["latest"] = ver
            _UPDATE_STATE["error"] = None
        else:
            _UPDATE_STATE["error"] = err or "Could not reach GitHub"
        _UPDATE_STATE["checked_at"] = time.time()
    threading.Thread(target=_run, daemon=True, name="VersionCheckOnDemand").start()
    return jsonify({"ok": True, "note": "version check running in background"})


@app.post("/api/update/apply")
@login_required
@csrf_protect
def api_update_apply():
    """Download latest ptpscope.py from GitHub, validate, replace, and restart."""
    import shutil as _shutil, py_compile as _pyc, re as _re

    current_ver = BUILD.split("-")[-1]
    latest_ver = _UPDATE_STATE.get("latest")
    if not latest_ver:
        return jsonify({"error": "No update info available — run a version check first"}), 400
    if _ver_tuple(latest_ver) <= _ver_tuple(current_ver):
        return jsonify({"error": f"Already on latest version ({current_ver})"}), 400

    # Download
    try:
        try:
            import requests as _requests
            resp = _requests.get(_GH_RAW_VER_URL, timeout=60)
            resp.raise_for_status()
            new_bytes = resp.content
        except ImportError:
            import urllib.request
            req = urllib.request.Request(_GH_RAW_VER_URL,
                                        headers={"User-Agent": f"PTPScope/{BUILD}"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                new_bytes = resp.read()
    except Exception as e:
        return jsonify({"error": f"Download failed: {e}"}), 502

    # Sanity-check downloaded file
    text = new_bytes.decode("utf-8", errors="ignore")
    m = _re.search(r"PTPScope-(\d+\.\d+\.\d+)", text)
    if not m:
        return jsonify({"error": "Downloaded file does not look like a valid PTPScope release"}), 502
    dl_ver = m.group(1)
    if _ver_tuple(dl_ver) <= _ver_tuple(current_ver):
        return jsonify({"error": f"Downloaded version ({dl_ver}) is not newer than running ({current_ver})"}), 400

    this_file = os.path.abspath(__file__)
    tmp_path = this_file + ".update_tmp"
    bak_path = this_file + f".bak_{current_ver}"

    # Write temp file and syntax check
    try:
        with open(tmp_path, "wb") as fh:
            fh.write(new_bytes)
        _pyc.compile(tmp_path, doraise=True)
    except Exception as e:
        try: os.remove(tmp_path)
        except OSError: pass
        return jsonify({"error": f"Downloaded file failed syntax check: {e}"}), 502

    # Backup current file
    try:
        _shutil.copy2(this_file, bak_path)
    except Exception as e:
        try: os.remove(tmp_path)
        except OSError: pass
        return jsonify({"error": f"Could not create backup at {bak_path}: {e}"}), 500

    # Atomic replace
    try:
        os.replace(tmp_path, this_file)
    except Exception as e:
        try: _shutil.copy2(bak_path, this_file)
        except OSError: pass
        try: os.remove(tmp_path)
        except OSError: pass
        return jsonify({"error": f"Could not replace application file: {e}"}), 500

    log_fn(f"[Update] ptpscope.py replaced: {current_ver} → {dl_ver}. Restarting in 3 s…")

    # Restart via os.execv (no systemd dependency)
    def _restart():
        time.sleep(3)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            try:
                os.kill(os.getpid(), signal.SIGTERM)
            except Exception:
                sys.exit(0)
    threading.Thread(target=_restart, daemon=True, name="UpdateRestart").start()

    return jsonify({
        "ok": True,
        "from_version": current_ver,
        "to_version": dl_ver,
        "backup": bak_path,
        "note": "Update applied — restarting in 3 s. Page will reload automatically.",
    })


if __name__ == "__main__":
    print(f"[{BUILD}] Starting PTPScope...")
    print(f"[{BUILD}] Base directory: {BASE_DIR}")
    print(f"[{BUILD}] Config: {CONFIG_PATH}")

    stop_events = []
    threads = []

    def _start_thread(name, target, args=()):
        ev = threading.Event()
        stop_events.append(ev)
        t = threading.Thread(target=target, args=(ev, *args), daemon=True, name=name)
        threads.append(t)
        t.start()
        return t

    _role = app_config.node.role
    log_fn(f"[{BUILD}] Node role: {_role}")

    if _role in ("standalone", "gps_source"):
        _start_thread("gps-reader", gps_reader.run, (app_config.gps,))
    if _role in ("standalone", "ptp_master"):
        _start_thread("ptp-manager", ptp_manager.run, (app_config.ptp,))
    if _role == "gps_source":
        _start_thread("hb-sender", hb_sender.run,
                      (gps_reader, chrony_monitor, sys_stats, app_config.node))
    _start_thread("chrony-monitor", chrony_monitor.run)
    _start_thread("sys-stats", sys_stats.run)
    _start_thread("metrics-flush", _metrics_flush_loop)
    _start_thread("daily-prune", _daily_prune_loop)
    _start_thread("version-check", _version_check_loop)

    log_fn(f"[{BUILD}] All background threads started")

    def _shutdown(signum, frame):
        log_fn(f"[{BUILD}] Shutting down (signal {signum})...")
        for ev in stop_events:
            ev.set()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        from waitress import serve
        log_fn(f"[{BUILD}] Serving on http://{app_config.bind_address}:{app_config.web_port}")
        serve(app, host=app_config.bind_address, port=app_config.web_port,
              threads=4, channel_timeout=120)
    except ImportError:
        log_fn(f"[{BUILD}] waitress not found, using Flask dev server")
        app.run(host=app_config.bind_address, port=app_config.web_port,
                debug=False, threaded=True)
