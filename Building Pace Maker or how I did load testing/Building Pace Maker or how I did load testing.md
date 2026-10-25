---
title: Building Pace Maker or how I did load testing
published: true
description: How a small Swift and SwiftUI app separates pacing from concurrency, measures honestly, and ships signed releases from a private repository into a public one
tags: swift, macos, performance, devops
---
# Building Pace Maker or how I did load testing

Most of the load tests I have run over the years were not grand capacity-planning exercises but small and slightly anxious questions asked late in the afternoon, such as whether a freshly deployed endpoint would survive a few hundred requests per second or whether a caching change had actually made a service faster, and almost every time the tooling around those questions felt heavier than the questions themselves. Just imagine the JMeter - nothing wrong, but I'd rather use a curl with a loop, than spend time on setting it up, even though it's powerful. Writing a scenario file, pulling a container image, or keeping a browser tab open on a hosted dashboard is perfectly reasonable for a scheduled performance suite, yet it is a lot of ceremony when all you want is to point something at a URL, decide how hard to push, and watch what happens. Brrr, no. I stopped and decided to make something which is free and much comfortable for me. 

That's how Pace Maker, a small native macOS app written in Swift and SwiftUI, was appeared.

![Pace Maker running a load test, with the live chart in the main area and the settings inspector on the right](Publications/Articles/Building%20Pace%20Maker%20or%20how%20I%20did%20load%20testing/images/main_window.png)

## Why?

Thinking about who would actually reach for such a tool shaped almost every later decision, because the typical user is a backend developer who already knows the endpoint, has a rough idea of the expected traffic, and mostly needs a fast and trustworthy feedback loop rather than a report generator, which means the window should be organized around the one thing that person keeps looking at while the test runs. And that's exactly what I needed.

The application is simple yet powerful - its live chart owns the main area of the window, the settings live in a native inspector that can be hidden once a test is configured, and the controls that change the state of a run, together with the elapsed time and the number of requests sent, sit in the toolbar and the window subtitle, where they stay visible without competing with the data. Name it "focus mode", but that's definitely not a cockpit.

## Separating pacing from concurrency

The most important architectural idea in the app is that the rate at which requests are released and the number of requests allowed to be in flight are two different concerns, and conflating them is the reason so many simple load generators quietly misreport what they measured. If a tool sends the next request only after a previous one returns, a slow server automatically slows the tool down, and the chart ends up showing whatever pace the server could tolerate instead of the pace you asked for, which hides precisely the degradation you were trying to observe.

![The request pipeline, from the rate pacer through the backlog and the adaptive connection gate to the worker pool, with outcomes flowing back through counters and the sampler](pipeline.png)

Pace Maker therefore releases requests on a schedule derived from the target rate alone, and those requests enter a bounded backlog that is served by a fixed pool of workers, so nothing is created per request thus memory stays flat regardless of how long a test runs or how high the rate goes. At the same time between the backlog and the workers sits an adaptive connection gate, which decides how many requests may be in flight at any moment by reasoning roughly along the lines of Little's law, since the concurrency needed to sustain a rate is approximately that rate multiplied by the current latency, and which backs off when errors climb while throughput stalls, because that combination usually signals a saturated server rather than one that merely needs more connections. When the backlog fills up, the excess is shed and counted instead of being buffered without limit, and this choice is what keeps the backpressure honest, because the user sees the achieved rate fall below the target exactly when the endpoint can no longer keep up, which is the very signal a load test exists to produce.

## Measuring as if someone will check

A chart is only as useful as the arithmetic behind it, and several of the more instructive bugs in the project came from numbers that looked plausible while being subtly wrong, such as failures being counted per sampling window while successes were normalized per second, which quietly halved the apparent error rate whenever the sampling interval was shorter than a second. Every series is now normalized to requests per second, the error rate is defined as the share of finished requests that failed rather than the share of requests sent, and the final partial window of a run is included in the totals but deliberately left out of the chart, because a rate computed over a few milliseconds is noise that would otherwise draw a dramatic spike at the very end of an otherwise calm test. The same concern for honesty extends to pausing, since resuming a test continues with whatever time and request budget remain, so a sixty-second test stays a sixty-second test no matter how often it is interrupted.

## Composing real requests

Read endpoints are only half of most APIs, so the app sends every common HTTP method, from GET and HEAD through POST, PUT, PATCH, and DELETE to OPTIONS, and the methods that carry a body get a dedicated Load tab in which the body is written, typed as JSON, form data, plain text, or XML, and highlighted as you type.

![The Load tab with a JSON request body and its live size and validity check](load.png)

Building that editor surfaced a small lesson that is easy to miss, because the standard text editor on macOS follows the system setting for smart quotes and silently turns straight quotation marks into typographic ones, which produces JSON that looks correct on screen and fails on the server, so the body editor disables every automatic substitution and shows a live check of the body size and of whether the JSON is valid. The Texts tab then closes the loop by showing the request exactly as it is sent, together with the most recent distinct responses, which makes it easy to confirm that the server answered with the expected status and payload before trusting anything the chart says.

![The Texts tab showing the request as sent and the most recent responses](Publications/Articles/Building%20Pace%20Maker%20or%20how%20I%20did%20load%20testing/images/texts.png)

## Architecture

Underneath the interface the structure is deliberately plain, with SwiftUI views observing a single session model, the model talking to an engine facade that owns the lifecycle of a run, and the facade delegating the actual traffic to a transport adapter, so that the views never know how requests are sent and the adapters never know how anything is drawn.

![The layers of the app, from the SwiftUI interface through the observable session model and the engine facade down to the transport adapters](architecture.png)

Because the model is observable at the level of individual properties, a tick from the engine redraws only the views that display tick data, and editing a setting no longer redraws the chart, which mattered more than expected once tests ran long enough to accumulate thousands of points. The adapter boundary is also where the roadmap lives, since HTTP is the only real transport today while gRPC, WebSocket, and raw TCP are planned as further adapters behind the same contract, and keeping the pure parts of the system, such as the pacing arithmetic, the chart windowing, and the response bookkeeping, free of interface code is what allows most of the behavior to be covered by fast unit tests that run on every pull request.

## Where it goes from here

Pace Maker is still a small tool, and that is very much the point, because the value of a quick load test lies in how little stands between the question and the answer. The next steps are the remaining transports and a few refinements to how the connection gate tells random errors apart from genuine saturation, and if you would like to try the current release, the signed builds and a full feature overview are available in the [public repository](https://github.com/eugenezimin/Pace-Maker).
