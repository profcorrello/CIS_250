# Implementation Plan - Library Management System

# Goal Description

Implement the core backend logic for the Library Management System, focusing on Inter-Library Loans (ILL), Fine Management, and Hold Queues as defined in the Scope Statement. The goal is to ensure all service layers are robust, interconnected, and fully capable of handling the defined workflows (state transitions, policy enforcements).

## User Review Required

> [!IMPORTANT]
> **Hold Expiry & Notifications**: The system logic for expiring holds and promoting the next user (`process_hold_expiry`, `promote_next_hold`) exists in the service layer but is not currently triggered by any scheduled job. For this phase, these will remain as manual API trigger points or logically integrated into specific book return workflows, as no background scheduler (e.g., Celery) is currently in scope.

## Proposed Changes

### Database Layer

#### [MODIFY] [models.py](file:///home/clayc/projects/Library_System/models.py)

- Ensure all foreign keys and relationships are correctly set up for cascading (if necessary) or orphan handling.
- Verify `Fine` and `Hold` models align with the expanded service logic requirements (e.g., ensures `created_at` or `expiry` fields are sufficient).

### Core Services

#### [MODIFY] [ill_service.py](file:///home/clayc/projects/Library_System/ill_service.py)

- Enhance `update_ill_status` to enforce valid state transitions (e.g., cannot go from `Draft` to `Received` directly).
- Add validation to ensure `partner_library_id` is present when moving to `Submitted` or `In Transit`.

#### [MODIFY] [fines_service.py](file:///home/clayc/projects/Library_System/fines_service.py)

- specific `pay_fine` function to handle partial or full payments and update `is_paid` status.
- Ensure `calculate_fine` logic is fully exposed via API for "preview" or automated daily calculations if needed.

#### [MODIFY] [holds_service.py](file:///home/clayc/projects/Library_System/holds_service.py)

- Refine `create_hold` to check:
  1. If the book is actually unavailable (if available, user should check it out, not hold).
  2. If the user already has a hold on this book.
- Ensure `promote_next_hold` is called when a book is returned (will need coordination with a Check-In endpoint).

#### [MODIFY] [patron_service.py](file:///home/clayc/projects/Library_System/patron_service.py)

- Ensure `patron_type` validation is enforced during creation to match the keys in `FINE_CONFIG`.

### API Layer

#### [MODIFY] [main.py](file:///home/clayc/projects/Library_System/main.py)

- **New Endpoint**: `POST /fines/{fine_id}/pay` to record payments.
- **New Endpoint**: `POST /books/{book_id}/return` (or similar) to handle book returns, which calculates final fines and triggers `promote_next_hold`.
- **Refinement**: Ensure ILL status updates use a dedicated endpoint or patch method for state transitions.

## Verification Plan

### Automated Tests

- **Unit Tests**:
  - Test fine calculation with various patron/item types and overdue durations.
  - Test ILL state transitions (valid and invalid).
  - Test Hold queue logic (FIFO order, expiry).

### Manual Verification

1. **ILL Flow**: Create request -> Update status through lifecycle -> Verify DB state.
2. **Fine Flow**: Create overdue item -> Calculate fine -> Pay fine -> Verify `is_paid`.
3. **Hold Flow**:
   - Patron A holds Book X.
   - Patron B holds Book X.
   - Return Book X -> Verify Patron A is notified/active.
   - Expire Patron A's hold -> Verify Patron B becomes active.
