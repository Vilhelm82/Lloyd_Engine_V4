# Protocol Contracts

A protocol declaration is a typed composition contract between a result producer and a result consumer. It states what statuses may be emitted, what statuses may be consumed, which fields are required, and when scalarization is forbidden.

The design aims toward static checkability. Early Python implementation uses strict runtime validation while preserving enough structure for later static tooling.

## Producer Protocol

A producer protocol declares:

- producer name and operation identity
- emitted status set
- output space
- required provenance fields
- whether scalarization is never, conditionally, or always available

## Consumer Protocol

A consumer protocol declares:

- consumer name
- accepted status set
- required validity fields
- required provenance fields
- forbidden scalarizations
- uncertainty policy
- exhaustive handling requirement

## Required Contract Concepts

Accepted status set: The exact statuses a consumer can handle.

Required fields: Validity, conditioning, metrology, and provenance fields needed by the consumer.

Forbidden scalarizations: Statuses for which conversion to scalar is invalid even if a raw value happens to exist.

Exhaustive handling requirement: Every producer status must either be accepted, refused, or routed to protocol uncertainty by name.

Protocol violation result: A typed result or check emitted when a consumer receives an unhandled status.

Protocol uncertainty result: A typed result or check emitted when the contract cannot prove compatibility but does not have enough evidence for a hard violation.

Test verification: Tests should construct a producer result with a status outside the consumer accepted set and assert a protocol violation. Tests should also verify required-field rejection and scalarization refusal paths.

## Pseudocode

```python
class ConsumerProtocol:
    accepted_strata: set[StatusCode]
    required_validity_fields: set[str]
    scalarization_allowed: bool
```

```python
def validate_protocol(result: TypedResult, consumer: ConsumerProtocol) -> ProtocolCheck:
    if missing_required_fields(result, consumer):
        return ProtocolCheck.violation("missing required fields")
    if result.status not in consumer.accepted_statuses:
        return ProtocolCheck.violation("unhandled status")
    if scalarization_requested(result) and not consumer.scalarization_allowed:
        return ProtocolCheck.violation("scalarization forbidden")
    return ProtocolCheck.ok()
```

No protocol may adapt results to V3 or downgrade typed status into legacy booleans.
