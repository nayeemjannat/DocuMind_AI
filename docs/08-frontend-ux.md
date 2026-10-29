# 08 — Frontend and UX Specification

## Main screens

1. Landing / product overview.
2. Sign up and sign in.
3. Workspace list and create workspace.
4. Workspace detail with document list and upload control.
5. Document processing state/detail.
6. Conversation view with question input, answer, and citations.
7. Conversation history.
8. Loading, empty, error, quota-exceeded, and not-found states.

## UX principles

- Keep the interface calm, clean, and professional; avoid unnecessary visual effects and crowded layouts.
- Make the primary action obvious.
- Show upload limits before or during upload.
- Show processing state and whether a document is ready for questions.
- Distinguish evidence-backed answers from insufficient-evidence responses.
- Make citations clickable or expandable to reveal the supporting excerpt.
- Show page number only when reliable.
- Explain errors in simple language without exposing internal diagnostics.
- Provide keyboard-accessible controls, visible focus states, meaningful labels, and readable contrast.
- Support mobile and desktop layouts.
- Confirm destructive actions such as deleting a document.
- Do not pretend a request succeeded until the API confirms it.

## Conversation behavior

- Disable or clearly guard duplicate submissions while a question is processing.
- Display a useful empty state before the first question.
- Render citations beside the answer they support.
- If an answer has no valid citation, treat it as a validation failure or insufficient-evidence result, not a normal grounded answer.
- Handle provider errors and rate limits with a safe retry message.

## Accessibility and polish checklist

- Every input has an accessible label.
- All actions are reachable by keyboard.
- Loading and failure states are announced or otherwise perceivable.
- Text remains readable at common viewport sizes.
- Errors are adjacent to the relevant control when possible.
- Destructive actions require clear confirmation.
