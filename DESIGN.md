# ACP 练习台 Design System

## 1. Atmosphere & Identity

Quiet study workstation: dense progress information sits above a readable question surface. The signature is a restrained teal accent against paper-white panels and a deep teal sidebar.

## 2. Color

| Role | Token | Value | Usage |
|---|---|---|---|
| Text primary | `--ink` | `#17212b` | Questions and controls |
| Text secondary | `--muted` | `#66727d` | Metadata and hints |
| Surface page | `--paper` | `#f7f9fa` | Body background |
| Surface card | `--card` | `#ffffff` | Activity and question panels |
| Border | `--line` | `#e1e7eb` | Panel and control outlines |
| Accent | `--teal` | `#0e7c78` | Active controls and selection |
| Accent strong | `--teal-dark` | `#075e5b` | Hover and emphasized text |
| Warning | `--amber` | `#e6a23c` | Favorite and missed-answer state |
| Error | `--red` | `#c85151` | Wrong-answer state |

## 3. Typography

System sans stack with CJK fallbacks. Body text is 15px/1.65; compact metadata and legends use 11px-13px; question text uses 19px desktop and 18px mobile.

## 4. Spacing & Layout

The app uses a 4px-derived rhythm, a 280px fixed sidebar on desktop, and a single-column flow below 760px. The main content is capped at 980px. Activity grids own horizontal overflow when their fixed cells exceed the available width.

## 5. Components

### Activity panel

- Structure: heading/status, fixed-cell progress grid, filter cluster, legend.
- States: unfiltered, category-filtered, current pending question, completed, favorite, wrong, chopped.
- Accessibility: native checkboxes and buttons; current state is represented by `?` and selected cells retain focusable buttons.

### Question card

- Structure: question metadata, prompt, option buttons, answer note, controls.
- States: selected, correct, wrong, missed (multi-select), favorite, chopped.
- Accessibility: options and actions are keyboard-reachable buttons with visible focus.

### Filter and reset controls

- Structure: multi-select checkbox cluster with a nearby reset button.
- Behavior: category choices filter the matching activity cells; reset confirms before clearing the selected progress scope.

## 6. Motion & Interaction

Controls use short ease-out transitions for hover and selection. No essential information depends on motion; reduced-motion users receive the same states without animation.

## 7. Depth & Surface

Mixed treatment: 1px borders define panels and controls, while the question card uses the existing subtle shadow token. Small progress cells use flat semantic colors for rapid scanning.

## 8. Accessibility Constraints & Accepted Debt

Target WCAG 2.2 AA contrast, visible focus for interactive controls, native keyboard semantics, and no horizontal overflow in primary content at 375px. Existing inline CSS remains compact for this small vanilla app; broader token extraction is accepted debt for a future component split.
