# ETH 2.0 config helpers

`preset_loader`: A util to load constants-presets with.
See [Constants-presets documentation](../../configs/constants_presets/README.md).

Usage:

```python
import preset_loader
from eth2spec.phase0 import spec
my_presets = preset_loader.load_presets('main_net')
spec.apply_constants_preset(my_presets)
```

WARNING: this is quite hacky, it relies on import order. Overwrite constants before loading them elsewhere.
