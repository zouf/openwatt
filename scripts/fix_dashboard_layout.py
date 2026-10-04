import sys

with open('openwatt.html', 'r') as f:
    html = f.read()

start_marker = "<!-- Top Grid -->"
end_marker = "<!-- Middle: Stats Bar & Full Bleed Chart -->"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    sys.exit(1)

new_dashboard = """<!-- Top Radial Dashboard -->
          <div class="flex items-center justify-between w-full px-12 pt-8 pb-4 h-[40%] min-h-[350px]">
            
            <!-- LEFT METRICS -->
            <div class="flex flex-col items-start justify-center space-y-6 w-1/4 bg-[#111] p-6 rounded-2xl border border-[#333]">
              <div class="w-full">
                <div class="text-[10px] font-black tracking-widest text-[#888] uppercase mb-1">Interval Time</div>
                <div id="time-block" class="text-5xl leading-none font-black text-white tracking-tighter">00:00</div>
              </div>
              <div class="w-full pt-4 border-t border-[#333]">
                <div class="text-[10px] font-black tracking-widest text-[#888] uppercase mb-1">Workout Time</div>
                <div id="time-elapsed" class="text-4xl leading-none font-black text-[#ccc] tracking-tighter">0:00:00</div>
                <div id="time-remaining" class="hidden"></div>
              </div>
            </div>

            <!-- CENTER HERO RADIAL -->
            <div class="flex flex-col items-center justify-center w-2/4 relative mt-4">
              <div class="relative flex items-center justify-center w-[280px] h-[280px]">
                
                <!-- Target Arc Background (Grey) -->
                <svg class="absolute inset-0 w-full h-full -rotate-90 drop-shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                  <circle cx="140" cy="140" r="120" stroke="#111" stroke-width="12" fill="none"></circle>
                  <!-- 10s Arc -->
                  <circle id="dial-10s" cx="140" cy="140" r="120" stroke="#ea580c" stroke-width="12" fill="none" stroke-linecap="round" stroke-dasharray="753.9" stroke-dashoffset="753.9" class="transition-all duration-300"></circle>
                  
                  <!-- 3s Arc (Inner) -->
                  <circle cx="140" cy="140" r="102" stroke="#111" stroke-width="6" fill="none"></circle>
                  <circle id="dial-3s" cx="140" cy="140" r="102" stroke="#f97316" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="640.8" stroke-dashoffset="640.8" class="transition-all duration-300"></circle>
                </svg>

                <!-- Central Power Readout -->
                <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
                  <div class="text-[9px] font-black tracking-[0.3em] text-[#888] uppercase">Live Power</div>
                  <div id="val-power" class="text-[85px] leading-none font-black text-white tracking-tighter drop-shadow-[0_0_20px_rgba(234,88,12,0.3)]">0</div>
                  <div id="zone-power" class="text-[9px] font-bold uppercase tracking-widest text-transparent mt-1 h-3"></div>
                </div>
              </div>

              <!-- Target Readout Below -->
              <div class="absolute -bottom-6 flex items-center gap-6 bg-[#0a0a0a] px-6 py-3 rounded-full border border-[#222] shadow-xl shadow-black/50">
                <div class="text-center flex flex-col">
                  <span class="text-[8px] uppercase tracking-widest text-[#888] font-black">Target</span>
                  <span id="val-target" class="text-2xl font-black text-white leading-none">0</span>
                  <div id="val-target-sub" class="hidden"></div>
                </div>
                <div class="w-px h-6 bg-[#333]"></div>
                <div class="flex gap-4">
                  <div class="text-center">
                    <div class="text-[8px] uppercase tracking-widest text-[#ea580c] font-black">3s Avg</div>
                    <div id="val-power-3s" class="text-lg font-bold text-white leading-none">0</div>
                  </div>
                  <div class="text-center">
                    <div class="text-[8px] uppercase tracking-widest text-[#ea580c] font-black">10s Avg</div>
                    <div id="val-power-10s" class="text-lg font-bold text-white leading-none">0</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- RIGHT METRICS -->
            <div class="flex flex-col items-end justify-center space-y-6 w-1/4 bg-[#111] p-6 rounded-2xl border border-[#333]">
              <div class="w-full text-right">
                <div class="text-[10px] font-black tracking-widest text-[#888] uppercase mb-1">Heart Rate</div>
                <div id="val-hr" class="text-5xl leading-none font-black text-white tracking-tighter text-red-500">0</div>
              </div>
              <div class="w-full text-right pt-4 border-t border-[#333]">
                <div class="text-[10px] font-black tracking-widest text-[#888] uppercase mb-1">Cadence</div>
                <div id="val-cadence" class="text-5xl leading-none font-black text-[#ccc] tracking-tighter">0</div>
              </div>
            </div>

          </div>
          """

html = html[:start_idx] + new_dashboard + html[end_idx:]

# Let's also fix the "--" strings replacing them with "0"
# Trainer Status pill style adjustment
# Old: <div id="status-trainer" class="bg-red-600 text-white px-3 py-1 rounded text-[10px] font-bold tracking-widest uppercase flex items-center gap-2">
# New: <div id="status-trainer" class="bg-[#111] text-[#888] border border-[#333] px-3 py-1 rounded text-[10px] font-bold tracking-widest uppercase flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-red-600"></div>Trainer: Offline</div>

html = html.replace('Trainer: Disconnected', '<div class="w-2 h-2 rounded-full bg-[#555]"></div>Trainer: Offline')
html = html.replace('HR: Disconnected', '<div class="w-2 h-2 rounded-full bg-[#555]"></div>HR: Offline')
html = html.replace('bg-red-600 text-white px-3 py-1 rounded', 'bg-[#111] text-[#888] border border-[#333] px-3 py-1 rounded')

with open('openwatt.html', 'w') as f:
    f.write(html)

print("Dashboard fixed!")
