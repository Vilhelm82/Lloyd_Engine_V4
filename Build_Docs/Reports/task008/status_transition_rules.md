# Task 008 Status Transition Rules

| rule | input protocol | output protocol | input family | output family | accepted statuses | refused statuses | mapped statuses | context keys | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `history.record_event` | any V4 typed-result producer | `history_event` | `Enum` | `HistoryStatus` | none | none | contextual source status to `history_event_recorded` | `stream_id`, `observation_key`, `step_index` | The API validates a concrete `TypedResult` and emits compact event evidence. |
| `history.event_pair.compare` | `history_event` | `history_transition` | `HistoryStatus` | `HistoryStatus` | `history_event_recorded` | none | contextual pair comparison statuses | `previous_event`, `next_event` | Pairwise classification uses precedence: incomparable, protocol, family, status, validity, geometry, stable. |
| `history.events.to_trace` | `history_event` | `history_trace` | `HistoryStatus` | `HistoryStatus` | `history_event_recorded` | none | contextual trace summary statuses | `events` | Trace classification uses caller order and does not sort or repair events. |
| `history.trace.require_stable` | `history_trace` | `stable_history_trace` | `HistoryStatus` | none | `history_trace_stable` | `history_trace_empty`, `history_trace_singleton`, `history_trace_transitioned`, `history_trace_incomplete`, `history_trace_unordered` | none | Enforced by `require_stable_status_trace`. |

Generic mixed-family joins remain conservative. History records mixed-family changes through named transition evidence rather than a universal join.
