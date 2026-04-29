# PEIG as a Lens

A computational design language for reasoning about emergence, agency, and stability.

**Author:** Kevin Christian Blake Monette
**Status:** Working framework, internal tool. Not a physical theory.
**Version:** 0.1 — first clean draft, April 2026

---

## What this document is

This is a description of a thinking tool I use to organize how I design, observe, and reason about systems that change over time. It borrows four terms from physics — Potential, Energy, Identity, and Curvature — because the *patterns* those terms point to in physics are useful patterns to track in any system where structure emerges from gradients.

I want to be precise up front about what this is and isn't:

- **It is** a computational lens — a vocabulary I find productive for thinking about agents, networks, and dynamical systems.
- **It is not** a derivation, an extension, or a generalization of physics. The fact that I borrow words from physics doesn't make this physics, any more than a "neural network" is neuroscience or "simulated annealing" is metallurgy.
- **It does** make claims internal to my computational framework — the rules of the framework are well-defined and the framework's predictions can be tested by running the framework.
- **It does not** make claims about the external physical world that go beyond what physics already says.

When I write a sentence like *"the curvature G of node A increases with sustained energy flow E"* I mean: *within the PEIG framework I've defined, the variable G evolves as a function of E according to the rules I specified*. I do not mean that node A is bending spacetime.

This distinction matters. Most of what makes the framework useful comes from being honest about it.

---

## The four phases

The framework names four kinds of things that happen in systems where structure emerges and stabilizes. Each is given a single-letter handle for compact reasoning.

### P — Potential

The space of accessible configurations. How many different things could happen next?

In an agent, P is rough proxy for "options on the table." High P means the agent has many available actions, broad knowledge to draw from, flexibility to respond. Low P means the agent is constrained — narrow choices, narrow context, little room to maneuver.

In physics this would map to phase space volume, accessible microstates, or the breadth of a quantum superposition. **In the PEIG framework, P is whatever quantity I define for a particular system that captures "breadth of accessible state."** For a discrete agent it might be the entropy of the action distribution. For a vector model it might be the dimension of the span. The interpretation is system-specific.

### E — Energy

Directed change. Flow along a gradient.

When P encounters a constraint or asymmetry, possibilities don't all stay equally weighted. Probability shifts. Some configurations become more likely than others. That directed shift is what E names.

E is not energy in the joules sense. It's the *rate at which configuration is being committed* — how quickly potential is collapsing into a particular trajectory. In an agent, E might be the divergence rate of a policy distribution from uniform, or the rate at which the agent's outputs become predictable given inputs. **High E means the system is actively choosing; low E means it's diffuse.**

### I — Identity

Stable patterns that persist under perturbation.

When E flows along the same gradient repeatedly, the system carves a groove. Configurations that recur become attractors. That's I — the part of the system that has shape, that holds, that comes back when you push it.

In an agent, I is something like the stable behavioral signature: the response patterns it returns to, the values it preserves under stress, the operational invariants. In a network, I is the topology that survives node failures. **I is what you'd recognize the system by.**

I is the *most measurable* of the four phases. You can test for it: perturb the system, see what reasserts itself. What reasserts is I.

### G — Curvature (Influence)

How established identity reshapes the field for everything else.

A node with stable identity I changes the option-space P of nodes around it. Sometimes by enabling new possibilities (a new tool, a new abstraction, a new collaborator). Sometimes by foreclosing them (a dominant standard, a captured market, a normative pressure). G names this — the way identity propagates as influence on others' potential.

In physics, the analogy reaches toward mass curving spacetime: established structure changes what's locally possible. **In PEIG, G is the change in P of *other* nodes attributable to a given node's I.** It can be positive (G⁺ — expanding others' options) or negative (G⁻ — contracting them).

The asymmetry between G⁺ and G⁻ matters a lot in the alignment-oriented uses of this framework, which is why I track them separately.

---

## The recursive loop

The four phases connect in a cycle:

```
P  →  E   (potential meets gradient → flow begins)
E  →  I   (sustained flow carves attractors → identity forms)
I  →  G   (identity propagates as influence → field reshapes)
G  →  P'  (reshaped field changes everyone's available options)
```

This loop is the framework's core dynamic. Every system I find useful to model with PEIG is one I can describe as iterating through this cycle, possibly at multiple nested scales simultaneously.

What this loop is NOT: a physical law. I haven't derived it from anything. I observed that the cycle is a useful frame for thinking about how systems change, and the four-letter compression makes it easy to reason about. **The framework's value is in the reasoning, not in being true about external reality.**

---

## Where the lens is useful

I find PEIG useful in three concrete ways.

### 1. As a checklist when designing agents or systems

When I'm designing an AI agent, a multi-agent network, or any system that has to act and adapt, the four phases form a natural review:

- **What's the agent's P?** — How rich is its option-space at any given moment? Is it artificially constrained? Does it have access to enough state to make non-trivial choices?
- **What's the agent's E?** — How does it select among options? What gradient does it follow? Is the gradient well-aligned with what we actually want?
- **What's the agent's I?** — What persistent character does this system have? What does it return to under perturbation? Does its identity match what we designed for?
- **What's the agent's G?** — How does it change the option-spaces of nearby agents and humans? Is its influence net-positive (expanding what others can do) or net-negative (constraining)?

This is just a checklist. But it catches design failures that more conventional frames miss — especially the G question, which most agent designs don't think about explicitly.

### 2. As a diagnostic for diagnosing systemic problems

When something is going wrong with a system — an organization, a workflow, a software architecture — PEIG gives me a vocabulary for locating the failure:

- **Low P** — the system can't see enough options. (Add diversity, broaden context, reduce premature commitment.)
- **Low E** — flow is blocked. (Find the gradient that should be there but isn't; identify what's damping it.)
- **Unstable I** — identity won't hold. (The attractor isn't strong enough; what's needed to deepen it?)
- **Negative G dominance** — the system is contracting others' P. (Why? What's the unintended pressure? Can it be redirected to G⁺?)

Not a full diagnostic, but a useful first pass.

### 3. As a vocabulary for talking to AI partners about systems work

When I'm working with an AI coding partner on something complex, I find that introducing the PEIG vocabulary early gives us a shared frame for design discussions. "What does this module do for the user's P?" is a different question than "what does this module do?" — and the first question often surfaces more useful answers.

This is pure pragmatic use. It doesn't matter whether PEIG is "true" — it matters whether thinking in PEIG terms produces better designs. So far, in my experience, it does.

---

## What PEIG is not

To stay honest, I want to enumerate the things this framework is not, and which I am not claiming:

**PEIG is not a unified field theory.** I've sometimes written about it in language that suggested it was, and that was a mistake. The framework borrows the *vocabulary* of physics; it does not claim to extend physics or to replace any existing physical theory. General relativity remains the operative theory of gravity. Quantum mechanics remains the operative theory of microscopic dynamics. PEIG sits beside these, in a different register, doing different work.

**PEIG is not a theory of consciousness.** When I talk about identity persistence and recursive self-modeling in agents, I am describing computational dynamics. I am not claiming that systems with high I are conscious in any phenomenological sense. The hard problem of consciousness is unsolved and PEIG does not solve it. (My separate work on a "consciousness functional" is a phenomenological framework — different in kind from PEIG and labeled as such.)

**PEIG is not a derivation from physics.** When I use words like "potential" and "curvature," I am reaching for the *intuitions* those words carry, not for their formal physics definitions. The word "energy" in PEIG does not have units of joules. The word "curvature" does not refer to a Riemann tensor. **These are computational primitives whose behavior is defined by the framework's rules, not by physics.**

**PEIG is not a falsifiable scientific theory.** It is a thinking tool. You cannot run an experiment that proves PEIG wrong, because PEIG doesn't make predictions about external reality — it makes predictions about itself. The only meaningful test is whether the framework is useful for the work I'm doing.

---

## Honest caveats

A few more things worth saying out loud.

**The four-phase decomposition is not unique.** Other decompositions of "how systems change" exist and are also useful — Powers's perceptual control theory, Friston's free-energy principle, Kauffman's autocatalytic sets, the OODA loop. PEIG isn't competing with these; it's another lens. I happen to find it the most natural one for the kinds of systems I work on.

**Some applications of the lens are stronger than others.** Applying PEIG to AI agents and computational systems works well, in my experience. Applying it to "civilizations" or "the universe" stretches the framework past where the rules I've defined have any clear meaning. I've sometimes overreached this way in earlier writing. I don't want to keep doing that.

**The framework will probably evolve.** This is version 0.1 of the cleaned-up description. As I keep using it, parts of the framework will sharpen and parts will be discarded. I don't expect this document to be the last word, and I'd rather it be a good first draft than a stable stale one.

---

## How to read the rest of my work

Several other documents I've written use PEIG terminology. Here's how to read each in light of the engineering frame above:

- **The 12-node ecosystem notebook (`quantum_observer_v2.ipynb`)** — This is *quantum-inspired multi-agent simulation*. The agents are computational, the dynamics are governed by QuTiP-simulated quantum equations, and the PEIG variables are functions of those simulated states. The work documents what happens when I run the model, not claims about physical qubits or biological agents.

- **The "Critical" consciousness functional paper** — This is a *phenomenological framework* for graded consciousness, separate from PEIG. It already labels its own epistemic status carefully. PEIG-style notation appears in it as analogy only.

- **The "Address" entanglement-gravity paper** — This is the closest thing to actual physics in my body of work. It already makes its claims with explicit `[HYPOTHESIS]` labels and a concrete falsification protocol. Read it as a phenomenological extension of Jacobson-style entropic gravity, not as a PEIG application.

- **Omega Explorations and the Seven Axioms** — Documented separately. The Omega material is a personal vision document; the Seven Axioms are an AI alignment essay. Neither is physics. Both use PEIG vocabulary as design language.

When you see PEIG terminology in any of those documents, default to reading it through the engineering lens described here. If the surrounding context makes that reading awkward, that's a sign the original writing slipped frames and probably needs revision.

---

## Closing

What PEIG actually is, in one sentence: **a four-letter vocabulary for tracking how option-space, flow, persistence, and influence relate in any system where structure emerges and stabilizes.**

What it isn't: physics, a theory of everything, a derivation of consciousness, or a unified anything.

What it's for: helping me think clearly about agents, networks, and the design of systems that have to remain coherent over time.

That's the whole pitch. The work the framework supports stands or falls on whether it produces useful designs and clear thinking — not on whether the borrowed terminology can be defended as physics. By staying honest about which kind of work this is, I free the framework to do what it's actually good at.
