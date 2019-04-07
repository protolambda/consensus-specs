# State transition tests

Tests the bigger transitions with a list of blocks,
 compared to other tests that care about very specific parts of the transition.

## Format:

```yaml
# encoded BeaconState, all fields
pre: <key/value map>
# A list of blocks to be processed sequentially on top of the initial state
blocks: <list of key/value maps, each encoding a BeaconBlock>
# Encoded BeaconState, optionally only a subset of fields of the state, containing the expected values of the resulting state
post: <key/value map>
```
