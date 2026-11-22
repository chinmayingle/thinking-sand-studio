# Upload text: "Driver SSD writes" (Short, 57.5 s)

**Title:** Your Idle PC Wrote 30 GB an Hour to Your SSD. Blame the GPU Driver
**Alternates:**
- Nvidia Drivers 621.14 and 621.24 Were Wearing Out SSDs (Check Yours)
- 515 MB in 5 Minutes While Doing Nothing: The Nvidia Driver SSD Bug

**Description:**
Your PC was doing nothing, and your SSD was writing up to 30 GB an hour. That's what users measured on Nvidia's GeForce drivers 621.14 and 621.24.

The culprit is a background service, NVDisplay.Container.exe, rewriting one log file (nvlog.nvlgstg) over and over while the PC sits idle. One user logged 515 MB in five idle minutes on 621.14; the older 621.01 driver wrote under 2 MB. SSDs wear out by writing: a typical 1 TB drive is rated for about 600 TB written, and 30 GB an hour for 8 hours a day would use roughly 15% of that every year. It won't kill a drive overnight, but it's wasted life. As of Nov 21, 2026, Nvidia's GeForce Hotfix 621.35 addresses it (hotfixes are optional betas), and rolling back to 621.01 also helps. To check your own PC: Resource Monitor > Disk tab > sort by Write.

The 30 GB/h and 515 MB figures are user measurements, not Nvidia's numbers. The table of processes in the video uses example numbers.

What did Resource Monitor show on your PC? 👇

Sources:
- Windows Latest, "First AMD, now Nvidia: your GPU driver could be quietly wearing out your Windows 11 PC's SSD" (Nov 20, 2026).
- Wccftech, "Nvidia GPU drivers reportedly writing up to 30GB per hour to SSDs" (Nov 18, 2026) and "Nvidia releases GPU hotfix driver 621.35, fixes excessive SSD writes" (Nov 21, 2026).
- Guru3D, "Reports indicate recent Nvidia GeForce drivers may generate heavy SSD writes" (Nov 2026).

#nvidia #ssd #shorts

**Tags:** nvidia driver ssd writes, nvidia driver bug, geforce 621.24, geforce 621.14, hotfix 621.35, nvdisplay.container.exe, ssd wear, ssd tbw, ssd health, nvidia driver rollback, resource monitor disk, gpu driver, pc tips, the thinking sand

**Pinned comment:** What did Resource Monitor show on your PC? Open it, Disk tab, sort by Write, and tell me the top process 👇

**Captions:** upload out/driver-ssd-writes.srt as English.

**Facts to re-check on upload day:** Hotfix 621.35 status (Nvidia's page nvidia.custhelp.com a_id 5940 couldn't be fetched; the fix is per Wccftech, Nov 21) and whether a regular Game Ready driver now includes the fix. If a newer WHQL driver ships with the fix, change the "fix" line in the description to name it.
