---
title: "Your codebase is the real prompt"
date: "2026-07-11T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/your-codebase-is-the-real-prompt"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "AI"
  - "Software Architecture"
  - "Spring Boot"
description: "AI agents treat your codebase like a new hire with amnesia. Here's why deep modules, not better prompts, are what make them useful, with a Spring Boot example."
---

I spawn a lot of AI coding agents at work. Some finish a task with barely any guidance. Others get lost, make a change in the wrong place, or return something that works only after I patch the pieces together myself.

I used to blame the prompt. If the output was bad, I would rewrite the instructions, add more context, and try again. But the more agents I use, the less convinced I am that the prompt is the main problem.

An agent can receive a detailed task and still struggle if the codebase is difficult to navigate. It opens one file, follows five imports, finds three abstractions with similar names, and spends most of its time reconstructing a mental model that I already have in my head.

The prompt might be clear. The environment is not.

I recently came across an idea from Matt Pocock that stayed with me: every agent enters the codebase like a new starter with no memory. It is a little like the main character in _Memento_ walking in every morning and asking, "What am I doing here?"

That changed how I think about agentic coding. The codebase itself is the real prompt.

## The Cost of Starting From Zero

An agent starting without a mental model creates three costs. First, the feedback loop gets slow. The agent spends time reading files and tracing dependencies before it can make a useful change. If the tests are also slow, it takes even longer to learn whether that change was correct.

Second, the codebase is hard to navigate. What feels like a clear architecture to me may look like hundreds of equally important files to an agent. It does not know which path is normal and which one is leftover from a migration three years ago.

Third, I become the integration layer. I correct the imports, move logic into the right service, and patch the edge cases the agent missed. Do that often enough and the productivity gain starts to look suspiciously like extra work.

## What the Agent Actually Sees

When I look at a system I have worked on for years, I do not just see files. I know which services are important, which abstractions are accidental, which parts are safe to change, and which parts only look unused.

An AI agent does not begin with any of that context. It sees a flat collection of files and relationships. It has to discover the architecture every time it starts.

That discovery becomes expensive when a codebase is made of many small, interconnected pieces:

```text
auth/
  PasswordHasher.java
  TokenGenerator.java
  SessionRepository.java

user/
  UserRepository.java
  UserService.java

web/
  LoginController.java
```

The folder structure looks clean, but the controller might call the user service, password hasher, token generator, and session repository directly. To understand login, the agent has to trace the entire web.

Humans pay the same cost. We are simply better at hiding it from ourselves because we carry context between tasks. An agent carries only what fits in its current session, then the next one starts over.

## Deep Modules Reduce the Surface Area

The alternative is a deep module: a small public interface hiding a larger implementation. Instead of hundreds of shallow pieces that all know about each other, the system is organized into a few substantial capabilities. Seven or eight is not a hard rule, but it is a more useful direction than seven or eight hundred places to start.

The idea comes from John Ousterhout's [_A Philosophy of Software Design_](https://web.stanford.edu/~ouster/cgi-bin/book.php). A module is deep when it provides a lot of useful behavior through a simple interface. A shallow module exposes almost as much complexity as it hides.

For authentication, the rest of the application should not need to know how passwords are hashed, how sessions are stored, or how tokens are created. It should only need to know what the authentication module can do.

```text
auth/
  AuthService.java          <- public boundary
  AuthServiceImpl.java      <- package-private
  PasswordHasher.java       <- package-private
  CredentialStore.java      <- package-private
  TokenGenerator.java       <- package-private
  AuthServiceTest.java      <- locks down behavior
```

Instead of exposing the plumbing, the module exposes one capability. This is progressive disclosure in code. An agent can read `AuthService` first and understand the module without reading its implementation. It only goes deeper when the task requires it.

## A Small Spring Boot Example

Here is the public boundary:

```java
package com.example.auth;

import java.util.Optional;

public interface AuthService {
    void signUp(String email, String password);
    Optional<String> logIn(String email, String password);
}
```

The rest of the application depends only on this interface:

```java
package com.example.web;

import com.example.auth.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LoginController {
    private final AuthService auth;

    public LoginController(AuthService auth) {
        this.auth = auth;
    }

    @PostMapping("/login")
    ResponseEntity<String> logIn(@RequestBody Credentials credentials) {
        return auth.logIn(credentials.email(), credentials.password())
            .map(ResponseEntity::ok)
            .orElseGet(() -> ResponseEntity.status(401).build());
    }

    record Credentials(String email, String password) {}
}
```

The implementation and its collaborators stay package-private inside `com.example.auth`:

```java
package com.example.auth;

import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
class AuthServiceImpl implements AuthService {
    private final PasswordHasher passwords;
    private final CredentialStore credentials;
    private final TokenGenerator tokens;

    AuthServiceImpl(
        PasswordHasher passwords,
        CredentialStore credentials,
        TokenGenerator tokens
    ) {
        this.passwords = passwords;
        this.credentials = credentials;
        this.tokens = tokens;
    }

    @Override
    public void signUp(String email, String password) {
        credentials.save(email, passwords.hash(password));
    }

    @Override
    public Optional<String> logIn(String email, String password) {
        return credentials.findPasswordHash(email)
            .filter(hash -> passwords.matches(password, hash))
            .map(ignored -> tokens.create(email));
    }
}
```

The collaborators are ordinary package-private Spring beans. Here is a small in-memory version, enough to make the example complete:

```java
package com.example.auth;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
class PasswordHasher {
    private final PasswordEncoder encoder =
        PasswordEncoderFactories.createDelegatingPasswordEncoder();

    String hash(String raw) {
        return encoder.encode(raw);
    }

    boolean matches(String raw, String encoded) {
        return encoder.matches(raw, encoded);
    }
}

@Component
class CredentialStore {
    private final Map<String, String> passwordHashes =
        new ConcurrentHashMap<>();

    void save(String email, String passwordHash) {
        passwordHashes.put(email, passwordHash);
    }

    Optional<String> findPasswordHash(String email) {
        return Optional.ofNullable(passwordHashes.get(email));
    }
}

@Component
class TokenGenerator {
    String create(String email) {
        return UUID.randomUUID().toString();
    }
}
```

In a real application, `CredentialStore` would use a database and `TokenGenerator` would create a signed, expiring token. Those choices stay inside the module. Code outside the package cannot instantiate these collaborators, write directly to the credential store, or invent a second login flow. It has one way in.

I would keep these classes in the same Java package. Java subpackages are different packages, so moving `PasswordHasher` to `com.example.auth.internal` would require making it public or enforcing the boundary with another tool.

## The Grey Box

I like to think of this as a grey box. A black box asks me to trust something I cannot inspect. A white box asks me to understand every implementation detail. A grey box gives me a boundary I own and internals I can inspect when necessary, but do not need to manage line by line.

For AI-assisted work, I want to own three things:

- the public interface
- the module boundary
- the tests that define its behavior

The agent can work inside that boundary. It can refactor the password hashing flow, replace the token implementation, or reorganize the session storage. If the interface remains stable and the tests pass, the change is easier to review.

This maps closely to how I already think about being [in the loop or on the loop](/posts/in-the-loop-or-on-the-loop), and to the Maker-Checker pattern. I am the checker at the boundary: I decide what the module promises and verify the result. The agent is the maker inside it: it can implement the behavior without changing the rules around it.

I stay in the loop when deciding what the module should expose. I can move on the loop for more of the implementation because the blast radius is controlled.

That does not mean I blindly trust the code. It means I spend my attention where it has the most leverage.

## Tests Are Part of the Interface

A simple interface is not enough if its behavior is ambiguous. The tests explain what the types cannot.

```java
@SpringBootTest
class AuthServiceTest {
    @Autowired
    AuthService auth;

    @Test
    void returnsTokenForValidCredentials() {
        auth.signUp("me@example.com", "correct-password");

        assertTrue(
            auth.logIn("me@example.com", "correct-password").isPresent()
        );
    }

    @Test
    void rejectsInvalidPassword() {
        auth.signUp("me@example.com", "correct-password");

        assertTrue(
            auth.logIn("me@example.com", "wrong-password").isEmpty()
        );
    }
}
```

These tests do more than prevent regressions. They give the agent a fast feedback loop. The agent does not have to guess whether its change worked, and I do not have to reconstruct the entire implementation to review it.

Slow or unreliable tests weaken this model. If feedback takes twenty minutes, the agent will make several decisions before learning that the first one was wrong. Fast tests keep the work inside a tight loop.

## The Hard Part Is Still Ours

Deep modules do not remove the need for engineering judgment. They move it to the boundary.

Someone still has to decide what belongs together, what the interface should promise, and which behaviors need tests. An AI agent can suggest those decisions, but it does not know the full context of the product, team, or business.

This is where taste matters. A bad boundary can make a deep module harder to use than the code it replaced. A giant `ApplicationService` with fifty methods is not deep. It is just large.

The goal is not fewer files for the sake of fewer files. The goal is fewer concepts that the rest of the system must understand.

## None of This Is New

That might be the most useful part of the idea. We do not need a special architecture for AI. Clear boundaries, encapsulation, stable interfaces, and fast tests have made codebases easier for humans to work in for decades. They also happen to make codebases easier for agents to navigate.

What works for a new engineer works for an AI agent: show them where to start, limit what they need to understand, and give them quick feedback when they get something wrong.

Better prompts still help. But when I find myself repeatedly explaining the same architecture to an agent, I now take that as a signal. Maybe the missing context belongs in the codebase.

I am not designing for the machine. I am designing for the next person who has to read the code. That person just happens to show up twenty times a day now.
