# A native macOS load tester app — and backpressure made it honest

_Why I built [Requester](https://github.com/eugenezimin/requester-public/releases), a real-time HTTP load testing app for macOS, and what Swift structured concurrency taught me about telling the truth under load._

I wanted to hammer an HTTP endpoint and _see_ what happened. Not read a summary report three minutes later — watch it, live, the way you watch a profiler.

The existing options are great but they all live in the terminal: `wrk`, `hey`, `k6`. I love them, but I kept wishing for a native window with a chart that moved. So I built one for macOS, in Swift and SwiftUI, and called it **Requester**.

This post is less "here are the features" and more "here are the three things I made building it." The most interesting one: making the tool _honest_ about backpressure turned out to be a design decision, not an accident.

![Main Window](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ij84li1dcg5uv6qhao0q.png)

## The model: RPS per channel × channels

Before any code, I needed a mental model the user could reason about. I landed on two knobs:

- **Channels** — how many requests can be in flight at once to emulate multiuser load (even though from a single host).
- **RPS per channel** — the rate I _want_ each channel to sustain.

So the total target rate is just `channels × rpsPerChannel`. No hidden division, no surprises. The dispatcher converts that into a fixed firing interval:

```swift
let interval = Duration.seconds(
    1.0 / Double(session.throughputPerSec * session.concurrency))
```

The win here is conceptual, not technical: the number you type is the number you get (when the endpoint can keep up). Which brings me to the part where it _can't_.

## A load tester should lie down when the server does

Here's the temptation. You set a target of 500 RPS. The endpoint can only serve 200. What do you do with the other 300 requests every second?

The naive answer is "buffer them." But then your queue grows without bound, memory balloons, and — worse — your tool reports that it's happily firing 500 RPS while reality is nowhere close. That's a lie, and it's the most dangerous kind because it looks like success.

So Requester does the opposite. The dispatcher fires requests as independent child tasks and never awaits a response. A single actor gates how many can be in flight:

```swift
private actor InFlightCounter {
    private let limit: Int
    private let maxQueueDepth: Int
    private var current = 0
    private var waiters: [CheckedContinuation<Void, Never>] = []

    func acquireSlot() async -> Bool {
        // Queue is full — shed this request, don't buffer forever.
        guard waiters.count < maxQueueDepth else { return false }

        if current < limit {
            current += 1
            return true
        }
        // At the limit: suspend until a response frees a slot.
        await withCheckedContinuation { waiters.append($0) }
        current += 1
        return true
    }

    func release() {
        current = max(0, current - 1)
        if !waiters.isEmpty { waiters.removeFirst().resume() }
    }
}
```

Two behaviors fall out of this:

1. **The dispatcher suspends when every channel is busy.** It can't fire faster than responses come back. So the _achieved_ RPS visibly drops below your target — and that dip is exactly the signal you came for. The chart tells you the truth.
2. **Past a configurable queue depth, requests are shed**, not buffered. Bounded memory, bounded lag, no fantasy throughput.

When the green "Received" line peels away from the blue "Sent" line on the chart, that's the endpoint saying _uncle_. I didn't have to build a special "the server is struggling" indicator. The honest plumbing surfaces it for free.

![Stats View](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ig9zh5ssremd49vp6ugc.png)

## Structured concurrency made the whole thing boring (in the best way)

The entire engine is `async`/`await`, `TaskGroup`, and actors — no GCD queues, no completion-handler pyramids, no manual locks.

The dispatcher and a snapshot timer run as siblings in one `TaskGroup`. The dispatcher records per-request outcomes into a `RunCounter` **actor**; the timer reads a delta from that same actor once per sampling interval and emits a `.tick` event. Because the counter is actor-isolated, the N writers and the one reader never race — and I never wrote a lock.

```swift
actor RunCounter {
    private(set) var totalCompleted = 0
    private(set) var totalFailed = 0

    func record(_ outcome: RequestOutcome) {
        switch outcome {
        case .success: totalCompleted += 1
        case .failure: totalFailed += 1
        }
    }

    /// Delta since the last read, then advance the baseline.
    func snapshot() -> (completedDelta: Int, /* … */ totalCompleted: Int) {
        let cd = totalCompleted - lastCompleted
        lastCompleted = totalCompleted
        return (cd, /* … */ totalCompleted)
    }
}
```

Events flow up through an `AsyncThrowingStream` from the transport adapter, into a facade, and finally onto `@Published`properties in a `@MainActor` view model. SwiftUI redraws. The chart moves. Each layer has exactly one job and they communicate through `Sendable` values crossing isolation boundaries safely.

The payoff: the scary part of a load tester — concurrent state — became the calmest part of the codebase.

## URLSession will silently eat your headers

This one cost me an embarrassing amount of time, so you get it for free.

I set a custom `User-Agent` on my `URLRequest` like any reasonable person:

```swift
request.setValue(session.userAgent, forHTTPHeaderField: "User-Agent") // 😶 silently dropped
```

It never showed up on the wire. Turns out `URLSession` treats `User-Agent` (and other reserved headers) as off-limits at the _request_ level and quietly strips them. The fix is to set them on the **configuration** instead:

```swift
let config = URLSessionConfiguration.ephemeral
config.httpAdditionalHeaders = ["User-Agent": session.userAgent] // ✅ actually sent
```

No error, no warning — it just works when you move it. If you've ever sworn your custom User-Agent "isn't applying," this is probably why. Requester ships with realistic browser presets (Safari, Chrome, Firefox, mobile variants, `curl`, Googlebot) precisely so you can test how an endpoint responds to different clients.

![Headers](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/esymxzo7jea43ghv0y0z.png)

## Seeing the actual bytes

A throughput chart tells you _how much_; sometimes you need _what_. Requester has a request/response inspector that shows the exact request being fired and the live responses coming back — status line, headers, body — with a sliding-window history and an optional truncation toggle for noisy bodies.

![Loads View](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/kssfxbo0xh6dngsq83dq.png)

## What's next

HTTP is what ships today. The transport layer is already abstracted behind a `TransportAdapter` protocol (which also made testing trivial — every transport has a mock), so the architecture is ready for more:

- **gRPC** endpoint testing
- **WebSocket** load
- **Raw TCP** load

Requester is a native macOS app built entirely in Swift and SwiftUI, targeting macOS 14+.

Built by Eugene Zimin and available on — [GitHub](https://github.com/eugenezimin/requester-public/releases).

_If you've built load-testing tooling, I'd love to hear how you handled the buffer-vs-shed question — drop a comment._