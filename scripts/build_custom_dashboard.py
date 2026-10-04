import re

with open('openwatt.html', 'r') as f:
    html = f.read()

# 1. Add Google Font
font_link = '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;900&display=swap" rel="stylesheet">\n  </head>'
html = html.replace('</head>', font_link)

# Replace body font family
html = html.replace('font-family: ui-sans-serif, system-ui, sans-serif;', "font-family: 'Space Grotesk', system-ui, sans-serif;")

# 2. Add History State
state_str_old = "telemetry: { power: 0, target: 0, cadence: 0, hr: 0 },"
state_str_new = "telemetry: { power: 0, target: 0, cadence: 0, hr: 0, powerHistory: [], power3s: 0, power10s: 0 },"
html = html.replace(state_str_old, state_str_new)

# 3. Update Trainer Payload logic to calculate rolling averages
payload_old = """        if (flags & (1 << 6)) {
          state.telemetry.power = val.getInt16(offset, true);
          offset += 2;
        }"""
payload_new = """        if (flags & (1 << 6)) {
          const power = val.getInt16(offset, true);
          state.telemetry.power = power;
          
          const now = Date.now();
          state.telemetry.powerHistory.push({t: now, v: power});
          // Remove old data > 10.5 seconds
          state.telemetry.powerHistory = state.telemetry.powerHistory.filter(x => now - x.t <= 10500);
          
          const p3 = state.telemetry.powerHistory.filter(x => now - x.t <= 3000);
          const p10 = state.telemetry.powerHistory.filter(x => now - x.t <= 10000);
          
          state.telemetry.power3s = p3.length ? Math.round(p3.reduce((a,b) => a+b.v, 0)/p3.length) : power;
          state.telemetry.power10s = p10.length ? Math.round(p10.reduce((a,b) => a+b.v, 0)/p10.length) : power;
          
          offset += 2;
        }"""
html = html.replace(payload_old, payload_new)

# 4. Replace Top Grid with Custom Radial Dashboard Layout
# Note: we are replacing the entire 'div class="grid grid-cols-3 w-full px-12 pt-8 pb-4 h-[40%] min-h-[250px]"'
# We'll use re.sub to make sure we grab the right block
pattern = r'<div\s+class="grid grid-cols-3 w-full px-12 pt-8 pb-4 h-\[40%\] min-h-\[250px\]">.*?</div>\s+<!-- CENTER: Interval Time & Workout Time -->.*?</div>\s+<!-- RIGHT: Heart Rate & Cadence -->.*?</div>\s+</div>'

new_dashboard = """<div class="flex items-center justify-between w-full px-16 pt-10 pb-6 h-[45%] min-h-[350px]">
          
          <!-- LEFT METRICS -->
          <div class="flex flex-col items-start justify-center space-y-12 w-1/4">
            <div>
              <div class="text-[12px] font-black tracking-widest text-[#666] uppercase mb-1">Interval Time</div>
              <div id="time-block" class="text-6xl leading-none font-black text-white tracking-tighter">00:00</div>
            </div>
            <div>
              <div class="text-[12px] font-black tracking-widest text-[#666] uppercase mb-1">Workout Time</div>
              <div id="time-elapsed" class="text-6xl leading-none font-black text-white tracking-tighter">0:00:00</div>
              <div id="time-remaining" class="hidden"></div>
            </div>
          </div>

          <!-- CENTER HERO RADIAL -->
          <div class="flex flex-col items-center justify-center w-2/4 relative">
            <div class="relative flex items-center justify-center w-[300px] h-[300px]">
              
              <!-- Target Arc Background (Grey) -->
              <svg class="absolute inset-0 w-full h-full -rotate-90">
                <circle cx="150" cy="150" r="130" stroke="#111" stroke-width="15" fill="none"></circle>
                <!-- 10s Arc -->
                <circle id="dial-10s" cx="150" cy="150" r="130" stroke="#ea580c" stroke-width="15" fill="none" stroke-linecap="round" stroke-dasharray="816.8" stroke-dashoffset="816.8" class="transition-all duration-300"></circle>
                <!-- 3s Arc (Inner) -->
                <circle cx="150" cy="150" r="110" stroke="#111" stroke-width="8" fill="none"></circle>
                <circle id="dial-3s" cx="150" cy="150" r="110" stroke="#f97316" stroke-width="8" fill="none" stroke-linecap="round" stroke-dasharray="691.1" stroke-dashoffset="691.1" class="transition-all duration-300"></circle>
              </svg>

              <!-- Central Power Readout -->
              <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
                <div class="text-[10px] font-black tracking-[0.3em] text-[#888] uppercase">Live Power</div>
                <div id="val-power" class="text-[90px] leading-none font-black text-white tracking-tighter drop-shadow-[0_0_20px_rgba(234,88,12,0.3)]">0</div>
                <div id="zone-power" class="text-[10px] font-bold uppercase tracking-widest text-transparent mt-1 h-3"></div>
              </div>
            </div>

            <!-- Target Readout Below -->
            <div class="absolute -bottom-6 flex items-center gap-6 bg-[#111] px-6 py-3 rounded-full border border-[#333]">
              <div class="text-center flex flex-col">
                <span class="text-[9px] uppercase tracking-widest text-[#888] font-black">Target</span>
                <span id="val-target" class="text-3xl font-black text-white leading-none">0</span>
                <div id="val-target-sub" class="hidden"></div>
              </div>
              <div class="w-px h-8 bg-[#333]"></div>
              <div class="flex gap-4">
                <div class="text-center">
                  <div class="text-[9px] uppercase tracking-widest text-[#ea580c] font-black">3s Avg</div>
                  <div id="val-power-3s" class="text-xl font-bold text-white">0</div>
                </div>
                <div class="text-center">
                  <div class="text-[9px] uppercase tracking-widest text-[#ea580c] font-black">10s Avg</div>
                  <div id="val-power-10s" class="text-xl font-bold text-white">0</div>
                </div>
              </div>
            </div>
          </div>

          <!-- RIGHT METRICS -->
          <div class="flex flex-col items-end justify-center space-y-12 w-1/4">
            <div class="text-right">
              <div class="text-[12px] font-black tracking-widest text-[#666] uppercase mb-1">Heart Rate</div>
              <div id="val-hr" class="text-6xl leading-none font-black text-white tracking-tighter text-red-500">---</div>
            </div>
            <div class="text-right">
              <div class="text-[12px] font-black tracking-widest text-[#666] uppercase mb-1">Cadence</div>
              <div id="val-cadence" class="text-6xl leading-none font-black text-white tracking-tighter">---</div>
            </div>
          </div>

        </div>"""

html = re.sub(pattern, new_dashboard, html, flags=re.DOTALL)

# 5. Add updating logic for the dials in renderTelemetryLoop
render_old = """      function renderTelemetryLoop() {
        document.getElementById("val-power").innerText = state.telemetry.power;"""

render_new = """      function renderTelemetryLoop() {
        document.getElementById("val-power").innerText = state.telemetry.power;
        
        // Update rolling average numbers
        const p3El = document.getElementById("val-power-3s");
        if (p3El) p3El.innerText = state.telemetry.power3s || 0;
        const p10El = document.getElementById("val-power-10s");
        if (p10El) p10El.innerText = state.telemetry.power10s || 0;

        // Update SVG Dials
        // Dial Circumference 10s (r=130): ~816.8
        // Dial Circumference 3s (r=110): ~691.1
        const target = state.telemetry.target > 0 ? state.telemetry.target : 1;
        const pct10s = Math.min(Math.max((state.telemetry.power10s || 0) / target, 0), 1.5); // Cap visual at 150%
        const pct3s = Math.min(Math.max((state.telemetry.power3s || 0) / target, 0), 1.5);
        
        const dial10s = document.getElementById("dial-10s");
        if (dial10s) {
          const offset10s = 816.8 - (816.8 * pct10s);
          dial10s.style.strokeDashoffset = offset10s;
          dial10s.setAttribute("stroke", (pct10s > 1.05) ? "#ef4444" : "#ea580c"); // Red if over target
        }
        
        const dial3s = document.getElementById("dial-3s");
        if (dial3s) {
          const offset3s = 691.1 - (691.1 * pct3s);
          dial3s.style.strokeDashoffset = offset3s;
          dial3s.setAttribute("stroke", (pct3s > 1.05) ? "#ef4444" : "#f97316"); // Lighter orange or red
        }
"""
html = html.replace(render_old, render_new)

with open('openwatt.html', 'w') as f:
    f.write(html)

print("Custom Dashboard Applied")
