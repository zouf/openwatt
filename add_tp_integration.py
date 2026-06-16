import re

with open('openwatt.html', 'r') as f:
    html = f.read()

# 1. Add Dropzone UI to the end of the <body>
dropzone_html = """
    <div id="dropzone" class="fixed inset-0 z-[100] hidden bg-black/90 flex flex-col items-center justify-center border-8 border-dashed border-[#ea580c] transition-all">
      <div class="text-[80px] font-black tracking-tighter text-white uppercase mb-4 text-center leading-none">Drop TrainingPeaks<br>.ZWO File Here</div>
      <div class="text-xl font-bold tracking-widest text-[#ea580c] uppercase">Instantly load your Workout of the Day</div>
    </div>
  </body>"""

html = html.replace('</body>', dropzone_html)

# 2. Add JavaScript logic for Drag and Drop and ZWO Parsing
# We will inject it right before the last </script> tag
zwo_script = """
      /**
       * TrainingPeaks ZWO Drag-and-Drop Integration
       */
      const dropzone = document.getElementById("dropzone");

      window.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.remove("hidden");
      });

      dropzone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dropzone.classList.add("hidden");
      });

      window.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.add("hidden");

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          const file = e.dataTransfer.files[0];
          if (file.name.toLowerCase().endsWith(".zwo")) {
            const reader = new FileReader();
            reader.onload = function(event) {
              parseZWO(event.target.result);
            };
            reader.readAsText(file);
          } else {
            alert("Please drop a .zwo file exported from TrainingPeaks.");
          }
        }
      });

      function parseZWO(xmlText) {
        try {
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(xmlText, "text/xml");
          
          const nameNode = xmlDoc.getElementsByTagName("name")[0];
          const name = nameNode ? nameNode.textContent : "TrainingPeaks Workout";
          
          let blocks = [];
          const workoutNode = xmlDoc.getElementsByTagName("workout")[0];
          if (!workoutNode) throw new Error("No <workout> tag found.");

          const children = workoutNode.children;
          for (let i = 0; i < children.length; i++) {
            const node = children[i];
            const tag = node.tagName;
            
            if (tag === "SteadyState") {
              const d = parseInt(node.getAttribute("Duration"));
              const p = parseFloat(node.getAttribute("Power"));
              blocks.push({ d: d, p: p });
            } else if (tag === "Warmup" || tag === "Cooldown") {
              const d = parseInt(node.getAttribute("Duration"));
              const pLow = parseFloat(node.getAttribute("PowerLow"));
              const pHigh = parseFloat(node.getAttribute("PowerHigh"));
              // Create 10 stepping blocks to simulate a ramp
              const steps = 10;
              const stepDuration = Math.floor(d / steps);
              const pDiff = (pHigh - pLow) / steps;
              for(let s=0; s<steps; s++) {
                blocks.push({ d: stepDuration, p: pLow + (pDiff * s) });
              }
            } else if (tag === "IntervalsT") {
              const repeat = parseInt(node.getAttribute("Repeat"));
              const onD = parseInt(node.getAttribute("OnDuration"));
              const offD = parseInt(node.getAttribute("OffDuration"));
              const onP = parseFloat(node.getAttribute("OnPower"));
              const offP = parseFloat(node.getAttribute("OffPower"));
              for(let r=0; r<repeat; r++) {
                blocks.push({ d: onD, p: onP });
                blocks.push({ d: offD, p: offP });
              }
            } else if (tag === "FreeRide") {
              const d = parseInt(node.getAttribute("Duration"));
              blocks.push({ d: d, p: 0.5 }); // Set freeride to a default 50%
            }
          }

          if (blocks.length > 0) {
            state.activeWorkout = {
              name: name,
              desc: "Imported via Drag-and-Drop",
              blocks: blocks
            };
            state.clockTime = 0;
            state.activeBlockIndex = 0;
            state.blockTimeElapsed = 0;
            processActiveWorkoutTimeline();
            
            // Re-render immediately
            document.getElementById("time-elapsed").innerText = "0:00:00";
            document.getElementById("time-block").innerText = "00:00";
            
            alert(`Successfully loaded: ${name}`);
          }
        } catch (err) {
          console.error(err);
          alert("Failed to parse the .zwo file. Ensure it is a valid XML export from TrainingPeaks.");
        }
      }
"""

html = html.replace('</script>\n  </body>', zwo_script + '\n    </script>\n  </body>')

with open('openwatt.html', 'w') as f:
    f.write(html)

print("TP Integration Added!")
