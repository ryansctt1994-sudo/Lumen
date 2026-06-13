# Hardware Targets

Hardware artifacts are Tier 3 preservation candidates.

They are not active enforcement in the current Lumen MVP.

## Governing Rule

```text
Hardware listed here is not hardware authority.
Hardware authority requires synthesis, timing evidence, physical traces, receipts, and independent verification.
```

## Candidate Artifacts

```text
lucifer_latch.v
lucifer_latch_hardened.v
heartbeat_watchdog_v2.v
watchdog.ino
gan_power_stage_if.sv
trace_attestation_engine.sv
dcls_comparator.sv
cathedral_uart_top.v
steward_efuse_ignition.py
eFuse_burn.tcl
gate_h0_temporal_filter.sv
gate_h0_sync_chain.sv
h0_atomic_fsm.sv
```

## Future Validation Requirements

Before any hardware module can be promoted, attach:

```text
selected FPGA / MCU target
source commit hash
synthesis logs
timing reports
simulation traces
physical test report
failure-mode test
receipt package
independent verifier report
```

## Target Metrics

These are target requirements, not achieved claims:

```text
fail-closed behavior
bounded response latency
trace receipt generation
out-of-band liveness check
no software reset after terminal latch
```

Any numeric timing target must be treated as unverified until backed by measurement traces.

## Current Lumen Hardware Status

```text
hardware_veto.py = software simulation only
FPGA enforcement = not implemented
silicon latch = not verified
physical watchdog = not connected
```

## Promotion Path

```text
Tier 3 candidate
→ simulation trace
→ synthesis report
→ physical test
→ receipt artifact
→ independent verification
→ E5 candidate
```

Until then:

```text
Authority: NONE
```
