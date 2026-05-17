# Architecture vocabulary

Apply when the user asks for architecture focus. Use these terms so findings share vocabulary:

- **Module** — anything with an interface and an implementation: function, class, package, slice.
- **Interface** — everything callers must know: types, invariants, ordering, error modes, config, performance.
- **Seam** — where an interface lives; a place behavior can change without editing in place.
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Depth** — leverage at the interface: lots of behavior behind a small interface.
- **Leverage** — caller value from depth.
- **Locality** — change, bugs, and verification concentrated in one place.

Deletion test: if deleting a module makes complexity vanish, it was a pass-through. If complexity reappears across callers, the module was earning its keep.

Seam rule: one adapter means a hypothetical seam; two adapters means a real seam. Do not propose ports without real variation.
