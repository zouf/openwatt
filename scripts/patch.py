import re

with open('openwatt.html', 'r') as f:
    content = f.read()

# 1. Update bindings state
content = re.sub(
    r"bindings:\s*\[\s*\{\s*byteIndex:\s*3,\s*bitIndex:\s*0,\s*action:\s*'bias_up'\s*},\s*\{\s*byteIndex:\s*3,\s*bitIndex:\s*1,\s*action:\s*'bias_down'\s*\}\s*\],\s*lastPayload:\s*\[\]",
    "bindings: [\n          { buttonId: '0001', action: 'skip' },\n          { buttonId: '8000', action: 'restart' }\n        ],\n        lastPayload: []",
    content
)

# 2. Update btn-add-binding HTML
content = content.replace(">+ Add Bit Binding<", ">+ Add Button Binding<")

# 3. Prevent GC in BLE connection
content = content.replace(
    "char.addEventListener('characteristicvaluechanged', handleWahooButtonPayload);\n                subscribedAny = true;\n                console.log",
    "char.addEventListener('characteristicvaluechanged', handleWahooButtonPayload);\n                subscribedAny = true;\n                if (!state.ble.wahooChars) state.ble.wahooChars = [];\n                state.ble.wahooChars.push(char);\n                console.log"
)

# 4. Replace handleWahooButtonPayload logic
old_handler = """    const lastPayloadsByUUID = {};
    function handleWahooButtonPayload(e) {
      const charUuid = e.target.uuid;
      const val = e.target.value;
      let bytes = [];
      for(let i=0; i<val.byteLength; i++) bytes.push(val.getUint8(i));
      
      const hexStr = bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ');
      const binStr = bytes.map(b => b.toString(2).padStart(8, '0')).join(' ');
      document.getElementById('raw-byte-stream').innerText = hexStr;
      document.getElementById('raw-binary-stream').innerText = binStr;
      
      const lastPayload = lastPayloadsByUUID[charUuid] || [];
      
      if (lastPayload.length > 0) {
        for (let i = 0; i < bytes.length; i++) {
          if (i >= lastPayload.length) break;
          const oldByte = lastPayload[i];
          const newByte = bytes[i];
          
          if (oldByte !== newByte) {
            const flipped = oldByte ^ newByte;
            for (let bit = 0; bit < 8; bit++) {
              if (flipped & (1 << bit)) {
                const isHigh = (newByte & (1 << bit)) !== 0;
                logEvent(`Char ${charUuid.split('-')[0]} | Byte ${i}, Bit ${bit} went ${isHigh ? 'HIGH' : 'LOW'}`);
                
                // Trigger action if button is pressed (HIGH)
                if (isHigh && state.buttonConfig.enabled) {
                  const binding = state.buttonConfig.bindings.find(b => b.byteIndex === i && b.bitIndex === bit);
                  if (binding && binding.action !== 'none') {
                    executeBoundAction(binding.action);
                  }
                }
              }
            }
          }
        }
      }
      lastPayloadsByUUID[charUuid] = [...bytes];
    }"""

new_handler = """    const WAHOO_BUTTON_MAP = {
      '0001': 'Right Hood: Up',
      '8000': 'Right Hood: Down',
      '0008': 'Right Hood: Inside',
      '0200': 'Left Hood: Up',
      '0400': 'Left Hood: Down',
      '2000': 'Left Hood: Inside',
      '0004': 'Right Shifter: Up',
      '0002': 'Right Shifter: Down',
      '1000': 'Left Shifter: Up',
      '0800': 'Left Shifter: Down',
      '4000': 'Right Brake',
      '0100': 'Left Brake'
    };

    function handleWahooButtonPayload(e) {
      const val = e.target.value;
      let bytes = [];
      for(let i=0; i<val.byteLength; i++) bytes.push(val.getUint8(i));
      
      const hexStr = bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ');
      const binStr = bytes.map(b => b.toString(2).padStart(8, '0')).join(' ');
      document.getElementById('raw-byte-stream').innerText = hexStr;
      document.getElementById('raw-binary-stream').innerText = binStr;
      
      if (bytes.length === 3) {
        const prefix = bytes.map(b => b.toString(16).padStart(2, '0').toUpperCase()).slice(0, 2).join('');
        const buttonName = WAHOO_BUTTON_MAP[prefix] || `Unknown (${prefix})`;
        const isPressed = (bytes[2] & 0x80) !== 0;
        
        if (isPressed) {
          logEvent(`PRESSED: ${buttonName}`);
          if (state.buttonConfig.enabled) {
            const binding = state.buttonConfig.bindings.find(b => b.buttonId === prefix);
            if (binding && binding.action !== 'none') {
              executeBoundAction(binding.action);
            }
          }
        } else {
          logEvent(`RELEASED: ${buttonName}`);
        }
      }
    }"""
content = content.replace(old_handler, new_handler)


# 5. Replace buildUIElements renderer logic
old_ui = """      const bindingsContainer = document.getElementById('button-bindings');
      bindingsContainer.innerHTML = '';
      state.buttonConfig.bindings.forEach((binding, index) => {
        const row = document.createElement('div');
        row.className = 'flex items-center gap-2 justify-between bg-slate-900 p-2 rounded border border-slate-700';
        
        let byteOpts = '';
        for(let i=0; i<15; i++) byteOpts += `<option value="${i}" ${binding.byteIndex===i?'selected':''}>Byte ${i}</option>`;
        
        let bitOpts = '';
        for(let i=0; i<8; i++) bitOpts += `<option value="${i}" ${binding.bitIndex===i?'selected':''}>Bit ${i}</option>`;
        
        let actOpts = '';
        ACTION_REGISTRY.forEach(act => {
          actOpts += `<option value="${act.id}" ${binding.action===act.id?'selected':''}>${act.name}</option>`;
        });

        row.innerHTML = `
          <select class="bind-byte bg-slate-800 border border-slate-600 rounded p-1 text-[10px] text-slate-200" data-idx="${index}">${byteOpts}</select>
          <select class="bind-bit bg-slate-800 border border-slate-600 rounded p-1 text-[10px] text-slate-200" data-idx="${index}">${bitOpts}</select>
          <span class="text-slate-500 font-bold">→</span>
          <select class="bind-action bg-slate-800 border border-slate-600 rounded p-1 text-[10px] text-slate-200 flex-1" data-idx="${index}">${actOpts}</select>
          <button class="bind-delete text-red-500 hover:text-red-400 font-bold px-2" data-idx="${index}">✕</button>
        `;
        bindingsContainer.appendChild(row);
      });

      // Bindings events
      document.querySelectorAll('.bind-byte').forEach(el => el.addEventListener('change', (e) => {
        state.buttonConfig.bindings[e.target.dataset.idx].byteIndex = parseInt(e.target.value, 10);
        saveStorage();
      }));
      document.querySelectorAll('.bind-bit').forEach(el => el.addEventListener('change', (e) => {
        state.buttonConfig.bindings[e.target.dataset.idx].bitIndex = parseInt(e.target.value, 10);
        saveStorage();
      }));"""

new_ui = """      const bindingsContainer = document.getElementById('button-bindings');
      bindingsContainer.innerHTML = '';
      state.buttonConfig.bindings.forEach((binding, index) => {
        const row = document.createElement('div');
        row.className = 'flex items-center gap-2 justify-between bg-slate-900 p-2 rounded border border-slate-700';
        
        let btnOpts = '';
        Object.entries(WAHOO_BUTTON_MAP).forEach(([prefix, name]) => {
          btnOpts += `<option value="${prefix}" ${binding.buttonId===prefix?'selected':''}>${name}</option>`;
        });
        
        let actOpts = '';
        ACTION_REGISTRY.forEach(act => {
          actOpts += `<option value="${act.id}" ${binding.action===act.id?'selected':''}>${act.name}</option>`;
        });

        row.innerHTML = `
          <select class="bind-btn bg-slate-800 border border-slate-600 rounded p-1 text-[10px] text-slate-200 flex-1" data-idx="${index}">${btnOpts}</select>
          <span class="text-slate-500 font-bold">→</span>
          <select class="bind-action bg-slate-800 border border-slate-600 rounded p-1 text-[10px] text-slate-200 flex-1" data-idx="${index}">${actOpts}</select>
          <button class="bind-delete text-red-500 hover:text-red-400 font-bold px-2" data-idx="${index}">✕</button>
        `;
        bindingsContainer.appendChild(row);
      });

      // Bindings events
      document.querySelectorAll('.bind-btn').forEach(el => el.addEventListener('change', (e) => {
        state.buttonConfig.bindings[e.target.dataset.idx].buttonId = e.target.value;
        saveStorage();
      }));"""
content = content.replace(old_ui, new_ui)

# 6. Add new binding logic fix
content = content.replace("state.buttonConfig.bindings.push({ byteIndex: 3, bitIndex: 0, action: 'none' });", "state.buttonConfig.bindings.push({ buttonId: '0001', action: 'none' });")

with open('openwatt.html', 'w') as f:
    f.write(content)
