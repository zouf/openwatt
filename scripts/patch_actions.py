import re

with open('openwatt.html', 'r') as f:
    content = f.read()

# 1. Update ACTION_REGISTRY
old_registry = """    const ACTION_REGISTRY = [
      { id: 'none', name: 'None' },
      { id: 'skip', name: 'Skip Section' },
      { id: 'restart', name: 'Restart Section' },
      { id: 'plus30', name: '+30s on Section' },
      { id: 'minus30', name: '-30s on Section' },
      { id: 'bias_up', name: 'Bias +2%' },
      { id: 'bias_down', name: 'Bias -2%' },
      { id: 'grade_up', name: 'Grade +0.5%' },
      { id: 'grade_down', name: 'Grade -0.5%' },
      { id: 'toggle_mode', name: 'Toggle ERG/SIM' },
      { id: 'play_pause', name: 'Start/Pause' }
    ];"""

new_registry = """    const ACTION_REGISTRY = [
      { id: 'none', name: 'None' },
      { id: 'skip', name: 'Skip Section' },
      { id: 'restart', name: 'Restart Section' },
      { id: 'plus30', name: '+30s on Section' },
      { id: 'minus30', name: '-30s on Section' },
      { id: 'bias_up', name: 'Bias +2%' },
      { id: 'bias_down', name: 'Bias -2%' },
      { id: 'bias_up_1', name: 'Bias +1%' },
      { id: 'bias_down_1', name: 'Bias -1%' },
      { id: 'grade_up', name: 'Grade +0.5%' },
      { id: 'grade_down', name: 'Grade -0.5%' },
      { id: 'toggle_mode', name: 'Toggle ERG/SIM' },
      { id: 'set_erg', name: 'Set ERG Mode' },
      { id: 'set_sim', name: 'Set SIM Mode' },
      { id: 'play_pause', name: 'Start/Pause' }
    ];"""
content = content.replace(old_registry, new_registry)

# 2. Update executeBoundAction
old_execute = """      if (actionId === 'bias_up' || actionId === 'bias_down') {
        const diff = actionId === 'bias_up' ? 2 : -2;
        const slider = document.getElementById('slider-bias');
        slider.value = Math.min(150, Math.max(50, parseInt(slider.value, 10) + diff));
        slider.dispatchEvent(new Event('input'));
      }"""

new_execute = """      if (actionId === 'set_erg') setExecutionMode('ERG');
      if (actionId === 'set_sim') setExecutionMode('SIM');
      if (actionId.startsWith('bias_')) {
        let diff = 0;
        if (actionId === 'bias_up') diff = 2;
        if (actionId === 'bias_down') diff = -2;
        if (actionId === 'bias_up_1') diff = 1;
        if (actionId === 'bias_down_1') diff = -1;
        const slider = document.getElementById('slider-bias');
        slider.value = Math.min(150, Math.max(50, parseInt(slider.value, 10) + diff));
        slider.dispatchEvent(new Event('input'));
      }"""
content = content.replace(old_execute, new_execute)

# 3. Update default bindings state
old_bindings = """        bindings: [
          { buttonId: '0001', action: 'skip' },
          { buttonId: '8000', action: 'restart' }
        ]"""
new_bindings = """        bindings: [
          { buttonId: '0001', action: 'bias_up_1' },
          { buttonId: '8000', action: 'bias_down_1' },
          { buttonId: '2000', action: 'set_erg' },
          { buttonId: '0008', action: 'set_sim' }
        ]"""
content = content.replace(old_bindings, new_bindings)

with open('openwatt.html', 'w') as f:
    f.write(content)
