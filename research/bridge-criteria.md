# What Would Close the One-Column Gap?

The current structural obstacle is simple:

- one eventually periodic column is the hypothesis we want to refute,
- two adjacent eventually periodic columns are enough to drive the known contradiction machinery.

So a successful proof needs a bridge from the first item to the second, or something equally strong.

## Sufficient Bridge Pattern

Any of the following would be enough in principle.

### Bridge A: Recover a Second Adjacent Eventually Periodic Column

If one could prove that eventual periodicity of the center column forces eventual periodicity of either adjacent column, then Proposition 2 in `partial-results.md` would apply immediately.

This is the cleanest possible bridge.

### Bridge B: Recover Any Second Observable That Determines an Adjacent Column

Suppose one can define a derived sequence `d(t)` from the center column alone such that:

1. if the center column is eventually periodic, then `d(t)` is eventually periodic,
2. the pair `(center column, d(t))` determines one adjacent Rule 30 column after some finite transient.

Then one again gets two eventually periodic adjacent columns and the known contradiction machinery starts.

This is the natural target for reconstruction-aware transducers.

Note:

- Proposition 9 in `partial-results.md` already implies that the center column determines the adjacent right column uniquely.
- So the real issue is not existence of such information, but recovering it in a form that preserves eventual periodicity in a usable way.

### Bridge C: Force an Eventually Zero Column Directly From the Center Column Hypothesis

If one could show that eventual periodicity of the center column alone implies the existence of some eventually zero column somewhere to the left, then the left-tail classification from `partial-results.md` would take over.

That would bypass the need to explicitly reconstruct a second adjacent periodic column.

### Bridge D: Contradict the Left-Tail Classification Indirectly

One could also try to show that the center-column hypothesis implies some spacetime property incompatible with the two possible left-tail behaviors forced by an eventually zero column:

- all zeros to the left,
- alternating `...1010` to the left.

This is weaker than Bridge C, but still viable if the contradiction can be made local or combinatorial.

## What Has Been Ruled Out So Far

The following have not produced the needed bridge on current data:

- short local transforms such as `xor-shift`,
- short parity windows,
- the simple stateful transform `running-parity`.

These are still mathematically relevant because eventual periodicity would pass through them, but they do not appear rich enough to recover a second adjacent periodic object.

## Current Best Direction

The most plausible remaining route is Bridge B:

- construct a finite-state or otherwise effective observable from the center column,
- prove it inherits eventual periodicity from the center column,
- prove that together with the center column it determines an adjacent column or an equivalent amount of left-reconstruction data.

Viewed through Proposition 9, this becomes even more specific:

- the adjacent column is already a deterministic functional of the center column,
- the missing ingredient is a representation of that functional with controlled memory or controlled combinatorial complexity.

That would turn the present experimental program into an actual proof template.

## New Direction: Class-Count vs. Period Argument

The recent predictive-state analysis (h=0..20) has opened a new potential proof template:

**Key empirical facts**:
1. |S_h| ~ exp(h^{2/3}) — unbounded, stretched-exponential growth.
2. ALL classes in S_h are reachable from the initial all-zeros state (for h ≤ 16, by BFS).
3. The actual Rule 30 trajectory visits all |S_h| classes (verified up to h=16).
4. Any eventually periodic trajectory visits at most T + p + h distinct classes at horizon h.

**If** fact 3 is proven for all h, then for any fixed p (period) and T (pre-period):  
  T + p + h ≥ |S_h| ~ exp(h^{2/3}) → contradiction for large h.

**The remaining gap**: Prove that the actual Rule 30 center-column-driven trajectory visits
all classes in S_h for every h — not just for h ≤ 16.

This requires showing that the center column's prefixes are complex enough to steer through all
|S_h| right-half configurations. A sufficient condition is that every binary word of length h
appears as a subword of the center column (full block complexity). Full block complexity would
prove non-periodicity directly (it implies non-periodicity of the center column automatically),
so it's a stronger result. A weaker sufficient condition might be enough.

**Intermediate target**: Show that the number of distinct length-h words appearing in the center
column grows faster than any linear function of h. If distinct words ≥ |S_h| ~ exp(h^{2/3}),
and each word steers to a distinct class, then the trajectory must visit ≥ |S_h| classes.

This reformulates the problem as a **subword complexity** question about the center column.