# Performance Analysis

Profile and optimize the specified component or function.

## Workflow

1. **Identify the component**: $ARGUMENTS
2. **Run benchmarks** for the specified area
3. **Generate profiling data** (pprof, flamegraphs, etc.)
4. **Analyze bottlenecks** and hot paths
5. **Suggest optimizations** with expected improvements

## Language-Specific Tools

### Go
- Run `go test -bench` for the component
- Generate pprof CPU and memory profiles
- Create flame graphs if available

### Python
- Use cProfile or line_profiler
- Memory profiling with memory_profiler
- Identify N+1 queries in ORMs

### JavaScript
- Chrome DevTools profiling data
- Lighthouse performance metrics
- Bundle size analysis

### Rust
- cargo bench with criterion
- perf integration for Linux
- valgrind for memory analysis

## Output

Provides:
- Current performance metrics
- Identified bottlenecks
- Recommended optimizations
- Expected performance gains