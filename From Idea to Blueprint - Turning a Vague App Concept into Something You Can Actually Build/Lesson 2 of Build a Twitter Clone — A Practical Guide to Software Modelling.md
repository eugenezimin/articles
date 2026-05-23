# The Blueprint Beneath the Blueprint: Designing `Bird`'s Data Model and Choosing Its Database

# Lesson 2 of _Build a Twitter Clone_ - A Practical Guide to Software Modelling

A diagram shows you _what_ a system does; a data model tells you _what it remembers_. Before drawing a single flowchart, you need to know what information `Bird` must store - and how that information is shaped. In this lesson we read our three use cases for data clues, name the entities the system must track, define their fields and relationships, and translate all of it into a real MySQL schema split across two purposefully separated databases. 

## Introduction - Data Before Diagrams

Lesson 1 closed with a promise: in Lesson 2, we draw the diagrams. Flowchart, functional diagram, sequence diagram - the works. At the moment we're going to defer it for a while. The reason is quite simple - because of something that becomes obvious the moment you try to draw the flowchart for _"Post a message"_ without it: **a diagram that doesn't know what data it's moving is vague in exactly the wrong places.**

You need to consider the following - the flowchart for posting a message will eventually have a step called something like _"save the message."_ Straightforward enough on paper. But the moment you try to build it, questions pile up fast:
- Save _what_, exactly? The text? The author? A timestamp? All three?
- Where does the author's identity come from - a name typed into a field, or a reference to a stored account?
- What does "the author" even mean to the system - a row in a table somewhere, or just a string?
- If the same author posts twice, how does the system know both messages belong to the same person?

![[message confusion.jpg]]Figure 1. What is the Message?

A diagram that leaves those questions open isn't a blueprint. It's a sketch - useful for thinking, but not yet useful for building. The answers live in the **data model**: the formal description of what the system stores, and how the pieces of stored information relate to one another.

> Think of the data model as the system's long-term memory. The diagrams describe what the system _does_- its behaviour, its structure, its conversations. The data model describes what it _remembers_ between those moments of action. Without memory, each request starts from nothing. With it, a message posted today is still there tomorrow, and the author who posted it can be found.

Getting the data model right before drawing the diagrams isn't pedantry. It's the thing that turns vague boxes into precise components. When you know that a `message` is a row with an `id`, a `content` field capped at 280 characters, and an `author_id` that points to a specific user - then the "save message" step in your flowchart stops being a placeholder and starts being an instruction. The functional block that does the saving has a clear contract. The sequence diagram can name what passes between components.

## One System, Two Databases - and Why That's the Right Call

Before we write a single table definition, there's a structural question to answer: should all of `Bird`'s data live in one database, or more than one?

The instinct is usually to start with one. It's simpler, it requires less setup, and for a small project it feels like the obvious default. We're going to make a different call - and the reasoning behind it is worth understanding clearly, because the same question will come up in every non-trivial system you ever build.

### The problem with putting everything in one place

Start with the simpler option: one database called `bird`, with all tables inside it - users, messages, sessions, roles, everything. Will it work?

The answer is clear - it would work. In fact, it's how most beginner projects start, and there's nothing wrong with it as a starting point. But consider what happens as the system grows:
- A security audit requires changes to how passwords are stored. To make that change safely, you need to understand every table that touches user data - except now it's tangled up with message tables, timeline queries, and subscription records. The scope of "change one thing" has quietly expanded.
- Message volume spikes. You want to move the `messages` table to faster storage, or archive old records. But the table is in the same database as your user credentials, which have entirely different performance and retention requirements. You can't move one without the other.
- A colleague is working on authentication while you're working on the timeline feature. Both of you are making schema changes in the same database, to tables that are conceptually unrelated. You're in each other's way.

![[all-in-one database.jpg]]Figure 2. All in one Database - Will it Work?

The deeper problem is this: a single database couples concerns that have no real reason to be coupled. They are in the same place not because they belong together, but because it was convenient to put them there. Convenience now, complexity later.

### The principle: each domain owns its data

The solution is to give each distinct area of the problem its own data store - its own database that it, and only it, is responsible for. Nothing else writes directly to that data; anything that needs information from another domain has to go through the interface that domain exposes.

This is a well-established pattern in software design called **[Database per Service](https://dev.to/eugene-zimin/database-per-service-as-a-design-pattern-44gi)**: each logical service or domain owns its storage, and the boundary between services is enforced at the data layer, not just at the code layer. The pattern makes the separation real and durable - you can't accidentally reach across a boundary you'd have to explicitly cross.

![[Database per Service Design Pattern.jpg]]Figure 3. Database per Service Design Pattern

For `Bird`, two domains emerge clearly once you ask the question:

- **Identity and access** - who people are, how they prove it, what permissions they hold, which sessions are currently active. This is security-critical data, relatively stable, and completely self-contained. It has nothing to do with messages.
- **Content and social graph** - the messages people post, and the follow relationships between them. This data is high-volume and fast-moving, with entirely different performance and retention characteristics.

These two concerns have different owners, different change rates, and different security requirements. They will be given separate databases: `ums` (User Management System) for identity and access, and `twitter` for content and social graph.

|Database|Domain|What it owns|
|---|---|---|
|`ums`|Identity & access|Who people are, how they authenticate, what permissions they hold, which sessions are active|
|`twitter`|Content & social graph|The messages people post, and who follows whom|

Separating them means each can be optimized, scaled, or secured independently - a schema change in one won't touch the other.

### The idea behind the split: bounded contexts

The deeper principle at work here comes from **Domain-Driven Design** (DDD) - a way of thinking about how to organize software around the real-world problems it solves, rather than around technical convenience.

DDD would describe `ums` and `twitter` as separate **bounded contexts**: distinct areas of the problem, each with its own vocabulary, rules, and data. The word _user_ in the identity context means something specific - an account with credentials, roles, and a session history. The word _author_ in the messaging context means something different - a source of content, identified by an ID, whose full identity details live elsewhere. These concepts correspond to the same human being, but they are different models of that person, serving different purposes. Keeping them in separate databases makes that distinction visible and enforces it.

![[DDD BOUNDED CONTEXTS.jpg]]Figure 4. How DDD Helps and Works

> **An analogy.** Think of a hospital. The billing department and the medical records department both deal with the same patients - but they maintain completely separate files. The billing system doesn't need to know a patient's diagnosis; the medical records system doesn't need to know their payment history. Each department owns its data. Information is shared only when explicitly requested, through defined channels. The separation isn't bureaucracy - it's what keeps sensitive data appropriately contained, and what lets each department evolve independently.

If you want to go deeper on Domain-Driven Design, [this article](https://dev.to/eugene-zimin/leveraging-domain-driven-design-for-application-design-58e2) covers the core ideas without requiring a computer science background.

## Reading the Use Cases for Data Clues

A use case describes what a user accomplishes. But read carefully, and it also tells you what the system must _remember_ in order to make that possible. Each of `Bird`'s three use cases leaves a trail of data requirements - we just have to follow it.

### Post a message
A user writes some text and publishes it. For this to work, the system must store the text itself, know _who_ posted it, and record _when_ it was posted so the timeline can be ordered. That's three pieces of information: content, author, timestamp.

| Scope      | Field        | Type                   | Why it's needed                                                         |
| ---------- | ------------ | ---------------------- | ----------------------------------------------------------------------- |
| `messages` | `id`         | UUID                   | A stable, unique identifier for this message                            |
| `messages` | `author_id`  | UUID                   | The `id` of the user who posted this message - links back to `users.id` |
| `messages` | `content`    | String (max 280 chars) | The text of the message, capped at 280 characters                       |
| `messages` | `created_at` | Timestamp              | When the message was posted - used to order the timeline                |

### View the timeline

This use case produces no new fields. It reads existing `messages` rows, ordered by `created_at` descending, and joins to `users` on `author_id` to display the author's name. Every field it depends on was already required by _Post a message_. Here we have to introduce what it is called - *subscriptions* and set a relation between author and and consumer of the message, i.e. - subscriber.

| Scope           | Field           | Type      | Why it's needed                                         |
| --------------- | --------------- | --------- | ------------------------------------------------------- |
| `subscriptions` | `subscriber_id` | UUID      | The user doing the following - logical FK to `users.id` |
| `subscriptions` | `producer_id`   | UUID      | The user being followed - logical FK to `users.id`      |
| `subscriptions` | `created_at`    | Timestamp | When the follow relationship was created                |

### Register an account
A user creates an identity. The system must store a name to display, credentials to authenticate with (stored as a hashed password, never plain text), and again a timestamp. It also needs a way to distinguish one account from every other - a unique identifier that never changes even if the username does.

| Scope   | Field           | Type      | Why it's needed                                                                       |
| ------- | --------------- | --------- | ------------------------------------------------------------------------------------- |
| `users` | `id`            | UUID      | A stable, unique identifier for this user - never changes, even if name or email does |
| `users` | `name`          | String    | The display name shown alongside every post                                           |
| `users` | `email`         | String    | Login credential; unique across all users - no two accounts can share an address      |
| `users` | `password_hash` | String    | The user's password after a one-way hashing function - never the plain-text password  |
| `users` | `created_at`    | Timestamp | When the account was registered                                                       |
| `users` | `updated_at`    | Timestamp | When any field on this record last changed; refreshed automatically on every write    |

| Scope   | Field         | Type   | Why it's needed                                               |
| ------- | ------------- | ------ | ------------------------------------------------------------- |
| `roles` | `id`          | UUID   | Unique identifier for this role                               |
| `roles` | `name`        | String | The role label (e.g. `admin`, `member`) - must be unique      |
| `roles` | `description` | String | Optional human-readable explanation of what this role permits |

| Scope      | Field           | Type      | Why it's needed                                               |
| ---------- | --------------- | --------- | ------------------------------------------------------------- |
| `sessions` | `id`            | UUID      | Unique identifier for this login session                      |
| `sessions` | `user_id`       | UUID      | References `users.id` - whose session this is                 |
| `sessions` | `logged_in_at`  | Timestamp | When the session started                                      |
| `sessions` | `logged_out_at` | Timestamp | When the session ended; `NULL` if the user is still logged in |

Across all three use cases, two distinct categories of information emerge: things the system needs to know about _people_, and things it needs to know about _messages_. That observation is the foundation of the data model.

## Naming the Entities

An **entity** is a category of information the system tracks as a distinct thing - something that has its own identity, its own set of properties, and its own lifetime. Naming entities is the first act of data modelling: you're deciding what the system considers a _noun_.

From the use cases, two entities name themselves:

**`User`** - a registered account. Every message is posted by a user; the timeline attributes each post to one. Users exist independently of any message they've posted, and they persist even if all their messages were deleted. They are a distinct thing in their own right.

**`Message`** - a piece of content posted by a user. Messages depend on users (a message with no author makes no sense), but they are not _part of_ a user - they are their own thing, with their own timestamp and their own text.

Two entities. That matches the two databases we decided to create: `ums` owns `User`, and `twitter` owns `Message`. The database boundary and the entity boundary are the same line drawn twice.

> You'll notice there's no `Timeline` entity, no `Feed` entity, no `Notification`. The timeline is not a thing the system stores - it's a _query_ - give me all messages, ordered by `created_at`, descending. It exists at runtime, not at rest. This is a useful distinction to internalise: not everything the user _sees_ needs to be _stored_.

In the next section we'll define the fields each entity carries - and introduce the mechanism that connects a `Message`back to the `User` who wrote it.

## Defining the Fields

An entity is just a name until you give it fields - the individual pieces of data it holds. This is where the model gets concrete. For each field, we'll state what it is, what type of value it holds, and _why it exists_, tracing every decision back to a use case or a design constraint.

### A note on identifiers

Every entity needs a **primary key** - a field whose sole job is to uniquely identify one row among all others, forever. A common choice is an auto-incrementing integer (1, 2, 3...), but `Bird` uses something different: a **UUID** (Universally Unique Identifier), stored as 16 bytes (or 128 bits) of binary data.

A UUID looks like `550e8400-e29b-41d4-a716-446655440000` - a 128-bit value generated in a way that makes collisions statistically impossible, even across separate systems. The binary storage (`BINARY(16)`) keeps it compact and fast to index. The reason to prefer UUIDs over integers here is forward-looking: if `Bird` ever scales to multiple servers generating records simultaneously, each can produce its own IDs without coordinating with the others. Integers can't do that safely.

Every table uses this same pattern for its primary key: a `BINARY(16)` column called `id`, defaulting to a freshly generated UUID.

### `users` - the identity record

The `users` table lives in the `ums` database. It is the authoritative record of everyone who has registered an account.

|Field|Type|Purpose|
|---|---|---|
|`id`|`BINARY(16)`|Primary key - uniquely identifies this user across the entire system|
|`name`|`VARCHAR(100)`|The display name shown on posts|
|`email`|`VARCHAR(255)`|Login credential and contact address; must be unique across all users|
|`password_hash`|`VARCHAR(255)`|The result of running the user's password through a one-way hashing function - never the password itself|
|`created_at`|`DATETIME`|When the account was registered|
|`updated_at`|`DATETIME`|When any field on this record was last changed; updated automatically|

Two fields deserve a word of explanation. `password_hash` stores a hashed password, not a plain-text one. A **hash function**is a one-way transformation: you can turn a password into a hash, but you cannot reverse the process. When a user logs in, the system hashes what they typed and compares the result to the stored hash - the original password never needs to be stored or retrieved. This is standard practice; storing plain passwords is a serious security failure.

`updated_at` tracks the last modification time and refreshes itself automatically on every write. It's low-cost to store and invaluable for debugging, auditing, and cache invalidation later.

### Supporting the `User`: roles and sessions

The use cases named registration - but a real identity system has two more concerns lurking just beneath the surface: _what is this user allowed to do_, and _is this user currently logged in_? These concerns get their own tables.

**`roles`** is a lookup table - a simple list of named permission levels (for example, `admin`, `moderator`, `member`). Roles don't come from the use cases directly; they come from the reality that not all users have the same permissions.

|Field|Type|Purpose|
|---|---|---|
|`id`|`BINARY(16)`|Primary key — uniquely identifies this role|
|`name`|`VARCHAR(50)`|The role label (e.g. `admin`, `member`) — must be unique|
|`description`|`VARCHAR(255)`|Optional human-readable explanation of what this role permits|

**`users_roles`** links users to roles. Because one user can hold multiple roles and one role can be held by many users, this is a **many-to-many relationship** - and the standard way to model that in a relational database is a join table: a table with two columns, each a reference to one side of the relationship.

**`sessions`** records active login sessions. When a user authenticates, a session row is created with a `logged_in_at` timestamp. When they log out, `logged_out_at` is filled in. This gives the system a full audit trail of who was logged in and when - and lets it invalidate specific sessions without forcing a global logout.

|Field|Type|Purpose|
|---|---|---|
|`id`|`BINARY(16)`|Primary key — uniquely identifies this session|
|`user_id`|`BINARY(16)`|References `ums.users.id` — whose session this is|
|`logged_in_at`|`DATETIME`|When the session started|
|`logged_out_at`|`DATETIME`|When the session ended; `NULL` if the user is still logged in|

None of these tables store messages or content. They belong entirely to the `ums` database and the identity domain.

### `messages` - the content record

The `messages` table lives in the `twitter` database. It is the record of everything posted.

|Field|Type|Purpose|
|---|---|---|
|`id`|`BINARY(16)`|Primary key - uniquely identifies this message|
|`author_id`|`BINARY(16)`|The `id` of the user who posted this message, from `ums.users`|
|`content`|`VARCHAR(280)`|The text of the message - capped at 280 characters|
|`created_at`|`DATETIME`|When the message was posted|

`content` is capped at 280 characters - the same limit Twitter uses, and a deliberate product constraint, not a technical one. The database enforces it with `VARCHAR(280)`.

`author_id` is the field that links a message to its author. It holds the `id` value of a row in `ums.users`. Because the two tables live in separate databases, MySQL cannot enforce this link with a formal foreign key constraint - but the relationship is real. The application layer is responsible for ensuring that no message is ever written with an `author_id` that doesn't correspond to a real user.

### `subscriptions` - the social graph

There is one more table in the `twitter` database: `subscriptions`. It didn't appear in the original three use cases, but it's present in the schema for a good reason - it's the data that would power a personalised timeline.

A subscription is a directional relationship between two users: one **subscriber** who follows one **producer**. The table has just three fields:

|Field|Type|Purpose|
|---|---|---|
|`subscriber_id`|`BINARY(16)`|The user doing the following|
|`producer_id`|`BINARY(16)`|The user being followed|
|`created_at`|`DATETIME`|When the follow happened|

The combination of `subscriber_id` and `producer_id` is the primary key - you can only follow someone once. Both columns are logical foreign keys to `ums.users.id`, subject to the same cross-database constraint limitation as `author_id` in `messages`.

`subscriptions` is infrastructure for a feature - _"Follow a user"_ - that isn't in scope for the current lesson's use cases but is correct to model now, because adding it later would require a migration. Modelling it upfront costs nothing; omitting it and adding it later costs a schema change and a deployment. This is the kind of forward-thinking that separates a considered data model from a reactive one.

## How the Entities Relate

Individual entities are only half the picture. A data model also defines how entities connect to one another - their **relationships**. For `Bird`, there are two:

**A User has many Messages** (one-to-many). One user can post any number of messages; each message belongs to exactly one user. This relationship is expressed through `author_id` in the `messages` table - a field that holds the `id` of the user who owns that row. Following the `author_id` from a message leads you to its author.

**A User can follow many Users, and be followed by many Users** (many-to-many). This is the social graph, modelled through the `subscriptions` table. To find everyone a user follows, query `subscriptions` where `subscriber_id` matches. To find everyone following a user, query where `producer_id` matches.

![[types of relationships.jpg]]

> **The pattern to remember.** A one-to-many relationship is expressed by putting the "one" side's `id` as a field on the "many" side - the foreign key lives in the child table. A many-to-many relationship requires its own table, with one column for each side. Both patterns appear in `Bird`, and together they cover the vast majority of real-world data relationships you'll encounter.

With the entities named, the fields defined, and the relationships mapped, the data model is complete. What remains is to choose a database engine and write the schema.

## What the Diagrams Will Now Be Built On

Lesson 1 introduced three lenses for looking at a system: functional structure, behaviour, and component interaction. Lesson 1 also made a promise — that diagrams would follow.

They will. But notice what's changed since then.

Before the data model existed, a flowchart for _"Post a message"_ would have had a step labelled something like _"save the message"_ — a placeholder that gestures at an action without defining it. Now that step has a precise meaning: create a row in `twitter.messages` with a `content` value, an `author_id` pointing to the authenticated user in `ums.users`, and a `created_at`timestamp set to now.

The data model doesn't just inform the diagrams — it creates clear mechanics how they work. Every box that reads or writes data now has a contract: specific fields, specific tables, specific relationships. The sequence diagram will name what passes between components. The functional diagram will know what each block owns. The flowchart steps will correspond to real operations.

That's where Lesson 3 picks up: with the data model as the foundation, we draw all three diagrams.

## Conclusion

A data model is the contract the rest of the system is written against.

We started with three use cases and asked a simple question: what must the system remember for each of these to work? That question led us to two entities — `User` and `Message` — and from there to five tables across two purposefully separated databases.

The separation itself was a design decision, not a convenience. Identity and access belong to one domain; content and social graph belong to another. Keeping them apart makes each easier to change, scale, and reason about independently. The trade-off — enforcing cross-database relationships in application code rather than at the database level — is a known and manageable cost.

Every field in the schema exists for a reason traceable back to a use case. Every relationship reflects a real dependency between things the system tracks. Nothing was added for completeness or anticipation — except `subscriptions`, which earns its place by being cheaper to model now than to migrate in later.

The diagrams come next. They'll have something real to say.
