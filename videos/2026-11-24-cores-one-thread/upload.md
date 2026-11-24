# Upload text: "cores one thread" (Short, 56.9 s)

**Title:** 16 Cores vs 8 Cores: Only 1.4% More FPS. Here's Why
**Alternates:**
- Twice the CPU Cores, 1.4% More FPS. Your Game Waits on One
- Why Games Don't Use All Your CPU Cores (Amdahl's Law)

**Description:**
A 16-core Ryzen 9 7950X vs an 8-core Ryzen 7 7700X in Gears of War: E-Day: 130.6 vs 128.8 FPS. That's 1.4%, in a game Tom's Hardware calls unusually CPU-heavy. And the 8-core 9800X3D beat both at 168.7 FPS.

Why? Each frame, one thread runs the game itself: input, AI, physics. Unreal Engine even calls it the game thread. Other cores take the side jobs, and more cores make those side jobs shorter, but the frame still waits for the game thread. That's Amdahl's law: the part that can't be split sets the limit. If half of a frame is stuck on one thread, 8 cores make it 1.78x faster, 16 cores 1.88x, and no number of cores gets past 2x.

How many cores does your CPU have? 👇

Sources (as of Nov 24, 2026):
- Tom's Hardware, "Gears of War: E-Day is an uncharacteristically CPU-heavy Unreal Engine 5 game: benchmarking 25 CPUs..." (Jake Roach, Oct 1, 2026). RTX 5090, 1080p, High preset; average FPS.
- Unreal Engine documentation, "Threaded Rendering" (the game thread and the rendering thread).
- Amdahl's law (Gene Amdahl, 1967). The 50% split is an illustration, not a measurement of this game.
The 7950X and 7700X also differ in clock speed and layout, so this is a comparison of real chips, not a pure core-count test.

#cpu #gaming #shorts

**Tags:** 16 cores vs 8 cores, how many cores for gaming, do games use all cores, 7950x vs 7700x, 9800x3d, gears of war e-day benchmark, cpu cores gaming, amdahl's law, game thread, main thread bottleneck, best gaming cpu 2026, cpu bottleneck, unreal engine 5 cpu, the thinking sand

**Pinned comment:** How many cores does your CPU have, and have you ever seen a game use all of them? Drop your CPU below 👇

**Captions:** upload out/cores-one-thread.srt as English.

**Facts to re-check on upload day:** nothing time-sensitive; the numbers are from a fixed Oct 1, 2026 test. "One sixty-nine" in the voice is 168.7 rounded.
