# Upload text: "Compiler free speed" (Short, 56.4 s)

**Title:** Same CPU, Same Code, 6.5% Faster. Only the Compiler Changed
**Alternates:**
- A Free Update Made the Same CPU 6.5% Faster
- 19 Instructions Became 10. Your CPU Got Faster for Free

**Description:**
Same chip. Same code. Up to 6.5% faster, and nobody touched the hardware. The only thing that changed was the compiler.

A compiler turns the code people write into the instructions your CPU actually runs. Smarter compilers find ways to do the same job with fewer instructions. This week Microsoft's C++ compiler (MSVC 14.52, Visual Studio 2026) learned to turn 19 separate memory loads into 10 on Arm laptops by loading two values at once. ServeTheHome rebuilt the SPEC CPU 2026 benchmark with LLVM 22 instead of LLVM 20: about 4% faster on an Intel Core Ultra 9 285HX, 5% on an AMD Ryzen AI Max+ 395 and 6.5% on Nvidia's Arm-based GB10 (DGX Spark). It's uneven: one encryption test more than doubled (+129%), while a board-game AI test got 3% slower on AMD. Every app and game on your PC went through a compiler, so when developers rebuild with a newer one, you get the speed for free.

Which app on your PC do you wish ran faster? 👇

Sources:
- ServeTheHome, "The Case For Compilers: A Look at SPEC CPU 2026 on LLVM 22" (May 10, 2026). LLVM 20.1.8 vs 22.1.4, SPECrate integer, full system, base rates; ServeTheHome's own unofficial estimates.
- Microsoft C++ Team Blog, "C++ Optimizations in MSVC Build Tools 14.52" (Nov 17, 2026).

#programming #cpu #shorts

**Tags:** compiler explained, what does a compiler do, llvm 22, msvc, visual studio 2026, compiler optimization, free performance, cpu performance, spec cpu 2026, arm laptop, windows on arm, how code runs on cpu, programming explained, the thinking sand

**Pinned comment:** Which app on your PC do you wish ran faster? Name it 👇 (Bonus: has an update ever made something noticeably faster for you?)

**Captions:** upload out/compiler-free-speed.srt as English.

**Facts to re-check on upload day:** 6.5% / 5% / 4% are ServeTheHome's full-system SPECrate integer uplifts (LLVM 22 vs 20), labelled unofficial estimates. +129% is 750.sealcrypto_r on the DGX Spark; -3% is 707.ntest_r (an Othello engine) on AMD (-3.1%). "19 loads into 10" = MSVC 14.52's ARM64 example: 19 indexed loads → nine ldp + one ldr. The speed-up only reaches an app when its developers rebuild it with the newer compiler.
