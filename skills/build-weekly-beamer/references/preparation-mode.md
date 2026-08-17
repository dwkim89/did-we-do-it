# Next-meeting preparation mode

Use this mode when meeting N has a reviewed summary but meeting N+1 has not yet occurred or has not yet been reviewed.

## Follow-up ledger

Extract material items from these summary sections:

- Decisions made that require implementation or validation;
- Open Questions;
- Pending Confirmation;
- Action items;
- Key outcomes only when they contain a concrete requested check or unresolved consequence.

Assign a stable ID such as `N-01`. Preserve that ID as evidence arrives and when the item appears in later decks. Record:

- compact request or question;
- owner, or `Unassigned`;
- hypothesis or answer being tested;
- required evidence: plot, table, metric, external PDF, or confirmation;
- comparison, selection, category, or success criterion;
- current status;
- source summary and source lines.

## Preparation states

- `awaiting evidence` - requested work or answer has no supplied result yet;
- `in progress` - dated evidence shows work has started but does not resolve the item;
- `blocked` - a stated dependency prevents progress;
- `needs confirmation` - supplied evidence or ownership is ambiguous;
- `done` - evidence satisfies the recorded success criterion and the conclusion is supported.

Do not use `not discussed` before N+1 has occurred. After the reviewed N+1 summary exists, use `not discussed` only when that summary contains no follow-up on the item.

## Skeleton construction

1. State the N-to-N+1 goal and why it matters.
2. Show the meeting N follow-up ledger.
3. Group related items by workstream or contributor.
4. Create one evidence frame per distinct hypothesis or direct comparison. Label each placeholder with its stable ID and the exact artifact needed.
5. Add a carry-forward frame containing every item not marked `done`. Keep its owner and missing evidence visible.
6. End with decisions expected at N+1 and the criteria for drawing each conclusion.

When an expected artifact does not exist, leave the labeled placeholder in the deck. Do not fabricate a result or write a conclusion in advance.

Compile the preparation skeleton and deliver both its editable `.tex` and
visually inspected `.pdf`. Evidence placeholders are valid; a missing PDF is not.

## Updating before and after N+1

Before N+1, label supplied results `pre-meeting evidence` with their creation date. Update the corresponding item, but do not claim the next meeting discussed or accepted it.

At N+1, unresolved items remain in the to-do frame. After its summary is reviewed, reconcile every stable ID:

- record the meeting-time status and evidence;
- use `not discussed` where appropriate;
- carry unresolved items into N+2;
- add new N+1 actions with new stable IDs;
- record explicitly closed or dropped items so they do not silently disappear.
