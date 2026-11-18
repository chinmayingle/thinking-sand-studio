# Upload text: "Why your SSD drops from 5 GB/s to 800 MB/s" (Short, 57.5 s)

**Title:** Your 5 GB/s SSD Gets 6× Slower. Here's Why (SLC Cache)
**Alternates:**
- Why Your NVMe SSD Slows Down After 600 GB
- 5,000 MB/s to 800 MB/s: The SSD Speed Nobody Mentions

**Description:**
Your SSD says 5 GB a second. Copy enough and it drops to about 800 MB/s, 6× slower.

In TechPowerUp's test, a 2 TB WD Black SN7100 held about 5 GB/s for 648 GB, then fell to about 800 MB/s.
Why: flash cells store 3 bits as one of 8 voltage levels, which is slow to write. So the drive writes 1 bit per cell first: the SLC cache.
1 bit instead of 3 uses 3× the space, the cache is built from free space, and a nearly full drive gets a tiny one.

How full is your game drive right now? 👇

Sources: TechPowerUp, WD Black SN7100 2 TB review (write-intensive test); Igor's Lab, "What does dynamic pSLC cache actually mean?"

#ssd #pcbuild #shorts

**Tags:** ssd slc cache, why is my ssd slow, nvme ssd slow down, ssd write speed drop, slc cache explained, tlc vs slc, wd black sn7100, nvme vs sata, ssd buying guide, black friday ssd, how ssds work, the thinking sand

**Pinned comment:** How full is your game drive right now? Under 50% or living dangerously at 95%? 👇

**Captions:** upload out/ssd-slc-cache.srt as English.

**Facts to re-check on upload day:** nothing time-sensitive; the numbers are from one drive's review, empty drive, single-thread sequential writes. Other drives have different cache sizes (some use a small fixed cache).
