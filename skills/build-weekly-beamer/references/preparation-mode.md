# Next-meeting preparation mode

Use this mode when meeting N has a reviewed summary but meeting N+1 has not yet occurred or has not yet been reviewed.

## Follow-up ledger

Extract material items from these summary sections:

- Decisions made that require implementation or validation;
- Open Questions;
- Pending Confirmation;
- Action items;
- Key outcomes only when they contain a concrete requested check or unresolved consequence.

Assign a stable, human-facing number such as `Item 1`. Preserve that number as evidence arrives and when the item appears in later decks. Do not display meeting codes or contributor initials in the item label unless the user asks for them. Record:

- compact request or question;
- owner, or `Unassigned`;
- hypothesis or answer being tested;
- required evidence: plot, table, metric, external PDF, or confirmation;
- comparison, selection, category, or success criterion;
- current status;
- source summary and source lines.

For an artifact revision, also record:

- prior artifact filename and date;
- exact requested change, such as an added selection, region, uncertainty, or table column;
- replacement artifact filename, or the specific missing input needed to create it.

## Preparation states

- `awaiting evidence` - requested work or answer has no supplied result yet;
- `in progress` - dated evidence shows work has started but does not resolve the item;
- `blocked` - a stated dependency prevents progress;
- `needs confirmation` - supplied evidence or ownership is ambiguous;
- `done` - evidence satisfies the recorded success criterion and the conclusion is supported.

Do not use `not discussed` before N+1 has occurred. After the reviewed N+1 summary exists, use `not discussed` only when that summary contains no follow-up on the item.

## Skeleton construction

1. State the N-to-N+1 goal and why it matters.
2. Immediately after the title, show one whole-team frame titled `Follow-up items` with `Item`, `Responsible`, `Follow-up`, and `Status` columns.
3. Include every assigned contributor in that overview before beginning the presenting contributor's detailed workstream.
4. Group related detailed items by workstream or contributor. Do not repeat an
   item/request/status strip on each frame; the opening overview is
   authoritative. Keep an item number in a title only when it aids navigation.
5. Create one evidence frame per distinct hypothesis or direct comparison. Label each placeholder with its stable item number and the exact artifact needed.
6. Put decision-relevant evidence in a roughly 15-frame main narrative. Place
   supporting plots, alternate selections, full tables, and provenance after
   `\appendix`; never add filler to reach the target.
7. Add a carry-forward frame containing every item not marked `done`. Keep its owner and missing evidence visible.
8. End with decisions expected at N+1 and the criteria for drawing each conclusion.

When an expected artifact does not exist, leave the labeled placeholder in the deck. Do not fabricate a result or write a conclusion in advance.

Compile the preparation skeleton and deliver both its editable `.tex` and
visually inspected `.pdf`. Evidence placeholders are valid; a missing PDF is not.

## Updating before and after N+1

Before N+1, label supplied results `pre-meeting evidence` with their creation date. Update the corresponding item, but do not claim the next meeting discussed or accepted it.

When meeting N requests an edited plot or table, create a versioned replacement
when the required data are available. Preserve the earlier artifact for the
old-to-new differential. Use `build-hep-validation-plots` for regenerated HEP
figures; update tables directly only from supplied, traceable values.

At N+1, unresolved items remain in the to-do frame. After its summary is reviewed, reconcile every stable item number:

- record the meeting-time status and evidence;
- use `not discussed` where appropriate;
- carry unresolved items into N+2;
- add new N+1 actions with new item numbers;
- record explicitly closed or dropped items so they do not silently disappear.
