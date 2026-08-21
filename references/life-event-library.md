# Life-Event Library and Call Chain

Life events are small, concrete changes that make a scene lived-in: an object is misplaced, a routine is interrupted, a request arrives at a bad time, a social obligation collides with the scene goal, or a minor mistake leaves a residue. They are not random accidents and must not rewrite the story's facts.

## Event card

Each card should contain:

- `event_id`, title, status, and one-sentence root event;
- source binding or explicit `INLINE_CANDIDATE` authorization;
- eligible characters, locations, time window, and knowledge boundary;
- pressure or trigger, target object/person, and intended narrative function;
- a visible chain of 2—6 steps;
- an interruption or abort point;
- `state_in`, `state_out`, and a residue that can change a later action;
- risk limits, forbidden outcomes, and merge/reuse notes.

Use `assets/life-event-card.template.json` as a copyable card. Valid lifecycle labels are `DRAFT`, `READY`, `ADOPTED`, `REJECTED_OR_MERGED`, `REVIEW_FLAG`, and `NOT_USED`.

## Call chain

1. **Inventory**: read only the authorized library or inline candidates. Record the library identity and source bindings.
2. **Filter**: remove candidates that violate scene time, place, character permission, knowledge boundary, facts, tone, or ending requirements.
3. **Select**: choose root event IDs and write a short selection reason. Do not silently add a second root event.
4. **Seed**: pass only the selected root event and its constraints to the writing pass. The writer may construct the direct 2—6 step chain, but may not scan the whole library for another event.
5. **Assemble**: place the chain in the scene and preserve the selected scene function. A chain counts as one event unit, not one unit per step.
6. **Postcheck**: extract the actual steps, actor/target changes, abort point, `state_out`, and residue from the produced prose. Verify that the residue changes a later action or explicitly record `NO_RESIDUE_INTENDED`.
7. **Disposition**: mark `ADOPTED`, `REJECTED_OR_MERGED`, `REVIEW_FLAG`, or `NOT_USED`; record why. Never promote a rejected or historical card without a new selection record.

The default autonomous-unit ceiling is configurable; five is a practical starting point, not a universal quota. If the event would change a major plot choice, causal order, relationship state, technical claim, or ending interface, return to the structured-input stage instead of treating it as decoration.

## What the library does not authorize

It does not authorize new facts, hidden knowledge, precise motives, scientific claims, a different point of view, or a new plot result. A life event may create friction and residue; it cannot erase required consequences or reset the scene after an interruption.
