# JWT at a Glance

Many of us heard about JWT and while JWT has become a buzzword in tech circles, it's frequently misunderstood or confused with OAuth 2.0 and OIDC, particularly among those who use it without fully grasping its intricacies. Mixing up JWT with OAuth 2.0 and OIDC is like tossing different fruits into a blender and calling it all "smoothie." It's especially messy when folks treat these tech tools like magic wands, waving them around without peeking under the hood.

What is JWT? By itself is a small piece of data that contains information about someone or something. It's like a small container which is able to keep and transfer information between two different destinations. Or it's like a digital badge that proves who the user is and what this user is authorized to do.

Let's imagine a library where anyone could walk in and borrow books without showing any identification. It would be chaos! The library needs a way to know who's borrowing what, and to ensure that only members can borrow books. In the digital world, JWT serves a similar purpose.
## Session Management Based Authorization

Traditional web applications often use sessions to keep track of who's logged in. This is like giving someone a special badge when they enter the library. Library staff can see the badge and then if they need to know details - they will check them out inside the computer. Let's take a look at the example below.
![Figure 1. Regular request-response flow](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/8wbl1asbe6lt60g2iuqk.png) Figure 1. Regular request-response flow

This diagram illustrates the basic flow of a web application, where the browser sends a request to the server, the server processes the request (potentially interacting with a database), and then sends a response back to the browser. Nothing complex, it's just a business as usual:
1. User sends a request to the `Service`, seeking for some information.
2. `Service` goes to the `Database` to retrieve that data from the long term storage.
3. Finally `Service` returns that data to the user in his browser to view.

Now, let's imagine if the `Service` holds sensitive personal information. Without security system to verify who's knocking on the door, there's a real danger of handing out private details to the wrong hands. It's like throwing a party and accidentally inviting the whole neighborhood when you meant to host a small gathering. In the digital world, this kind of mix-up isn't just embarrassing - it's a serious security risk that could expose confidential data to anyone who comes asking. That's a scenario is a "no-go" situation!

To prevent this situation to ever happen, let's think about implementing another service, which would be in charge to authenticate users and grant them special permissions which data they allow to access and which is not. Look at the diagram below:

![Figure 2. Regular request-response flow with Login Service](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/gcpr4d5sjqunyz7p3tgx.png)
Figure 2. Regular request-response flow with Login Service

What is changed on the diagram? Let's take a look again. We've introduced a new service which will be in charge for user's authentication and authorization. In other words we make this service exists to ensure proper user verification before granting access to the system's resources.

Prior to allowing any interaction with the data, this service requires users to authenticate themselves through a login process. Upon successful identification, the system initiates a session and issue a session identifier, or `SessionID`. In this context, a session is essentially a database record in `Auth Users` database indicating user is online and interacting with the system.

Upon successful authentication, all the rest interaction with the system no longer require the user to re-authenticate. Instead, the user's client (browser) simply keeps and provides back with every request the session identifier, which is securely stored in the `Auth Users` database. This identifier serves as a temporary credential, allowing the system to recognize and authorize the user for the duration of their session.

It may be shown like on the diagram below.

![Figure 3. Session Management](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/vgazf7ib6hm7qopv6rus.png)
Figure 3. Session Management

Let's walk through this web application flow step by step, in a way that's easy to understand:
1. The process begins with the browser initiating an HTTP request to the server. This should happen only after user has been authenticated and have a `Session ID` in hands as a response from the authentication flow.
	1. HTTP request itself is comprehensive and contains at least:
	    - The destination URL
	    - A token in the headers, any relevant cookies and optionally - a request body
	2. The token in the headers carries a `Session ID` - a unique identifier acting as a digital passport for the user's session.
2. Upon receiving the request, the `Service` doesn't immediately process it. Instead, it has to forwards the session information to the `Auth` component for verification of the request sender, i.e user.
3. The `Auth` service cross-references the `Session ID` with the database, essentially checking the list of sessions and its mapping to the provided `Session ID`. If there is a match, the `Auth` component retrieves and returns the associated user data, which may include any necessary data about the user, like user ID, first and last name of the user, his email and user's role and permissions.
5. Armed with this user information, `Service` can now safely decide whether user is able to interact with the system or not. Eventually, `Service` compiles the requested information and sends it back to the browser as an HTTP response if the user is authorized or rejects it if the user is not authorized.

That's it! As this process occurs with each interaction between user and the system, we may consider the system is safe unless the session token is not stolen or brute forced.

Is that good or bad approach? There is no straightforward answer. One of its greatest benefits is that the backend fully controls the access to all protected resources. By any chance if any request would be considered suspicious, user might be easily kicked off of the system by erasing a record in the `Auth Users` database with the `Session ID` associated to him.

On the other hand - backend needs to keep the state about user's status - whether he authenticated or not. This stateful nature of session-based authentication brings challenges.

As every request to the system necessitates a database lookup to verify the session we can easily imagine what happens if our UI sends N (where N > 0) concurrent requests to retrieve information from the backend (hello React and other SPA):

![Figure 4. System Bottleneck](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/hg52p38lc4f9lj42sn14.png)
Figure 4. Potential bottleneck with the session management

Take a look at the diagram above. On every user action, for example an initial page load, the UI may send 4 requests to fill out different page sections. That may happen as those data might be provided by different API Endpoints, like information about the user should be obtained from `/api/v1/users` and information about their appointments from another one, like `/api/v1/appointments`. More importantly, those requests are usually sent concurrently, as we want rapid page rendering in the user's browser.

Now let's estimate the cost of such an approach. Every user action with that page will push us to send 4 concurrent requests to the `Service`. Okay, that's doable. However each of those requests will also need be authorized, which means `Service` should ask `Auth` is that possible to proceed with them as it doesn't have any other information than `Session ID` which is nothing more than a link in `Auth Users` database. In that case `Service` needs to issue another 4 requests to the `Auth` and ask it about user information and details.

Easy calculation gives us that 1 user action creates 4 requests to one service in our backend and same amount for another service on the backend. In total, these eight actions will all result in database interactions. Let's imagine there are another services which also require confirmed authorization and we will understand the full picture.

Is it too much? The answer depends on the use case - sometimes it's necessary. However, is it possible to decrease the load on the database and other services?

## Stateless Authorization Management

There is another way to handle system security and authorize users without using session management. This alternative approach tackles some of the scalability headaches we saw earlier and it is often implemented using JSON Web Tokens (JWT).

As we mentioned earlier JWT is a small container which holds some information for us. Compare it with the `Session ID`:

![Figure 5. Compare Sessions with JWT approaches](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/wixqd8ycjvntrojx9mpy.png)
Figure 5. Compare Sessions with JWT approaches

In a JWT-based system, the server no longer needs to store session information. Instead, when user authenticates, the `Auth` generates a JWT - a compact, self-contained token that encapsulates all necessary user information and permissions. This token is then sent back to the client and stored, typically in local storage or a cookie.

Interesting thing happens on the next stage - when user needs to reach protected resources. Using previous approach we have to trigger authorization logic on every upcoming request on a different service which is `Auth` in the example above. What happened when we employ JWT?

Take a look at the diagram below.

![Figure 6. JWT based Authorization flow](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th4bbllayrjyqnul4ur4.png)
Figure 6. JWT based Authorization flow

When a user makes a request to access a protected resource, their client (typically the browser) automatically includes the JWT in the request headers. This is usually done by setting the Authorization header to "Bearer token", where `token` is the actual JWT.

Upon receiving the request, the `Service` no longer needs to consult with the `Auth` service for each incoming request. Instead, it can verify the JWT's integrity directly and decode the JWT on its own. This is possible because the JWT is cryptographically signed, and the `Service` has access to the JWT secret key or public key (in case of asymmetric signing) used to sign the token by `Auth` at the JWT creation time.

Once the signature is verified, the `Service` can decode the JWT payload. This payload contains all the necessary information about the user - their ID, roles, permissions, and any other relevant data that was included when the token was created. All of this happens without any database lookups or calls to the `Auth` service.

Finally with the user information available from the decoded JWT, the `Service` can make immediate authorization decisions. It can check if the user has the necessary permissions to access the requested resource, all without any additional network calls or database queries.

## JWT Structure

To make this flow happen JWT should be able to carry on some information. That includes not only some useful information we may want to store in the token, but also data, allowing to make the flow secured.

[RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) defines the JWT as follows.

> JSON Web Token (JWT) is a compact, URL-safe means of representing
   claims to be transferred between two parties.  The claims in a JWT
   are encoded as a JSON object that is used as the payload of a JSON
   Web Signature (JWS) structure or as the plaintext of a JSON Web
   Encryption (JWE) structure, enabling the claims to be digitally
   signed or integrity protected with a Message Authentication Code
   (MAC) and/or encrypted.

Using that we can describe the structure of a JWT as of (usually) consisting of three parts: a header, a payload, and a signature, separated by `.` (dot) symbol. The payload contains claims about the user, such as user ID, role, and expiration time. The signature, created using a secret key known only to the server, ensures the token's integrity and authenticity.

![Figure 7. JWT Structure](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/uy8kplddispzjryuw04q.png)
Figure 7. JWT Structure

All these 3 parts are separated by dot symbol and following in the order of:

```
header . payload . signature
```

These three components are encoded using the BASE64URL algorithm. This encoding method is closely related to standard BASE64, but with a few key differences. In BASE64URL, the output replaces the plus sign `+` with a minus sign `-`, and the forward slash `/` becomes an underscore `_`. Additionally, BASE64URL omits the typical padding found in standard BASE64, which usually consists of equal signs `=` at the end of the encoded string. These modifications make the encoded output more suitable for use in URLs and other contexts where certain characters might cause issues.
### Payload

If the payload (middle) part is more or less clear, as it is the container for user defined data, it still worth to take a look at some predefined fields over there.

[RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) standard calls data inside the payload a Climes Set and defines three classes of JWT Claim Names

> The JWT Claims Set represents a JSON object whose members are the
   claims conveyed by the JWT.  
   There are three classes of JWT Claim Names: Registered Claim Names,
   Public Claim Names, and Private Claim Names.

Registered Climes are those which defined by the standard and used by applications in case they considered as mandatory by developers. Here they are:
- `jti` (JWT ID) Claim
	a case-sensitive unique identifier for the JWT, designed to prevent token replay and ensure uniqueness across multiple issuers
- `iss` (Issuer) Claim
	identifies the JWT's issuer using a case-sensitive StringOrURI value, with processing typically application-specific
- `iat` (Issued At) Claim
	specifies the JWT's creation time, allowing for age determination of the token
- `sub` (Subject) Claim
	identifies the JWT's principal using a case-sensitive StringOrURI value, which must be locally or globally unique, and typically serves as the subject of the token's claims
- `aud` (Audience) Claim
	specifies the intended recipients of the JWT as a case-sensitive string or array of strings, each containing a StringOrURI value, and requires the processing principal to be identified within this claim for token acceptance
- `exp` (Expiration Time) Claim
	specifies the latest valid processing time for the JWT, with a small leeway often permitted for clock skew
- `nbf` (Not Before) Claim
	sets the earliest time the JWT can be processed, with a small leeway often allowed for clock skew

Different applications may use different claims from the list above, but many of them rely at least on 2 - which are `iat` and `exp` to determine the lifecycle of the token itself and when it should be regenerated.

Public Claims contains user defined information and may include there everything in JSON format. Usually developers create it with user data, which is necessary to be shown on the UI, user permissions and some additional information.
### Header

The JWT header plays a critical role in the token's functionality. This component,  appearing at the beginning of the token, contains metadata about the token itself. Two key elements stored in the header are the token type and the hashing algorithm used for the signature.

The token type, denoted by the `typ` claim, usually specifies `JWT` to indicate that the token is indeed a JSON Web Token. This information helps systems quickly identify and process the token appropriately. The hashing algorithm, represented by the `alg` claim, specifies the cryptographic algorithm employed to create the token's signature. Common algorithms are HMAC SHA256 (HS256) or RSA SHA256 (RS256), but there are many others which are possible.
### Signature

This section of the JWT is supposed to provide a mechanism of verification of the token integrity and authenticity. It is important and serves only for a one reason - prevent modification of any information at any stage.

This validation of the JWT happen on the backend `Service`, right after the `Service` received user's request for data. Server actually can recreate the signature using the same secret key (which is secretly stored on the backend) and algorithm (which is defined in the JWT header section). If the newly generated signature matches the one in the token, it confirms that the contents haven't been altered since the token's creation.
## Refreshing JSON Web Tokens

There is a last but not least thing to consider - JWT lifetime. After issuing a JWT to a user, we actually allowing him to access the protected data in accordance with his level of permissions. However do we want to limit it in time? In other words - do we want that user confirms his authenticity after some time or not?

Even though this question is not that obvious, the answer is straightforward and positive. User must to re-confirms his authenticity and he should do that within a reasonable amount of time. It matters because we can't exclude the situation or JWT leakage, as what goes to browser is available to the rest of the world. JWT provides safety mechanism from data modifications (by signing them and later signature verification), but they do not save from reusing them.

This brings us to the concept of JWT refreshing. While limiting the lifetime of a JWT is necessary for security reasons, it can also lead to a poor user experience if the token expires too quickly, forcing frequent re-authentication. And this is where refresh tokens come into play.

A refresh token is another special token that can be used to obtain a new JWT once the original JWT has expired. Unlike JWTs, refresh tokens are typically stored server-side only and are associated with a specific user, using some of its unique data, like a hash of the JWT itself. They have a longer lifespan than JWTs but are only used to verify one thing - the old JWT is valid even if it is expired and we can safely issue a new one. In other words it let us know that original JWT was not modified and still can be trusted.

This approach balances security and user experience. It allows for short-lived JWT reducing the window of potential token misuse, while also allowing users to remain logged in for extended periods without explicit re-authentication.
## Scalability Advantages of JWT

The stateless nature of JWT provides a significant boost especially for distributed systems in terms of scalability, when compared to traditional session-based authentication systems. This makes JWT an attractive approach for modern, distributed applications, such as those deployed in cloud environments or utilizing load-balanced architectures.

In traditional session-based systems, user authentication data is stored on the server side, typically in a database or in-memory store. Each time a user makes a request, the server must retrieve this session information to verify the user's identity and permissions. As the number of concurrent users grows, this approach can lead to increased load on the session store, potentially becoming a bottleneck in the system.

JWT, on the other hand, encapsulate all necessary authentication and authorization information within the token itself. When a user authenticates, the server generates a JWT containing the user's identity and permissions, then sends this token back to the client. For subsequent requests, the client includes this token, allowing the server to verify the user's identity and permissions without querying a central session store.

JWT's stateless nature aligns well with microservices architectures. In a microservices environment, different services can easily validate the JWT and extract necessary information without maintaining complex, centralized session management systems. This decoupling of authentication state from individual services enhances the overall scalability and flexibility of the system.

## Next Steps

In the next article, we'll take a look further into the authentication and authorization cased by integrating JWT and two other important protocols: OAuth 2.0 and OpenID Connect (OIDC). Stay tuned to learn how combining JWT with OAuth 2.0 and OIDC can enhance your application's security posture while maintaining the scalability benefits we've discussed!