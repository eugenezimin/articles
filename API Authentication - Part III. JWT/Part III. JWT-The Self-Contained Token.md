# Part III — JWT: The Self-Contained Token

## Why API Keys Aren't Always Enough

In Part II we saw that an API key is essentially a long, secret password your software shows to a server. It works, but it has a hidden cost: every time the key is used, the server must look it up in a database to find out what the key is allowed to do, whether it has expired, and whether it has been switched off. A **JSON Web Token (JWT)** removes that lookup by carrying all of that information _inside the token itself_. This article explains the problem JWT solves and shows where it sits in the larger story of web authentication.

Part I covered Basic Authentication — sending a username and password with every request. Part II covered API keys — replacing that reusable password with a single opaque secret string that identifies an application rather than a person.

Both approaches share a quiet assumption: **the server already knows things about the credential, and it has to go and remember them.**

Think of an API key as a numbered coat-check ticket. The ticket itself tells you nothing — it's just a number. To find out what the ticket entitles you to, the attendant has to walk into the back room, find the matching record, and read it. The ticket is meaningless without the back room.

That "back room" is a database, and consulting it is called a **database roundtrip** — the server pauses, sends a question to the database, and waits for an answer before it can continue.

### The hidden cost of a roundtrip

For most applications, one database lookup per request is perfectly fine. But consider what the server actually has to check each time an API key arrives:

- **Permissions** — what is this key allowed to do?
- **Expiry** — is this key still valid, or has it passed its end date?
- **Status** — has someone revoked or suspended this key?

All three answers live in the database, not in the key. So _every single request_ triggers a roundtrip before any real work happens.

![[API Keys and Database Roundtrips.png]]Figure 1. API Keys and Database Roundtrips

This becomes a problem at scale in two specific situations:

1. **High request volume.** A popular API might handle thousands of requests per second. Thousands of identity lookups per second is real, measurable load — and load that does nothing for the user except verify who they are.
    
2. **Distributed systems.** Modern applications are often split into many small, independent services (commonly called **microservices** — a single application built as a collection of small, separately running programs that talk to each other). If a request passes through five services, and each one independently re-checks the caller's identity against the database, that's five roundtrips for one user action. The database becomes a bottleneck that every service depends on.
  
![[API Key Validation Scaling Problem.png]]Figure 2. API Key Validation Scaling Problem

The deeper issue is **state**. A server that must consult a database to understand a credential is a **stateful** server — it cannot make a decision on its own. It always needs the back room.

### The core idea behind JWT

JWT flips the model. Instead of handing the server a meaningless ticket and forcing it to look up the details, JWT hands the server a ticket that _has the details printed on it_ — and stamped in a way that proves the printing wasn't forged.

![[JWT and Stateless Validation.png]]Figure 3. JWT and Stateless Validation

To stay with the analogy: a JWT is less like a coat-check number and more like a **boarding pass**. A boarding pass already states your name, your flight, your seat, and your boarding time, right there on the paper. The gate agent doesn't phone headquarters to look you up — they read the pass and check that it's genuine. The information travels _with_ the traveler.

This property has a precise name. A server that can validate a token using only the token itself (plus a verification key it already holds) is **stateless** — it holds no per-request memory and needs no back room. We will unpack exactly _how_ a JWT proves it hasn't been forged later, when we open up its three-part structure. For now, the one idea to carry forward is the trade:

> An API key keeps the metadata in the database and gives you a pointer to it. A JWT puts the metadata in the token and gives you a way to trust it.

![[API versus JWT comparison.png]]Figure 4. API Keys vs. JWT comparison

That trade is powerful, but — as Part III will explore honestly — it is not free. Information printed on a token cannot be un-printed, which creates a genuine difficulty when you need to cancel a token early.

## A Few Words of History

Every technology arrives at a particular moment for a particular reason. JWT is no exception — it appeared just as the web was shifting away from a model that had quietly dominated for over a decade.

### The world before: the session cookie

For most of the 2000s, web authentication worked through **server-side sessions**. When you logged in, the server created a record of your session in its own memory or database and handed your browser a small identifier — a **session cookie**. On every later request, your browser sent that cookie back, and the server looked it up to remember who you were.

This is the same coat-check pattern from the previous session above: the cookie is a meaningless number, and the server holds all the real information. It worked well when a website was a single server. But it tied every logged-in user to a specific machine's memory. Spread your traffic across many servers, and you hit a problem — a user logged in on **Server A** is a stranger to **Server B**, because **Server B** never created that session record.

### The pressure that created JWT

Two trends in the early 2010s made server-side sessions increasingly awkward.

First, applications stopped being single servers. They were spread across fleets of machines, and increasingly split into **microservices** — many small programs, each handling one job. A shared, central session store became a bottleneck that every service had to consult.

Second, the _clients_ changed. The web was no longer just browsers loading full pages. It was single-page applications (SPAs) — websites that load once and then behave like desktop apps — and native mobile apps, often talking to APIs hosted on entirely different domains. Cookies, which are tightly bound to a single domain by design, fit this new world poorly.

The industry needed a credential that any server could verify on its own, without a shared session store, and that wasn't anchored to one domain. The answer was to make the token _carry its own proof of identity_.

### RFC 7519: the standard

The work happened inside the **IETF** (the Internet Engineering Task Force, the body that standardizes the protocols underlying the internet) as part of its OAuth working group — the same group designing the next generation of authorization standards. They needed a compact, secure token format to pass identity information around, and JWT was built to fill that gap.

The result was published in **May 2015 as [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)** — the formal specification that defines what a JSON Web Token is. An **RFC** ("Request for Comments") is the document format the IETF uses for internet standards; despite the tentative-sounding name, a published RFC is the authoritative definition.

A point worth noting: JWT was never a lone invention. It is the centerpiece of a small family of related standards — collectively called **JOSE** (JavaScript Object Signing and Encryption) — that also define how to sign tokens (JWS), encrypt them (JWE), and represent cryptographic keys (JWK). 

For most practical purposes, though, "JWT" is the term everyone uses, and it's the one we'll use here.

### From standard to ubiquity

A specification only matters if people adopt it, and JWT's adoption was unusually fast. The identity company **[Auth0](https://auth0.com)**, founded in 2013, built much of its product and developer education around JWT and promoted the format heavily — including `jwt.io`, a free online debugger that let developers paste in a token and see its decoded contents instantly. For a great many engineers, that tool was their first hands-on encounter with the format.

From there, JWT spread through the ecosystem. It became the default token format for **[OpenID Connect](https://openid.net)** — the identity layer built on top of [OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749), and the subject we'll reach later in this series. Cloud platforms adopted it for service-to-service authentication. Web frameworks in nearly every programming language shipped libraries to create and verify it. Within a few years of RFC 7519, JWT had moved from a new proposal to a default assumption.

### Why the history matters

This background isn't trivia — it explains the _shape_ of the technology you're about to take apart. JWT looks the way it does because it was designed for a specific world: distributed systems with no shared memory, and clients scattered across domains and devices.

That origin also explains its central trade-off. JWT was built to let a server make a decision _on its own_, without calling back to a central store. That independence is exactly the feature that makes JWT fast and scalable — and, as we'll see, exactly the feature that makes a token hard to cancel once it's been issued. The strength and the weakness are the same design decision, viewed from two sides.

With that context in place, we can now open up an actual token and see what those three dot-separated parts really contain.

## The Anatomy of a JWT

This is the heart of subject. Once you can see what a JWT actually **_is_**, every later topic — claims, signatures, validation, security — becomes far easier to follow. So we'll take a real token apart, piece by piece.

### Three parts, two dots

A JWT, when written out, looks like a long, slightly intimidating string of gibberish:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsIm5hbWUiOiJBZGEifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

It looks random. It isn't. Look closely and you'll spot **two dots** dividing it into **three parts**:

```
header  .  payload  .  signature
```

That structure never changes. Every JWT, everywhere, is exactly three parts separated by dots:

1. The **header** — describes the token itself.
2. The **payload** — carries the actual information.
3. The **signature** — proves the first two parts haven't been tampered with.

The boarding-pass analogy from the first section holds up neatly here. The header is the small print at the top that says what kind of document this is. The payload is the part you actually care about — your name, your flight, your seat. The signature is the official stamp that proves the pass is genuine and not something printed at home.

### Why it looks like gibberish: Base64URL

The reason a JWT looks unreadable is not encryption. It is **encoding** — and the distinction matters.

- **Encryption** scrambles data so that _no one_ can read it without a secret key.
- **Encoding** simply rewrites data into a different alphabet so it can travel safely. Anyone can reverse it.

A JWT's header and payload are merely **encoded**, not encrypted. They use a scheme called **Base64URL** — a way of representing data using only letters, digits, and a couple of symbols that are safe to put inside a web address (a URL).

This leads to the single most important — and most misunderstood — fact about JWTs:

> **The contents of a JWT are not secret.** Anyone who holds the token can decode the header and payload and read everything inside. The signature stops people from _changing_ a token; it does nothing to _hide_ it.

![[JWT Decoding vs Hiding Secrets.png]]Figure 5. JWT Decoding vs. Hiding Secrets

We'll return to the security consequences of this later. For now, just hold onto it: a JWT protects against forgery, not against reading. Never put a password, a credit-card number, or any other secret inside it.

### Part 1: The header

Take the first segment of our example token and reverse the Base64URL encoding, and you get a small block of **JSON**— JavaScript Object Notation, the simple, human-readable `key: value` format used everywhere on the modern web:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

The header is metadata _about the token_. It answers two questions:

- **`alg`** ("algorithm") — how the signature was created. Here, `HS256`. We'll examine the algorithm choices in detail in part of the article; for now, treat it as a label naming the method used to make the stamp.
- **`typ`** ("type") — what kind of object this is. For a JWT, this is simply `"JWT"`.

The header is short, and it's mostly there so the receiving server knows _how_ to check the signature later.

### Part 2: The payload

Decode the second segment and you get another block of JSON — and this is the part that does the real work:

```json
{
  "sub": "12345",
  "name": "Ada"
}
```

The payload carries the **claims** — the individual statements the token is making. The word is well chosen: each entry is a _claim_, an assertion that "this is true." Here the token claims two things: the subject (`sub`) of this token is user `12345`, and that user's name is `Ada`. The payload is where identity, permissions, expiry times, and your own custom data live. 

### Part 3: The signature

The third segment is the only part that is genuinely cryptographic — and it's the part that makes a JWT trustworthy.

Here is the problem the signature solves. We just established that anyone holding a token can read the payload. But could they also _change_ it — swap `"sub": "12345"` for `"sub": "99999"` and impersonate another user? The answer is **"YES"**. Does it stay hidden? And the most important answer is here - **"NO"**, as the signature is what makes that attack fail because it becomes easily recognizable and server knows how to react on it.

![[JWT Forgery Protection - The Signature.png]]Figure 6. JWT Forgery Protection - The Signature

When the server first creates the token, it performs a calculation. It takes the encoded header and the encoded payload, joins them with a dot, and feeds that — together with a **secret key that only the server knows** — into a one-way mathematical function. For our `HS256` example, that function is **HMAC-SHA256**. The output is the signature:

```
signature = HMAC-SHA256(
    base64url(header) + "." + base64url(payload),
    secret
)
```

Two properties of this function are what make the whole scheme work:

1. **It depends on every input.** Change a single character of the header or payload, and the output is completely different.
2. **It can't be reversed or faked without the secret.** Knowing the inputs but not the secret, there is no practical way to compute the correct signature.

So when an attacker edits the payload to say `"sub": "99999"`, the signature attached to the token no longer matches the modified content. When the server recomputes the signature from the tampered payload and compares it to the one in the token, the two don't match — and the token is rejected. Because the attacker doesn't have the secret key, they can't produce a fresh, valid signature for their forged payload either.

![[JWT Signature- The Key to Integrity and Honesty.png]]Figure 7. JWT Signature- The Key to Integrity and Honesty

And this is the core idea worth carrying out of this section:

> The signature doesn't keep a JWT _private_. It keeps a JWT _honest_. It guarantees that the header and payload are exactly what the issuing server wrote, untouched since.

### Building one by hand

The best way to dispel the sense that this is magic is to build a token with no library at all — just the standard tools any programming language provides. Here it is in Python:

```python
import base64, json, hmac, hashlib

def base64url_encode(data: bytes) -> str:
    # Standard Base64, then made URL-safe: trailing '=' padding removed.
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def create_jwt(payload: dict, secret: str) -> str:
    # 1. The header: declare the algorithm and type.
    header = {"alg": "HS256", "typ": "JWT"}

    # 2. Encode the header and payload as Base64URL.
    h = base64url_encode(json.dumps(header).encode())
    p = base64url_encode(json.dumps(payload).encode())

    # 3. Sign "header.payload" with the secret using HMAC-SHA256.
    sig = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()

    # 4. Join all three parts with dots.
    return f"{h}.{p}.{base64url_encode(sig)}"


token = create_jwt({"sub": "12345", "name": "Ada"}, secret="my-secret-key")
print(token)
```

That is the _entire_ mechanism. There is nothing hidden. A JWT is two pieces of JSON, encoded for safe transport, plus a signature computed from them. The four numbered steps in the code are the whole story.

### The production path: use a library

Building a token by hand is the right way to _understand_ JWTs. It is the wrong way to _use_ them in real software.

In production, always reach for a well-maintained, audited library — `PyJWT` or `python-jose` in Python, and direct equivalents in every other major language. The same task becomes a single call:

```python
import jwt  # the PyJWT library

token = jwt.encode(
    {"sub": "12345", "name": "Ada"},
    "my-secret-key",
    algorithm="HS256"
)
```

This isn't laziness — it's safety. The hand-written version above is correct for _creating_ tokens, but _verifying_ them safely is full of subtle traps. A naive verifier can be tricked into accepting forged tokens, expired tokens, or tokens it should never have trusted. Mature libraries have already absorbed those lessons; your own code, written from scratch, has not.

So build one by hand once, to see that the magic is just arithmetic. Then never do it again in production.

With the structure of a token clear, we can turn to its most important part in detail — the payload, and the claims it carries.

## Claims: What a Token Actually Says

In previous section we opened up a JWT and found the payload — the middle segment carrying the token's real content. Each piece of information in that payload is called a **claim**. This section is about what those claims are, which ones the standard defines for you, and which ones you create yourself.

### A claim is just a statement

The terminology sounds formal, but the idea is plain. A **claim** is a single statement the token makes about its subject — one `key: value` pair in the payload's JSON. The token "claims" these things are true, and the signature is what makes that claim trustworthy.

A payload is simply a collection of these statements:

```json
{
  "iss": "auth.myapp.com",
  "sub": "12345",
  "aud": "api.myapp.com",
  "iat": 1716120000,
  "exp": 1716123600,
  "role": "editor",
  "tenant_id": "acme-corp"
}
```

Some of those keys — `iss`, `sub`, `aud`, `iat`, `exp` — are part of the JWT standard and mean the same thing everywhere. Others — `role`, `tenant_id` — are invented by the application. That split is the central idea of this section.

### Registered claims: the standard vocabulary

RFC 7519 defines a small set of **registered claims**. These are not required — a JWT is free to omit any of them — but if you _do_ use them, you must use them with the meaning the standard assigns. They have short, three-letter names to keep tokens compact.

There are seven worth knowing:

|Claim|Name|What it means|
|---|---|---|
|`iss`|Issuer|Who created and signed this token.|
|`sub`|Subject|Who or what the token is about — typically the user ID.|
|`aud`|Audience|Who the token is _intended for_ — which service should accept it.|
|`exp`|Expiration Time|The moment after which the token must be rejected.|
|`nbf`|Not Before|The moment before which the token is not yet valid.|
|`iat`|Issued At|The moment the token was created.|
|`jti`|JWT ID|A unique identifier for this specific token.|

A few of these deserve a closer look, because they do more than they first appear to.

**`iss` (Issuer)** identifies the authority that minted the token — usually an authentication server like `auth.myapp.com`. A receiving service checks this so it only trusts tokens from a source it recognizes, and ignores tokens minted by anyone else.

**`aud` (Audience)** is the one most often misunderstood, and it matters for security. It names the intended _recipient_. If your authentication server issues tokens for several different services, the `aud` claim lets each service confirm "this token was meant for _me_." A token minted for the billing service should be refused by the email service, even though both trust the same issuer. Skipping this check is a real vulnerability.

**`jti` (JWT ID)** is a unique serial number for one individual token. On its own it does little. Its importance shows up later: when you need to _cancel_ a specific token before it expires, the `jti` is the handle you use to do it. That's the revocation problem, and `jti` is the thread that connects to it.

### The temporal claims: `iat`, `nbf`, and `exp`

Three of the registered claims — `iat`, `nbf`, and `exp` — are about _time_, and together they give a token a lifespan. They are the mechanism behind one of JWT's most important properties: a token that automatically stops working.

Laid out on a timeline, they mark out a window of validity:

```
   iat            nbf              now                      exp
    │              │                │                        │
    ●──────────────●════════════════●════════════════════════●─────────►  time
  issued       valid from      this moment              expires after
                │◄───────── token is VALID here ───────────►│
```
Figure 8. Timeline for JWT claims

- **`iat` (Issued At)** is the token's birth timestamp — when it was created.
- **`nbf` (Not Before)** is the moment the token _starts_ being valid. Usually this is the same as `iat`, but it can be set in the future to issue a token now that only "switches on" later.
- **`exp` (Expiration Time)** is the moment the token _stops_ being valid. After this instant, every correct server must reject it, no matter what else the token says.

The `exp` claim is what gives a JWT its self-limiting nature. An API key, by contrast, tends to live until a human remembers to revoke it. A JWT carries its own deadline. Set `exp` to 15 minutes after `iat`, and the token simply expires 15 minutes later — no database, no cleanup job, no human action. This is central to managing the risk of a stolen token.

One technical detail: these timestamps are stored as **Unix time** — the number of seconds since midnight UTC on January 1, 1970. That's why `exp` appears as a large integer like `1716123600` rather than a human-readable date. It's a universal, timezone-free way to pin down an exact instant, and every JWT library converts it for you.

### Custom claims: your own data

The registered claims cover identity and timing. They say nothing about what a user is _allowed to do_, because that is specific to your application. For everything else, you add **custom claims** — `key: value` pairs you define yourself, with whatever names and meanings you choose.

Custom claims are where JWT delivers on the promise from the section above — moving metadata _into the token_ so the server doesn't need a database lookup. Typical examples:

- **`role`** or **`permissions`** — what the user is authorized to do (`"editor"`, `"admin"`, or a list like `["read:invoices", "write:invoices"]`). The receiving service reads this straight from the token and decides what to allow — no roundtrip required.
- **`tenant_id`** — in applications that serve many separate organizations from one system, this identifies which organization the user belongs to.
- **`email`**, **`name`** — basic profile fields, included to save a lookup when displaying the user's identity.

This is exactly the design that makes a server **stateless**: the answer to "who is this, and what may they do?" travels inside the request itself.

Two cautions, both flowing directly from facts already established.

First — and this bears repeating because it is the most common JWT mistake — **the payload is not secret.** Anyone holding the token can decode and read it. So custom claims may contain a user's role; they must never contain anything sensitive — no passwords, no API secrets, no private personal data.

Second, **keep the payload small.** A JWT travels with _every single request_ to your API. Every claim you add makes every request slightly larger. Stick to what the receiving service genuinely needs to make a decision; resist the temptation to pack a user's entire profile into the token.

### Avoiding name collisions

If your application invents a custom claim called `role`, and some other system your token passes through also uses `role` to mean something different, the two meanings collide. The JWT standard's recommended fix is to **namespace** custom claims — prefix them with a URL you control, so the name is globally unique:

```json
{
  "sub": "12345",
  "https://myapp.com/role": "editor"
}
```

The URL doesn't have to point anywhere real; it's used purely as a unique prefix. For a closed system where you control every service, plain names like `role` are common and perfectly workable. For tokens that travel between organizations, namespacing prevents a class of subtle, hard-to-diagnose bugs.

### The payload, in summary

A JWT's payload is a set of claims — statements the token asserts and the signature makes trustworthy. Some claims are **registered** by the standard: `iss`, `sub`, and `aud` answer _who_; `iat`, `nbf`, and `exp` answer _when_; `jti` gives the token a unique name. The rest are **custom claims** you define, and they are how identity and permissions ride along inside the request, sparing the server a database lookup.

We now know what a token _says_. The next question is _how_ it proves it — which means looking closely at the signature, and the different algorithms used to create it.

## Signature Algorithms: HS256, RS256, and ES256

 Above we established what the signature _does_: it makes a token honest, guaranteeing the header and payload haven't been altered since the issuer wrote them. We used `HS256` as the example and treated it as a black box. Now we open the box — because the choice of signing algorithm is one of the most consequential decisions you'll make when building a real system, and it turns entirely on a single question: **who is allowed to verify the token?**

### Two families: symmetric and asymmetric

Every JWT signing algorithm belongs to one of two families. The difference between them is the difference between a shared password and a wax seal.

![[JWT Signing - Symmetric vs. Asymmetric.png]]Figure 9. JWT Signing - Symmetric vs. Asymmetric

A **symmetric** algorithm uses **one secret key for both jobs** — creating the signature and checking it. The same key signs and verifies. It's like a password shared between two parties: whoever knows it can both lock and unlock.

An **asymmetric** algorithm uses **a pair of mathematically linked keys**: a **private key** and a **public key**. The private key creates signatures and is guarded closely. The public key only _verifies_ signatures and can be shared freely — handed to anyone, posted publicly — without weakening anything. It's like a wax seal: the issuer owns the unique stamp (the private key), but anyone with a picture of the seal (the public key) can recognize a genuine one. Holding the public key lets you _check_ a seal but never _forge_ one.

That single distinction — one shared key versus a public/private pair — drives everything that follows.

### HS256: the symmetric option

**HS256** stands for **HMAC using SHA-256**. It is the symmetric choice, and it's the algorithm in every example so far.

With HS256, one secret string both signs and verifies tokens. The server that issues a token uses the secret to compute the signature; the server that receives a token uses _the same secret_ to recompute the signature and compare. If they match, the token is genuine.

This is simple, fast, and produces compact signatures. But it carries one unavoidable consequence: **every party that needs to verify a token must hold the secret key.** And here is the catch — the verifying key and the signing key are the _same key_. Any service that can _check_ a token can therefore also _mint_ a brand-new token that everyone else will trust.

In a single, self-contained application, that's fine. The same server issues tokens and checks them. There's one secret, in one place, and no one else needs it.

The trouble begins when the system grows.

### RS256: the asymmetric option

**RS256** stands for **RSA Signature using SHA-256**. RSA is a long-established public-key cryptosystem; what matters here is that RS256 is **asymmetric** — it uses the private/public key pair.

With RS256, the authentication server holds a **private key** and uses it — and only it — to sign tokens. It then publishes the matching **public key** for the world to see. Any other service can take that public key and verify a token's signature. But the public key _cannot sign anything_. A service holding only the public key can confirm a token is genuine, yet has no power to forge one.

That asymmetry solves the exact problem HS256 created.

### The "aha": why this matters for microservices

Recall the microservices picture from Figure 1 — an application split into many small, independent services. Suppose one of them, the authentication service, issues tokens, and a dozen others need to verify them.

**With HS256**, every one of those dozen services must hold the shared secret. That's a real problem on two fronts:

- **A wider attack surface.** The secret now lives in twelve places instead of one. A breach of _any single service_leaks the key — and with it, the power to forge tokens that all twelve will trust.
- **Misplaced trust.** Every service that can _verify_ can also _issue_. A minor, low-privilege service now holds the keys to impersonate anyone. That violates a basic security principle: a component should hold only the power it actually needs.

**With RS256**, the picture changes completely:

- The **private key lives in exactly one place** — the authentication service. Only it can mint tokens.
- The **public key is distributed** to all twelve verifying services. It's not a secret; if one leaks, nothing is compromised, because a public key cannot forge anything.
- Verifying services can do their job — confirming a token is genuine — without ever holding the power to create one.

![[Token Validation in Microservices - Securing the Keys.png]]Figure 10. Token Validation in Microservices - Securing the Keys

This is the central insight of the section, and it's worth stating plainly:

> In a distributed system, use an **asymmetric** algorithm. It lets you separate the power to _issue_ tokens from the power to _verify_ them — concentrating the dangerous capability in one guarded place while distributing the harmless one freely.

### ES256: asymmetric, but leaner

**ES256** stands for **ECDSA using SHA-256**, where ECDSA is the Elliptic Curve Digital Signature Algorithm.

For decision-making purposes, ES256 belongs in the same category as RS256: it is **asymmetric**, with a private key for signing and a public key for verifying, and it solves the microservices problem in exactly the same way. The difference is mechanical. ES256 is built on **elliptic-curve cryptography**, a more modern branch of public-key cryptography that achieves the same security strength with much smaller keys and signatures.

The practical payoff is **size**. An RS256 signature is large; an ES256 signature, at comparable security, is substantially smaller. Since a JWT travels with every request, a smaller signature means a smaller token on every call. For a high-traffic API, that adds up.

The trade-off is maturity and ubiquity. RSA has been in use for decades and is supported absolutely everywhere; elliptic-curve support, while now excellent, is marginally less universal in older systems. In practice, both are solid choices — RS256 is the safe, conventional default, and ES256 is the leaner, more modern alternative.

### Putting it side by side

| |**HS256**|**RS256**|**ES256**|
|---|---|---|---|
|**Family**|Symmetric|Asymmetric|Asymmetric|
|**Key(s)**|One shared secret|RSA private/public pair|EC private/public pair|
|**Who can verify?**|Only holders of the secret|Anyone with the public key|Anyone with the public key|
|**Can a verifier also forge tokens?**|**Yes** — same key signs and verifies|No — public key can't sign|No — public key can't sign|
|**Signature size**|Small|Large|Small|
|**Best fit**|A single, self-contained service|Distributed systems / microservices|Distributed systems where token size matters|

The decision rule is short. If your application is a **single service** that both issues and verifies its own tokens, **HS256** is simple, fast, and entirely appropriate — there's no second party, so a shared secret shares nothing. The moment **more than one independent service must verify tokens**, switch to an asymmetric algorithm: **RS256** as the well-supported default, **ES256** when you want smaller tokens and your platform supports it. The question is never "which algorithm is best" in the abstract — it is "who, in my system, needs to verify a token, and should those same parties be able to create one?"

We now know how a token is signed. But verifying a token correctly involves much more than checking that one signature. The next section lays out the full validation checklist — and shows why skipping any step on it opens a door.

## Validation: The Full Checklist

Here is a mistake that has shipped to production in countless real systems: a developer wires up JWT authentication, confirms the signature checks out, and considers the job done. The signature is valid — so the token is trustworthy. Right?

Not quite. **A valid signature answers only one question: was this token altered since it was issued?** It says nothing about _when_ the token was issued, _who_ issued it, _who_ it was meant for, or whether it has been _cancelled_ in the meantime. A token can have a perfect signature and still be one your server must refuse.

Proper validation is therefore a **checklist**, run in order. This section walks through all six steps, mirroring the security rigor of the earlier parts of this series.

### Why the order matters

The steps are sequenced deliberately, and the first one comes first for a reason: **until the signature is fully verified, you cannot trust a single byte of the payload.**

Every later check — expiry, issuer, audience — reads a value _from the payload_. But if the signature hasn't been confirmed, the payload might be an attacker's forgery, and an attacker writes their `exp` claim to say whatever they like. Checking expiry on an unverified payload is theatre. So the signature is verified first; only once it passes does the payload become trustworthy enough to inspect.

### The six-step checklist

**Step 1 — Verify the signature.** Recompute the signature from the token's header and payload (using the secret for HS256, or the public key for RS256/ES256) and confirm it matches the signature attached to the token. If it doesn't, the token is forged or corrupted — reject it immediately and run no further checks. If it matches, the payload is now proven authentic, and the remaining steps can rely on it.

**Step 2 — Check `exp` (not expired).** Read the expiration timestamp and confirm the current time is before it. An expired token is rejected even though its signature is flawless. This is the check that makes a stolen token stop working on its own — and the entire reason short expiry times are worth setting.

**Step 3 — Check `nbf` (not used before valid).** If the token carries a "not before" claim, confirm the current time is past it. A token presented before its activation moment is not yet valid and must be refused. In practice this rarely fires, but a complete validator checks it.

**Step 4 — Check `iss` (expected issuer).** Confirm the `iss` claim names an authentication server you actually trust. A token can be perfectly signed by _some_ issuer, but if it isn't _your_ issuer, it's irrelevant — reject it. This stops your service from honouring tokens minted by an unrelated, untrusted source.

**Step 5 — Check `aud` (intended audience).** Confirm the `aud` claim names _your_ service. This is the check which is most often skipped — and skipping it is a genuine vulnerability. Without it, a token issued for the low-privilege analytics service would be accepted by the high-privilege billing service, simply because both trust the same issuer. The `aud` check is what keeps a token usable _only_ where it was meant to be used.

**Step 6 — Check `jti` against a revocation list (if needed).** For most stateless setups this step is deliberately omitted — checking a token against a list means consulting a database, which sacrifices the very statelessness JWT was chosen for. But when you genuinely need the ability to cancel an individual token before it expires, this is where it happens: look up the token's `jti` and reject it if it appears on a blocklist. This step is the bridge revocation problem, and the reason it's marked "if needed" is itself the subject of that section.

### What this looks like in code

Previously we said: build a token by hand once to understand it, then use a library in production. Validation is precisely where that advice earns its keep. A good library performs the entire checklist for you — _if_ you tell it what to expect:

```python
import jwt  # the PyJWT library

def validate_jwt(token: str, secret: str, expected_audience: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],          # Step 1: which algorithm(s) to trust
            audience=expected_audience,    # Step 5: the aud claim must match this
        )
        # Steps 2 and 3 — exp and nbf — are checked automatically by decode().
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")          # Step 2 failed
    except jwt.InvalidAudienceError:
        raise AuthError("Invalid audience")           # Step 5 failed
    except jwt.InvalidSignatureError:
        raise AuthError("Signature verification failed")  # Step 1 failed
    # ... and so on for the other failure cases
```

Three details in that small function carry the section's whole lesson.

First, **`jwt.decode()` does several checks at once.** A single call verifies the signature, the expiry, and the "not before" time. The library runs the checklist — but only the parts you've configured.

Second, **a check you don't ask for doesn't happen.** Notice `audience=expected_audience` is passed explicitly. Leave that argument out, and many libraries simply _skip the audience check entirely_ — Step 5 silently vanishes, and no error is ever raised. The token validates "successfully," and a real vulnerability sits quietly in your code. The same applies to the issuer. Safe validation means actively telling the library what to expect; its defaults are not your security policy.

Third — and this is the most important line in the whole snippet — **`algorithms=["HS256"]` is not optional.** It tells the library exactly which signing algorithm(s) to accept. Omitting it, or filling it in carelessly, opens the single most infamous JWT vulnerability of all. We've now mentioned it twice as a forward pointer; later we finally show the attack itself.

### The takeaway

A valid signature is the _first_ line of a six-line checklist, not the whole of it. Full validation confirms a token is **authentic**(signature), **current** (`exp`, `nbf`), **from a source you trust** (`iss`), **meant for you** (`aud`), and **not revoked** (`jti`, when required). A production-grade library will run every one of those checks — but only the ones you explicitly configure. The unsafe defaults are silent, and silence, in security, is exactly the danger.

That sixth step — revocation — has been flagged twice now as something deferred. It's deferred because it isn't a simple checklist item; it's a genuine tension at the heart of the whole JWT design. The next section confronts it directly.

## The Stateless Advantage — and the Revocation Problem

This is the most important section in the article, and the most honest. Everything so far has built toward a single payoff — and that same payoff comes bundled with a single, genuine flaw. A clear-eyed engineer needs both halves. This section gives you both.

### The win: a server that needs no memory

Return to the very first idea of this series. An API key is a meaningless ticket; to learn what it permits, the server must make a **database roundtrip** to the back room. A JWT prints the details on the ticket itself and stamps them so they can't be forged.

Now we can state precisely what that buys you. When a JWT arrives, the receiving server checks it using **only the token and a verification key the server already holds** — the shared secret for HS256, or the public key for RS256/ES256. The signature confirms the token is authentic; the claims inside answer _who the user is_ and _what they may do_. Nothing else is consulted.

That property is **statelessness**: the server keeps no per-user, per-session memory. It needs no shared session store, no identity database lookup on the request path. And the benefits compound:

- **Speed.** No network trip to a database before real work begins. Verification is local arithmetic.
- **Scale.** Add a hundred new servers and not one of them needs a connection to a session store. Each verifies tokens entirely on its own.
- **Resilience.** Recall the microservices picture from figure 2 — a dozen services each verifying tokens. With JWT, none of them shares a session-store bottleneck. If that store would have existed, it would have been a single point of failure every service depended on. JWT removes it.

This is the killer feature. It is the reason JWT became the default token of the distributed-systems era.

### The problem: you can't un-issue a token

Now the honest half.

The very thing that makes a JWT powerful — it is **self-contained**, valid purely on its own evidence — is the thing that makes it dangerous. A stateless server's logic is simply: _"the signature is good and the token hasn't expired, therefore I trust it."_ That logic has no step that asks anyone's permission. It never phones home.

So consider: a token is **stolen**. An attacker copies a user's valid, unexpired JWT — through a compromised device, an intercepted request, a leaked log file.

With an old-style server-side session, the fix is instant. You delete the session record from the server. The next request carrying that session is a stranger; access is gone forever.

With a JWT, there is **no record to delete.** The token's authority lives _inside the token_, in the attacker's possession. Every server that sees it performs the same local check, gets the same answer — _signature good, not expired_ — and grants access. The token keeps working, in the attacker's hands, **until its `exp` timestamp passes.** And nothing you do can hurry that moment along.

State this plainly, because it is the crux of the entire JWT trade-off:

> A JWT is **self-contained by design**, which means it is **non-revocable by design.** The server gave up its memory in exchange for speed — and a server with no memory has no way to remember that one particular token should now be refused.

This is not a bug to be patched. It is the direct, unavoidable shadow of the feature. Statelessness and instant revocation are two ends of the same stick: you cannot pick up one end without the other coming with it.

### Living with the trade-off

You can't eliminate the problem, but you can _manage_ it. Three patterns are used in practice, and they sit on a deliberate spectrum — from "fully stateless, accept some risk" to "give back some statelessness, regain control."

#### 1. Short expiry times

The simplest response: if a stolen token is valid until `exp`, then **make `exp` soon.**

Set tokens to expire in fifteen minutes rather than twenty-four hours. A stolen token is still unstoppable — but only for a short window. The damage is time-boxed. This keeps the server fully stateless; you simply accept a small, bounded exposure instead of trying to abolish it.

The objection is obvious, and it's a usability one: a token that expires every fifteen minutes would log the user out every fifteen minutes. Forcing someone to re-enter their password that often is unworkable. Which is exactly why short expiry never travels alone — it travels with the next pattern.

#### 2. The access token + refresh token pattern

This is the pattern most production systems actually implement, and it resolves the usability objection cleanly by splitting one token into **two tokens with two different jobs.**

- **The access token** is a JWT, short-lived (say, 15 minutes). It rides along with every API request and does the real authorization work. Being a JWT, it is verified statelessly — fast, local, no database. If stolen, it's dangerous for only 15 minutes.
- **The refresh token** is long-lived (days or weeks), but it is **not** used for ordinary API calls. Its _only_ power is to ask the authentication server for a fresh access token. It is sent rarely, to one endpoint only, and it is typically a stored, **revocable** credential — the auth server _does_ keep a record of it.

![[Access & Refresh Token Split Pattern.png]]Figure 11. Access & Refresh Token Split Pattern

The whole lifecycle is as follows:

```
1. User logs in.
   → Auth server issues:  a short-lived ACCESS token  +  a long-lived REFRESH token.

2. For each API request:
   → Client sends the ACCESS token.  Service verifies it statelessly. Fast.

3. After ~15 minutes:
   → The ACCESS token expires. The next API call is rejected.

4. Client quietly sends the REFRESH token to the auth server.
   → Auth server checks the refresh token is still valid (and not revoked),
     then issues a brand-new short-lived ACCESS token.

5. Loop back to step 2. The user notices nothing.
```

The elegance is in the division of labour. The token used _constantly_ (the access token) is stateless and fast, exactly where speed matters — but barely dangerous, because it expires almost immediately. The token that is _long-lived and genuinely dangerous_ (the refresh token) is used _rarely_, hits only one endpoint, and **can be revoked at that one chokepoint.** To cut off a compromised user, you invalidate their refresh token: within fifteen minutes their access token expires, the refresh fails, and they're locked out.

You haven't achieved truly instant revocation — there's still that ≤15-minute tail — but you've shrunk the unstoppable window to something tolerable while keeping the request path stateless. For most systems, that is the right balance.

#### 3. A revocation blocklist

When even a fifteen-minute window is unacceptable — banking, healthcare, anything where a compromised session must die _now_ — you need true immediate revocation. And here you must pay the honest price.

The pattern: recall the **`jti`** claim, the token's unique serial number. To revoke a token immediately, add its `jti` to a **blocklist** — a list of "tokens that must now be refused" — and have every service check incoming tokens against it. To keep that check fast, the list lives in a high-speed in-memory store such as **Redis**, not a slow disk database.

Be clear-eyed about what this costs. Checking a blocklist means **consulting a shared store on every request** — which is precisely the database roundtrip that JWT was chosen to eliminate. You have, deliberately, **given back the stateless advantage.**

But the surrender is partial, and that nuance matters:

- A blocklist holds only _revoked_ tokens — a tiny set — not _every_ session. The store stays small.
- An in-memory store like Redis is far faster than the relational-database lookup the original API-key model implied.
- Entries can be evicted the moment a token's natural `exp` passes — a revoked token already rejected by the expiry check needs no blocklist entry. The list stays small on its own.

So this isn't a wholesale return to stateful sessions. It's a precise, conscious concession: trade a little speed, on a small fast lookup, to buy back the immediate-revocation capability — but only when the application's risk profile genuinely demands it.

### The honest summary

JWT's defining feature and JWT's defining flaw are **the same fact**, seen from two sides. A self-contained token lets a server decide _on its own_ — fast, scalable, memoryless. A self-contained token also cannot be _un-decided_ — once issued, it is authoritative until it expires.

There is no pattern that makes that flaw vanish. There are only positions on a spectrum:

|Approach|Statelessness|Revocation speed|Typical use|
|---|---|---|---|
|Short expiry only|Fully stateless|None — wait for `exp`|Low-risk, simple systems|
|Access + refresh tokens|Stateless request path|Bounded — within the access token's lifetime|The mainstream default|
|`jti` blocklist|Partly stateful again|Immediate|High-stakes systems only|

The engineering question is never "how do I make JWT revocable?" — it can't be made so without giving something up. The question is: **how much immediate-revocation power does this system genuinely need, and how much statelessness am I willing to trade for it?** Answer that honestly, pick your point on the spectrum, and you are using JWT well.

We've now covered what a JWT is, what it carries, how it's signed, how it's validated, and its central trade-off. One thing remains: the specific ways JWT implementations get attacked — including the single most infamous JWT vulnerability of all.

## Security Considerations

A JWT is a security mechanism, which makes its own failure modes worth studying with care. Most JWT disasters are not failures of the cryptography — the math is sound. They are failures of _implementation_: a check skipped, a default trusted, a token stored carelessly. This section covers the four that matter most, beginning with the most famous of them all.

### The algorithm confusion attack: `alg: none`

We have pointed at this vulnerability twice and promised to show it here. It is the most infamous JWT bug ever, and what makes it memorable is that it turns the token's own honesty mechanism _against itself_.

Recall the structure of the token. The **header** declares which algorithm was used to sign the token, in its `alg` field — `"alg": "HS256"`. The **signature** is the stamp that proves the token wasn't altered.

Now recall a detail almost no one expects: the JWT standard defines a _legitimate_ algorithm value called **`none`**. It means "this token is unsigned." It exists for narrow cases where a token's integrity is already guaranteed by some other layer. It also creates a trapdoor.

Here is the attack, step by step:

```
1. The attacker takes a real, valid token and decodes it
   (remember - the payload is NOT secret, anyone can read it).

2. The attacker EDITS the payload freely:
        "sub": "regular-user"   →   "sub": "admin"

3. The attacker changes the header:
        "alg": "HS256"          →   "alg": "none"

4. The attacker DELETES the signature entirely,
   leaving a token that ends in a final dot and nothing after it:
        header.payload.

5. The token is sent to the server.
```

Now everything depends on one line of the server's code. A **naively written verifier** reads the header, sees `"alg": "none"`, and reasons: _"The header says this token is unsigned, so there is no signature to check. No signature to check means nothing fails. Token accepted."_

![[JWT alg Attack.png]]Figure 12. JWT Attack with "alg" set to "none"

The forged token sails through. The attacker is now `admin`. They never needed the secret key, never broke any cryptography — they simply **let the token tell the server how to verify it**, and the token, under attacker control, said "don't bother."

That is the heart of the trap: a naive verifier trusts the _token's own header_ to decide how the token should be checked. But the header is attacker-controlled. You have let the thing being inspected dictate the terms of its own inspection. (If this sounds like the embedded-public-key problem discussed earlier — a token vouching for its own trust — it is exactly the same mistake, in a different costume.)

**The fix is one line, and you have already seen it:*

```python
jwt.decode(token, secret, algorithms=["HS256"])
```

That `algorithms=["HS256"]` argument is the entire defense. It instructs the library: _"I will accept HS256 and nothing else. I don't care what the token's header claims."_ A token arriving with `alg: none` is now rejected before any verification logic runs, because `none` is not on the list the _server_ chose.

The principle, stated generally:

> **Never let the token decide how it should be verified.** The set of acceptable algorithms is a decision the server makes in advance and enforces — not a value it reads out of the untrusted header.

Modern, well-maintained libraries now refuse `alg: none` by default and require you to specify allowed algorithms — which is exactly why we insisted on using a real library rather than hand-rolling verification. But the lesson outlives this one bug: a verifier must hold its own policy, never inherit it from the token.

### A second face of algorithm confusion: HS256 vs RS256

There is a subtler cousin of the same attack.

Recall the asymmetric model: with RS256, the server signs with a **private key** and publishes the **public key** for anyone to verify with. The public key is, by design, _not secret_.

Now picture a server configured for RS256 but with a careless verifier that accepts whatever algorithm the header names. An attacker takes the **public key** — which is freely available — and uses it as if it were an **HS256 shared secret**. They forge a token, set the header to `"alg": "HS256"`, and sign it using the public key as the HMAC secret.

![[RS256:HS256 Key Confusion Attack Path.png]]Figure 13. RS256/HS256 Key Confusion Attack Path

When the token arrives, the confused server sees `alg: HS256`, fetches its RS256 public key as the "secret," runs the HS256 check — and it passes. The attacker has forged a valid token using only public information.

The fix is the same fix: pin the accepted algorithm. A server expecting RS256 must specify `algorithms=["RS256"]` and refuse everything else, so a token claiming `HS256` is rejected outright. Once again — the server decides, not the token.

### Secret strength for HS256

This one is simple and easily neglected. With HS256, the security of every token rests entirely on one shared secret. The signature is only as strong as that secret is hard to guess.

A secret like `"secret"`, `"password123"`, or your application's name is not a secret — it is an invitation. An attacker who suspects HS256 can run an **offline brute-force attack**: take any real token they've captured, and rapidly try millions of candidate secrets, checking each by recomputing the signature. A weak secret falls in seconds. Once it's found, the attacker can mint unlimited valid tokens for anyone.

The defense is unglamorous but absolute:

- Use a **long, high-entropy, randomly generated** secret — at least 256 bits (32 random bytes), produced by a cryptographic random generator, never typed by a human.
- Store it as a **secret** — in a secrets manager or environment configuration, never hard-coded in source, never committed to version control.
- This concern is HS256-specific. With RS256/ES256 there is no shared secret to guess; the private key is a different kind of object, guarded differently.

### Token storage in the browser

When a JWT is used to authenticate a user in a web browser, a practical question arises: _where does the browser keep the token between requests?_ This debate is mostly relevant to browser-based apps rather than the pure API-to-API use that is this series' main focus, so we'll keep it brief — but it's worth knowing the shape of it.

There are two common choices, each with a different weakness:

- **`localStorage`** is a simple in-browser storage area. It's easy to use, but any JavaScript running on the page can read it. If an attacker manages to inject a malicious script into your site — a **cross-site scripting (XSS)** attack — that script can read the token straight out of `localStorage` and steal it.
    
- **An `httpOnly` cookie** is a cookie the browser marks as off-limits to JavaScript. Even a successful XSS attack cannot read it directly, which closes the theft route above. The trade-off: cookies are sent by the browser automatically, which can expose the app to a different attack class — **cross-site request forgery (CSRF)** — that needs its own separate defenses.
    

There is no universally "correct" answer; each option trades one risk for another. The genuinely important point sits underneath both:

> A JWT is a **bearer token** — like cash, whoever holds it can spend it. The token itself contains no proof that the _right_ person is presenting it. So the security of any browser-based JWT system depends heavily on simply _not letting the token get stolen_ — and that depends on the surrounding application being free of injection flaws.

### Short expiry as a discipline

The final consideration is not a new attack but a habit that blunts all of them — and we've already met it.

Every threat in this section ends the same way: an attacker obtains a token they shouldn't have. And we already know JWT's hard truth — a stolen token cannot be recalled; it is valid until its `exp`.

This makes the expiry time itself a security control. A long-lived token turns any single theft into a long-lived breach. A short-lived one — minutes, not days — means a stolen token is a _briefly_ useful prize, paired with the refresh-token pattern so users never feel the churn.

Short expiry doesn't _prevent_ theft. It **caps the cost** of theft. It is the safety net beneath every other mistake, and it should be treated as non-negotiable discipline rather than a tuning knob.

### The thread connecting all four

Step back and the four considerations rhyme. The algorithm confusion attack is _trusting the token to define its own verification_. Weak HS256 secrets are _trusting an easily guessed value to be hard_. Careless token storage is _trusting a hostile environment to keep a bearer token safe_. And the antidote running through all of them is the same instinct: **trust must be anchored in decisions the server makes and controls — never in something the token, the attacker, or the environment supplies.** The cryptography in JWT is rarely what fails. The trust assumptions around it are.

With the failure modes mapped, only the practical verdict remains: when JWT is the right tool for the job — and when it isn't.

## When to Use JWT — and When Not To

We've taken JWT apart completely: its structure, its claims, its signatures, its validation, its central trade-off, and its failure modes. Knowing how a tool works is not the same as knowing when to reach for it. This section is the practical verdict — a decision guide for an engineer building a real system.

The honest framing is this: JWT is not a _better_ credential than the API key from Part II. It is a _different_ credential, built for a different job. Picking the right one means matching the tool to the situation.

### When JWT is the right choice

JWT earns its place whenever its defining feature — a **self-contained, statelessly verifiable token** — solves a problem you actually have.

**Stateless microservices — the killer use case.** This is the scenario JWT was built for, and the one where it has no real rival. When an application is split into many small services, and a request may pass through several of them, a JWT lets _each_ service verify the caller independently — with only a public key, no shared session store, no database roundtrip. The token carries identity and permissions with it. If there is one situation where JWT is unambiguously the answer, this is it.

**Cross-domain authentication — SPAs and mobile apps.** Recall that JWT emerged partly because session cookies are bound to a single domain and fit modern clients poorly. A JWT is just a string. It travels comfortably from a single-page app or a native mobile application to an API hosted on an entirely different domain, with none of the domain-binding friction cookies impose. When your client and your API don't share an origin, JWT removes a real obstacle.

**Short-lived service-to-service tokens.** When one internal service needs to call another and prove "this request is genuinely from me," a short-lived JWT is an excellent fit. Its built-in expiry means these machine-to-machine tokens clean up after themselves — no long-lived credential left lying around, no revocation process to run. They are minted, used, and expire, all within minutes.

**As a session-scoped layer on top of a long-term API key.** This is the subtlest fit, and it shows JWT and the API key working _together_ rather than competing. An API key (Part II) is excellent for stable, long-term _identity_ — "this is the Acme Corp account." A JWT is excellent for short-lived, fine-grained _authorization_ — "this particular request, in this 15-minute window, may write to invoices." A common production pattern: a client authenticates _once_ with its long-lived API key, and in exchange receives a series of short-lived JWTs that carry the actual per-request permissions. The API key answers _who you are over time_; the JWT answers _what you may do right now_.

### When to reach for something else

JWT's weaknesses are not hidden and we stated them plainly. Two situations expose them directly, and in both, a different tool is the honest choice.

**When you need immediate, reliable revocation.** This is JWT's defining flaw, and it is worth refusing to paper over. A standard JWT _cannot be un-issued_ — it is valid until `exp`, full stop. If your system has a hard requirement that a compromised credential must die _the instant_ you say so — with no fifteen-minute tail, no acceptable window — then a self-contained token is fighting your requirement.

The alternative here is an **opaque token** checked by **introspection**: the token is a meaningless reference string (like the API key of Part II — a coat-check ticket), and the receiving service asks a central authority, on every request, "is this token still valid?" That _is_ a database roundtrip. You are deliberately giving up statelessness — but in exchange you get exactly the instant, authoritative revocation that statelessness cost you. For high-stakes systems, that is the right trade.

**When the token is genuinely long-lived.** If a credential is meant to last for months — a stable identifier for a server, a long-running integration — then JWT's machinery is working against you. Its central feature, the self-contained expiring claim set, brings no benefit when nothing is meant to expire soon, and its central flaw, non-revocability, becomes a serious liability over a long lifespan. For durable, long-term identity, a plain **API key** is simpler, and — because it's checked against a database anyway — it can be revoked the moment you need to. Don't reach for a JWT's complexity to do an API key's job.

### The decision in one table

|Your situation|Reach for|Why|
|---|---|---|
|Many services must verify a caller independently|**JWT**|Stateless verification, no shared session store|
|Client and API live on different domains|**JWT**|A plain string travels anywhere; no cookie domain-binding|
|Short-lived, self-expiring service-to-service calls|**JWT**|Built-in expiry; no revocation process needed|
|Stable, long-term identity for an account or server|**API key** (Part II)|Simpler; revocable; nothing needs to expire soon|
|A compromised credential must be killable _instantly_|**Opaque token + introspection**|True immediate revocation, at the cost of statelessness|

### The underlying judgment

Reduce all of the above to a single question and it becomes easy to remember:

> **Does this system need a server to decide _on its own_, fast and at scale — or does it need a central authority to stay _in control_, able to revoke instantly?**

JWT is the tool for the first. It trades central control for local, stateless speed — a brilliant trade when speed and scale are what you need, a poor one when control is. Opaque tokens and API keys are the tools for the second.

There is no "best" credential, only a credential that fits. An engineer who can name _why_ they chose JWT — and name what they gave up to get it — is using it well. One who reaches for it by default, because it is the modern-sounding option, has skipped the only question that matters.

That leaves one piece of this series unfinished. JWT answers, beautifully, the question _who are you?_ It does not answer a different and harder one: _how do you let a third party act on your behalf — without ever handing them your password?_ That is the problem the final part was built to solve.

## Conclusion: Three Tools, Three Jobs

We began this article with a coat-check ticket and we end it with a boarding pass. That shift — from a meaningless token the server must look up, to a self-describing token the server can read and trust on sight — is the whole of what JWT contributes. It's worth gathering the journey into a single picture before we close.

### What JWT actually gave us

Strip away the Base64URL, the claims tables, the algorithm names, and one idea remains: **a JWT moves metadata out of the database and into the token itself, stamped so it cannot be forged.**

That single move is the source of everything else in this article. It is why a server can be **stateless** — verifying a request with only a key it already holds, no roundtrip, no shared session store. It is why JWT scales so gracefully across microservices and travels so freely across domains. And it is — unavoidably — why a JWT cannot be un-issued: a server that gave up its memory for speed has no memory in which to record that one token should now be refused.

The strength and the flaw are the same fact seen from two sides. An engineer who holds both halves in mind at once understands JWT. One who remembers only the strength will, sooner or later, be surprised by the flaw.

### Three methods, side by side

This series has now equipped us with three distinct credentials. They are not a ranking — not worse, better, best. They are three tools for three different jobs:

| |**Basic Auth** (Part I)|**API Key** (Part II)|**JWT** (Part III)|
|---|---|---|---|
|**What it is**|Username + password sent on every request|A single opaque secret string|A signed, self-describing token|
|**Carries its own data?**|No|No — it's just a reference|**Yes** — identity, permissions, expiry, all inside|
|**Server needs a lookup?**|Yes, every request|Yes, every request|**No** — verified statelessly with a key|
|**Built-in expiry?**|No|No|**Yes** — the `exp` claim|
|**Revocable immediately?**|Yes (change the password)|Yes (delete the key)|**No** — valid until it expires|
|**Best at**|Simple, internal, low-stakes access|Stable, long-term identity|Stateless, distributed, short-lived authorization|

Read the table top to bottom and the trade-off snaps into focus. Basic Auth and the API key keep their information in the database — which makes them slower per request, but instantly revocable. JWT carries its information in the token — which makes it fast and stateless, but stubbornly non-revocable. **You cannot have both.** Every authentication design is, at heart, a choice about where the trust lives: in a central store the server must consult, or in the token the server can read on its own.

Choosing well means naming that trade-off out loud — not reaching for the most modern-sounding option by reflex, but asking what _this_ system actually needs, and what it can afford to give up.

### The one question that remains

And yet, for all three of these methods, notice what they have in common. Basic Auth, the API key, and the JWT all answer the same single question:

> **"Who are you?"**

They are mechanisms of _authentication_ — proving identity. Each one assumes the party presenting the credential is the party it belongs to, acting on its own behalf.

![[Authentication- Proving Identity vs. Delegation- Safely Granting Third-Party Access.png]]Figure 14. Authentication vs. Authorization

But a great deal of the modern web does not work that way. When you let a photo-printing service reach into your cloud storage, or allow an analytics dashboard to read your calendar, something more delicate is happening. You are granting _a third party_ access to _your_ resources — and you would never dream of handing them your password to do it.

None of the three tools in this series solves that. A JWT can prove _who you are_ beautifully; it has nothing to say about how you safely _delegate_ a sliver of your access to someone else.

That problem — **how to grant a third party limited access to your resources without ever sharing your credentials** — is precisely the problem the next and final part of this series was built around. It is the problem of _authorization_ and _delegation_, and the answer is the framework that quietly underpins nearly every "Sign in with…" button and connected app on the internet: **OAuth 2.0**.

We have spent three articles learning, in ever-greater depth, how to answer _who are you?_ It is time to ask the harder question.