import re

with open('openwatt.html', 'r') as f:
    html = f.read()

# 1. Update Body
html = html.replace('<body class="p-6">', '<body class="bg-[#1e1e1e] text-slate-200 selection:bg-blue-500/30 font-sans min-h-screen flex flex-col overflow-hidden">')

# 2. Update Header
old_header = """    <header class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-800 p-4 rounded-xl border border-slate-700 gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
          OpenWatt <span class="text-xs font-mono font-normal bg-slate-700 px-2 py-1 rounded text-slate-400">v1.0.0</span>
        </h1>
        <p class="text-xs text-slate-400 mt-1">Direct BLE FTMS control cockpit • No servers, no tracking</p>
      </div>
      
      <div class="flex items-center gap-3 flex-wrap">
        <div id="profile-chips" class="flex gap-2"></div>
        <button id="btn-add-profile" class="bg-slate-700 hover:bg-slate-600 text-white font-mono text-sm px-3 py-1.5 rounded-lg border border-slate-600 transition">
          + Add Profile
        </button>
      </div>
    </header>"""

new_header = """    <header class="flex justify-between items-center px-4 py-2 bg-[#1a1a1a] border-b border-[#333]">
      <div class="flex items-center gap-6">
        <h1 class="text-lg font-black tracking-tighter text-white">OpenWatt</h1>
        <nav class="flex space-x-4 text-xs font-bold tracking-widest uppercase">
          <button onclick="switchTab('workout')" id="nav-workout" class="text-blue-500 transition hover:text-blue-400">Workout</button>
          <button onclick="switchTab('devices')" id="nav-devices" class="text-slate-500 transition hover:text-slate-300">Devices</button>
          <button onclick="switchTab('profile')" id="nav-profile" class="text-slate-500 transition hover:text-slate-300">Profile</button>
        </nav>
      </div>
      
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <label class="text-[10px] uppercase font-bold text-slate-500 tracking-widest">Workout:</label>
          <select id="select-workout" class="bg-[#111] text-white border border-[#333] rounded px-2 py-1 text-xs font-bold focus:outline-none"></select>
          <input type="file" id="file-input" class="hidden" accept=".zwo,.erg,.mrc" />
          <button onclick="document.getElementById('file-input').click()" class="bg-[#333] hover:bg-[#444] px-2 py-1 text-[10px] uppercase tracking-widest font-bold rounded text-white transition">Upload File</button>
        </div>
        <div class="w-px h-6 bg-[#333]"></div>
        <div id="profile-chips" class="flex gap-2 text-xs"></div>
        <button id="btn-add-profile" class="bg-[#333] hover:bg-[#444] text-white font-bold text-[10px] uppercase tracking-widest px-2 py-1 rounded transition">
          + Profile
        </button>
      </div>
    </header>"""

if old_header in html:
    html = html.replace(old_header, new_header)

# 3. Build new main and tabs
new_main = """    <main class="flex-1 flex flex-col relative">

      <!-- TAB: WORKOUT (TrainerRoad Replica) -->
      <section id="tab-workout" class="flex-1 flex flex-col w-full h-full block absolute inset-0">
        
        <!-- Top Grid -->
        <div class="grid grid-cols-3 w-full px-12 pt-8 pb-4 h-[40%] min-h-[250px]">
          
          <!-- LEFT: Power & Target -->
          <div class="flex flex-col items-center justify-center space-y-8">
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Power</div>
              <div id="val-power" class="text-[80px] leading-none font-black font-sans text-white tracking-tighter">---</div>
              <div id="zone-power" class="text-[9px] font-bold uppercase tracking-widest text-transparent mt-1 h-3"></div>
            </div>
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Target</div>
              <div id="val-target" class="text-[100px] leading-none font-black font-sans text-white tracking-tighter drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">0</div>
              <div id="val-target-sub" class="hidden"></div>
            </div>
          </div>

          <!-- CENTER: Interval Time & Workout Time -->
          <div class="flex flex-col items-center justify-center space-y-8">
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Interval Time</div>
              <div id="time-block" class="text-[110px] leading-none font-black font-sans text-white tracking-tighter">00:00</div>
            </div>
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Workout Time</div>
              <div id="time-elapsed" class="text-[110px] leading-none font-black font-sans text-white tracking-tighter">0:00:00</div>
              <div id="time-remaining" class="hidden"></div>
            </div>
          </div>

          <!-- RIGHT: Heart Rate & Cadence -->
          <div class="flex flex-col items-center justify-center space-y-8">
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Heart Rate</div>
              <div id="val-hr" class="text-[80px] leading-none font-black font-sans text-white tracking-tighter">---</div>
            </div>
            <div class="text-center">
              <div class="text-[11px] font-bold tracking-[0.25em] text-[#aaaaaa] uppercase mb-1">Cadence</div>
              <div id="val-cadence" class="text-[80px] leading-none font-black font-sans text-white tracking-tighter">---</div>
            </div>
          </div>

        </div>

        <!-- Middle: Stats Bar & Full Bleed Chart -->
        <div class="flex-1 w-full flex flex-col relative bg-[#181818] border-t border-[#333]">
          
          <!-- Stats Bar -->
          <div class="w-full flex justify-between items-center px-4 py-2 border-b border-[#333] text-[9px] font-bold text-[#888888] uppercase tracking-[0.2em] bg-[#1a1a1a]">
            <div class="text-lg leading-none cursor-pointer hover:text-white">≡</div>
            <div class="flex gap-12">
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>INT POW</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>INT HR</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>INT CAD</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>TSS</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>TOTAL KJ</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>NP</div></div>
              <div class="text-center"><div class="text-white text-xs font-black tracking-widest mb-0.5">---</div><div>AVG POW</div></div>
            </div>
            <div class="cursor-pointer hover:text-white">STATS ∧</div>
          </div>

          <!-- Charts -->
          <div class="relative flex-1 w-full overflow-hidden mt-8">
            <div id="indicator-target-strip" class="hidden"></div>
            <div id="indicator-power-strip" class="hidden"></div>
            <!-- Huge canvas taking up bottom half completely -->
            <canvas id="canvas-profile" width="1200" height="400" class="absolute inset-0 w-full h-full opacity-60 mix-blend-screen"></canvas>
            <canvas id="canvas-trace" width="1200" height="400" class="absolute inset-0 w-full h-full"></canvas>
          </div>
          
        </div>

        <!-- Bottom Footer Bar -->
        <div class="h-14 w-full bg-[#1a1a1a] border-t border-[#333] flex justify-between items-center px-4">
          
          <!-- Intensity Control -->
          <div class="flex items-center gap-1 bg-[#111] px-1 py-1 rounded border border-[#333]">
            <button id="btn-bias-down" class="text-[#888] hover:text-white px-2 text-xs font-bold">v</button>
            <span id="label-bias" class="text-white font-bold text-xs tracking-widest min-w-[50px] text-center">100%</span>
            <button id="btn-bias-up" class="text-[#888] hover:text-white px-2 text-xs font-bold">^</button>
            <input id="slider-bias" type="range" min="50" max="150" step="1" value="100" class="hidden">
          </div>

          <!-- Device Status -->
          <div class="flex items-center gap-4">
            <div id="status-trainer" class="bg-red-600 text-white px-3 py-1 rounded text-[10px] font-bold tracking-widest uppercase flex items-center gap-2">
              Trainer: Disconnected
            </div>
            <div id="status-hr" class="bg-red-600 text-white px-3 py-1 rounded text-[10px] font-bold tracking-widest uppercase flex items-center gap-2">
              HR: Disconnected
            </div>
          </div>

          <!-- Controls -->
          <div class="flex gap-2">
            <button id="btn-seg-restart" class="bg-[#333] hover:bg-[#444] text-white font-bold py-1.5 px-3 rounded text-[10px] tracking-widest uppercase transition">Restart</button>
            <button id="btn-seg-minus" class="bg-[#333] hover:bg-[#444] text-white font-bold py-1.5 px-3 rounded text-[10px] tracking-widest uppercase transition">- 30s</button>
            <button id="btn-seg-plus" class="bg-[#333] hover:bg-[#444] text-white font-bold py-1.5 px-3 rounded text-[10px] tracking-widest uppercase transition">+ 1 Min</button>
            <button id="btn-seg-skip" class="bg-[#333] hover:bg-[#444] text-white font-bold py-1.5 px-3 rounded text-[10px] tracking-widest uppercase transition">Skip</button>
            <button id="btn-engine-control" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-1.5 px-6 rounded text-xs tracking-widest transition uppercase ml-2">Start</button>
          </div>
          
        </div>
      </section>

      <!-- TAB: DEVICES -->
      <section id="tab-devices" class="hidden w-full h-full absolute inset-0 overflow-y-auto p-8 bg-[#1e1e1e]">
        <div class="max-w-3xl mx-auto space-y-8">
          <div class="bg-[#1a1a1a] p-6 rounded-xl border border-[#333] space-y-6">
            <h2 class="text-xl font-bold tracking-tighter text-white">Hardware Connectivity</h2>
            <div class="grid grid-cols-2 gap-4">
              <button id="btn-connect-trainer" class="bg-blue-600 hover:bg-blue-500 text-white font-bold tracking-widest uppercase py-3 rounded-lg text-xs transition">Connect Trainer</button>
              <button id="btn-connect-hr" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold tracking-widest uppercase py-3 rounded-lg text-xs transition">Connect HR Strap</button>
            </div>
          </div>

          <div class="bg-[#1a1a1a] p-6 rounded-xl border border-[#333] space-y-6">
            <div class="flex justify-between items-center">
              <h2 class="text-xl font-bold tracking-tighter text-white">KICKR Bike Buttons</h2>
              <input type="checkbox" id="chk-buttons-enable" class="w-4 h-4 text-blue-600 bg-[#111] border-[#333] rounded">
            </div>
            
            <div class="space-y-4">
              <div class="bg-[#111] p-4 rounded-lg font-mono text-[#888] border border-[#333] space-y-2 text-xs">
                <div class="text-[10px] uppercase font-bold tracking-widest">Raw Data Stream Inspector</div>
                <div id="raw-byte-stream" class="text-slate-300">00 00 00 00</div>
                <div id="raw-binary-stream" class="text-[#555]">00000000</div>
                <div class="mt-2 text-[10px] bg-black p-2 rounded h-24 overflow-y-auto" id="event-log">
                  <div class="italic text-[#555]">Press buttons to see bitmask changes...</div>
                </div>
              </div>

              <div class="space-y-2 pt-4 border-t border-[#333]" id="button-bindings"></div>
              <button id="btn-add-binding" class="w-full bg-[#333] hover:bg-[#444] text-white font-bold uppercase tracking-widest text-[10px] py-2 rounded transition">+ Add Button Binding</button>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB: PROFILE -->
      <section id="tab-profile" class="hidden w-full h-full absolute inset-0 overflow-y-auto p-8 bg-[#1e1e1e]">
        <div class="max-w-xl mx-auto space-y-8">
          <div class="bg-[#1a1a1a] p-6 rounded-xl border border-[#333] space-y-6">
            <div class="flex justify-between items-center">
              <h2 class="text-xl font-bold tracking-tighter text-white">Execution Mode</h2>
              <div class="flex bg-[#111] p-1 rounded-lg border border-[#333]">
                <button id="mode-erg" class="px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition bg-blue-600 text-white">ERG</button>
                <button id="mode-sim" class="px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition text-[#666]">SIM</button>
              </div>
            </div>
            
            <div id="sim-controls" class="hidden space-y-4 bg-[#111] p-5 rounded-lg border border-[#333]">
              <div class="flex justify-between items-center">
                <label class="text-xs uppercase font-bold tracking-widest text-[#888]">Virtual Grade</label>
                <span id="label-grade" class="text-xl font-black font-sans text-white">0.0%</span>
              </div>
              <input id="slider-grade" type="range" min="-10" max="20" step="0.5" value="0" class="w-full h-2 bg-[#333] rounded-lg appearance-none">
              <div class="grid grid-cols-2 gap-2">
                <button id="btn-grade-down" class="bg-[#222] hover:bg-[#333] text-white text-[10px] font-bold uppercase tracking-widest py-2 rounded">-0.5%</button>
                <button id="btn-grade-up" class="bg-[#222] hover:bg-[#333] text-white text-[10px] font-bold uppercase tracking-widest py-2 rounded">+0.5%</button>
              </div>
            </div>
          </div>
        </div>
      </section>

    </main>"""

# Replace old <main> section entirely
old_main_match = re.search(r'(<main class="grid grid-cols-1 lg:grid-cols-3 gap-6">.*?</main>)', html, re.DOTALL)
if old_main_match:
    html = html.replace(old_main_match.group(1), new_main)

# Add Javascript for switchTab
js_insert = """
    function switchTab(tabId) {
      ['workout', 'devices', 'profile'].forEach(id => {
        document.getElementById('tab-' + id).classList.remove('block');
        document.getElementById('tab-' + id).classList.add('hidden');
        document.getElementById('nav-' + id).classList.remove('text-blue-500');
        document.getElementById('nav-' + id).classList.add('text-slate-500');
      });
      document.getElementById('tab-' + tabId).classList.remove('hidden');
      document.getElementById('tab-' + tabId).classList.add('block');
      document.getElementById('nav-' + tabId).classList.remove('text-slate-500');
      document.getElementById('nav-' + tabId).classList.add('text-blue-500');
    }
"""

if "function switchTab(" not in html:
    html = html.replace("const WORKOUT_PRESETS = [", js_insert + "\n    const WORKOUT_PRESETS = [")

with open('openwatt.html', 'w') as f:
    f.write(html)

print("TR Clean Rebuild Done")
