# TypeScript Review Slice

Language-specific review material for TypeScript 5.x. The host skill supplies scope, workflow, and the findings/output contract — this file supplies only the TypeScript tooling, version-specific traps, and focus-area checks.

## Run tooling first

Execute these before manual review to catch issues programmatically:

```bash
# Type checking
bunx tsc --noEmit 2>&1

# Run tests
bun test 2>&1

# Security audit
npm audit --production 2>&1
```

Include tool output in findings. Security issues are blocking. Focus manual review on files flagged by tools plus direct callers found via LSP. Do not scan the entire codebase manually.

If a tool is not installed or fails, note the failure in findings and continue with manual review of remaining focus areas. Do not attempt to install missing tools.

## LSP navigation (trace security-sensitive data flow)

- `goToDefinition` — trace function calls to understand data flow
- `findReferences` — find all callers of security-sensitive functions
- `incomingCalls` — trace who calls a function (input validation checks)
- `goToImplementation` — find concrete implementations of interfaces

## Logic correctness

- Type assumptions at runtime: TypeScript types don't exist at runtime — external data must be validated

```typescript
// BAD: trusting runtime data
type Status = "pending" | "approved" | "rejected";
const status: Status = req.body.status; // could be anything at runtime!

// GOOD: runtime validation
const StatusSchema = z.enum(["pending", "approved", "rejected"]);
const status = StatusSchema.parse(req.body.status);
```

- Exhaustiveness errors: missing cases in discriminated union switches
- Null/undefined handling: missing guards before dereferencing
- Off-by-one errors: array bounds, loop boundaries
- Floating promises: promises not awaited (silently fails)

## Security (OWASP)

### Injection (SQL/NoSQL/Command)

```typescript
// BAD: SQL injection
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// GOOD: parameterized query
const result = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);

// BAD: command injection
exec(`ping -c 1 ${host}`);

// GOOD: use execFile with array args
execFile("ping", ["-c", "1", host]);

// BAD: NoSQL injection (MongoDB)
const user = await User.findOne({ username: req.query.username }); // could be {"$ne": null}

// GOOD: validate first
const { username } = UsernameSchema.parse(req.query);
const user = await User.findOne({ username });
```

### XSS (Cross-Site Scripting)

```typescript
// BAD: unescaped user input in HTML
res.send(`<h1>Hello ${req.query.name}</h1>`);

// GOOD: escape or use templating engine that escapes by default
import { escape } from "lodash";
res.send(`<h1>Hello ${escape(name)}</h1>`);
```

### Broken Access Control (IDOR)

```typescript
// BAD: no ownership check
app.get("/api/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  res.json(order); // any user can access any order!
});

// GOOD: verify ownership
app.get("/api/orders/:id", async (req, res) => {
  const order = await Order.findOne({
    _id: req.params.id,
    userId: req.user.id, // ownership check
  });
  if (!order) return res.status(404).end();
  res.json(order);
});
```

### Prototype Pollution

```typescript
// BAD: spreading untrusted data
const settings = { ...defaultSettings, ...req.body }; // __proto__ pollution possible

// GOOD: validate and whitelist fields
const input = SettingsSchema.parse(req.body);
const settings = { ...defaultSettings, ...input };
```

### Sensitive data exposure

- Logging secrets: tokens, passwords in logs
- Weak crypto: MD5/SHA1 for passwords — use bcrypt/argon2
- Insecure cookies: missing httpOnly, secure, sameSite

```typescript
// BAD: weak password hashing
const hash = crypto.createHash("sha1").update(password).digest("hex");

// GOOD: use bcrypt
import bcrypt from "bcryptjs";
const hash = await bcrypt.hash(password, 12);

// BAD: insecure cookie
res.cookie("session", token);

// GOOD: secure cookie
res.cookie("session", token, {
  httpOnly: true,
  secure: true,
  sameSite: "lax",
});
```

## Performance

### Blocking event loop

```typescript
// BAD: sync I/O in request handler
app.get("/report", (req, res) => {
  const data = fs.readFileSync("/big/file.json", "utf8");
  res.json(JSON.parse(data));
});

// GOOD: streaming or async
app.get("/report", async (req, res) => {
  const stream = fs.createReadStream("/big/file.json");
  stream.pipe(res);
});
```

### N+1 queries

```typescript
// BAD: sequential queries in loop
for (const id of userIds) {
  const user = await getUserById(id);
  users.push(user);
}

// GOOD: batch query
const users = await getUsersByIds(userIds);
// or
const users = await Promise.all(userIds.map(getUserById));
```

### Missing timeouts

```typescript
// BAD: no timeout on external call
const response = await fetch(url);

// GOOD: with timeout
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 5000);
try {
  const response = await fetch(url, { signal: controller.signal });
} finally {
  clearTimeout(timeout);
}
```

## Security configuration

- CORS misconfiguration: `origin: '*'` with credentials
- Missing helmet: no security headers
- Debug in production: verbose errors, stack traces exposed

```typescript
// BAD: permissive CORS
app.use(cors());

// GOOD: restricted CORS
app.use(
  cors({
    origin: ["https://app.example.com"],
    credentials: true,
  }),
);

// GOOD: security headers
import helmet from "helmet";
app.use(helmet());
```

## Failure handling

- `npm audit` fails or is unavailable: note the gap; skip dependency audit and continue with manual security review.
- Tests fail: include output as a blocking finding — do not attempt to fix, report and stop.
- Security issue is ambiguous: err on the side of flagging it — mark as "potential" and explain the attack vector.
- LSP unavailable: fall back to reading files directly; note that cross-file call-chain checks were skipped.
- No input validation library detected: flag all external data usage as unvalidated and recommend adding runtime validation — do not assume validation happens elsewhere.
