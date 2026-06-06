# A native macOS load tester app — and backpressure made it honest

An article about building Requester, a real-time HTTP load testing app for macOS written in Swift and SwiftUI. The piece explores three key design decisions: using a simple RPS-per-channel concurrency model, implementing honest backpressure (shedding requests instead of buffering them indefinitely), and leveraging Swift structured concurrency (`async`/`await`, actors, `TaskGroup`) to safely coordinate concurrent state.

The article includes practical insights on pitfalls (like URLSession silently dropping custom headers) and demonstrates how a load tester's UI can make the truth about server bottlenecks immediately visible — when the "Received" line dips below "Sent," the endpoint is struggling.

Published on [Medium](https://medium.com/@eugene-zimin/a-native-macos-load-tester-app-and-backpressure-made-it-honest-6b72d946f4d0) and [DEV.to](https://dev.to/eugene-zimin/a-native-macos-load-tester-app-and-backpressure-made-it-honest-3jah).
