import re

with open('openwatt.html', 'r') as f:
    content = f.read()

old_load = """      if (saved.buttonConfig) state.buttonConfig = saved.buttonConfig;"""
new_load = """      if (saved.buttonConfig) {
        // Migration from bitmask format to button format
        if (saved.buttonConfig.bindings && saved.buttonConfig.bindings.length > 0 && saved.buttonConfig.bindings[0].byteIndex !== undefined) {
          console.log("Migrating old bitmask bindings to new format");
          // Keep defaults instead of corrupted state
        } else {
          state.buttonConfig = saved.buttonConfig;
        }
      }"""
content = content.replace(old_load, new_load)

with open('openwatt.html', 'w') as f:
    f.write(content)
