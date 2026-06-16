import re

with open('openwatt.html', 'r') as f:
    html = f.read()

# 1. Fix Layout Collapse Bug
# Replace the container div that restricts width and breaks flex height
html = html.replace('<div class="max-w-7xl mx-auto space-y-6">', '<div class="w-full h-screen flex flex-col">')

# Also, ensure body is truly full screen
html = html.replace('min-h-screen', 'h-screen')

# 2. Apply Black & Orange Theme
# Backgrounds
html = html.replace('bg-[#1e1e1e]', 'bg-black')
html = html.replace('bg-[#1a1a1a]', 'bg-[#111111]')
html = html.replace('bg-[#181818]', 'bg-[#050505]')

# Blue accents -> Orange accents
html = html.replace('bg-blue-600', 'bg-orange-600')
html = html.replace('bg-blue-500', 'bg-orange-500')
html = html.replace('text-blue-600', 'text-orange-600')
html = html.replace('text-blue-500', 'text-orange-500')
html = html.replace('hover:text-blue-400', 'hover:text-orange-400')
html = html.replace('hover:bg-blue-500', 'hover:bg-orange-500')

# Selection color
html = html.replace('selection:bg-blue-500/30', 'selection:bg-orange-500/30')

# 3. Update Chart Color in JS
# We need to find the canvas rendering logic for the blue chart
# It's in function drawProfile() inside openwatt.html
# Example: ctx.fillStyle = 'rgba(59, 130, 246, 0.5)'; (Tailwind blue-500)
html = html.replace("ctx.fillStyle = 'rgba(59, 130, 246, 0.5)';", "ctx.fillStyle = 'rgba(249, 115, 22, 0.8)';") # Orange-500
html = html.replace("ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';", "ctx.fillStyle = 'rgba(249, 115, 22, 0.2)';")

# Also, there's a hardcoded #2563eb (blue-600) for the profile path
html = html.replace("ctx.strokeStyle = '#2563eb';", "ctx.strokeStyle = '#ea580c';") # Orange-600
html = html.replace("ctx.fillStyle = '#2563eb';", "ctx.fillStyle = '#ea580c';") # Orange-600

with open('openwatt.html', 'w') as f:
    f.write(html)

print("Theme and Layout Fixed")
