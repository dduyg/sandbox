# How to Choose the Right GitHub License (Without Needing a Law Degree)

Choosing the right open-source license for your GitHub repository usually comes down to one simple question: **How much freedom do you actually want to give people using your code?**

Pick wrong, and your late-night side project might end up powering a massive commercial software suite without giving you a single line of credit. Conversely, pick a license that is too strict, and you might scare off developers who just wanted to use your utility library for a fun weekend hackathon.

Navigating open-source licensing doesn't have to be overwhelming. Here is a straightforward breakdown to help you pick the perfect license for your project—and even monetize it down the line.

## The Big Three: How 90% of GitHub Projects Are Licensed

If you want to keep things simple, almost every public repository on GitHub falls into one of three core categories based on creator intent:

| Main goal | Suggested approach |
|---|---|
| "Do whatever, just keep my name on it" | **MIT License** (Permissive) |
| "Share, but keep it open-source" | **Apache 2.0** / **MPL 2.0 / LGPL** (depending on your needs) |
| "Force everyone to share back" | **GPLv3** (Strong Copyleft) |

### 1. The "Do Whatever, Just Don't Sue Me" Route: MIT License

- **The Vibe:** Maximum freedom, minimal friction.
- **How It Works:** Anyone can copy, modify, distribute, or even sell your code inside a closed-source product. The key requirements include preserving the copyright notice and license text and accepting the license's disclaimer.
- **Best For:** Utility libraries, beginner projects, frameworks, or anything you want as many people as possible to adopt quickly.
- **Famous Examples:** React, Vue.js, Node.js.

### 2. The "Middle Ground" Route: Apache 2.0

- **The Vibe:** MIT-like permissiveness, with explicit patent protections.
- **How It Works:** Very similar to MIT in terms of freedom, but it adds an explicit patent license from contributors to users, subject to the license's terms.
- **Best For:** Developer tools, enterprise-focused projects, or large frameworks aiming for corporate adoption.
- **Famous Examples:** TensorFlow, Kubernetes, Android.

### 3. The "Keep Open Source Open" Route: GNU GPLv3

- **The Vibe:** Strong copyleft.
- **How It Works:** Anyone can use and modify your code under the GPL, but distributing a covered derivative work generally triggers GPL obligations, including source-code availability under the GPL. The exact scope depends on how the software is combined and distributed.
- **Best For:** Standalone desktop applications, security tools, or projects where you want strong protections for the freedom of derivative works.
- **Famous Examples:** Linux Kernel (GPLv2, not GPLv3), Ansible, Blender.

## Quick License Comparison Matrix

| License | Commercial Use? | Can Modify? | Can Distribute? | Forced to Share Source Code? | Patent Grant Included? |
|---|---|---|---|---|---|
| **MIT** | Yes | Yes | Yes | **No** | **No explicit patent grant** |
| **Apache 2.0** | Yes | Yes | Yes | **No** | **Yes** |
| **GPLv3** | Yes | Yes | Yes | **Yes, when GPL obligations are triggered** | **Yes** |
| **Unlicense** | Yes | Yes | Yes | **No** | **No explicit patent grant** |

## Special Cases & Edge Scenarios

- **Public Domain (Unlicense or CC0):** If you don't even care about receiving credit and want to dedicate your work to the public domain as far as legally possible, you can consider the **Unlicense** or **CC0**.
- **Non-Code Assets (Documentation, Graphics, Media):** Software licenses don't map cleanly to non-code assets. For media, books, or documentation, consider **Creative Commons** licenses such as CC-BY or CC-BY-SA.

## How to Add a License to GitHub in 30 Seconds

GitHub makes adding a license straightforward:

1. In your repository dashboard, click **Add file** > **Create new file**.
2. Name the file `LICENSE` (or `LICENSE.md`).
3. A **Choose a license template** option may appear in the repository interface.
4. Select your preferred license, fill in your name and current year where appropriate, and commit the file.

## Leveling Up: How Dual-Licensing Works

Want to monetize your open-source project? **Dual-licensing** can be one way to turn an open codebase into a sustainable business model.

Dual-licensing means offering the same codebase under two distinct legal terms: a free open-source license and a paid commercial license.

```text
                    ┌───────────────────────────┐
                    │       Your Codebase       │
                    └─────────────┬─────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       Option A: Free Tier              Option B: Paid Tier
    ┌───────────────────────┐        ┌───────────────────────┐
    │      AGPLv3 / GPLv3   │        │   Commercial License  │
    │ Free under open-source│        │ Paid for proprietary  │
    │ license terms         │        │ deployments           │
    └───────────────────────┘        └───────────────────────┘
```

### The Mechanism Behind Dual-Licensing

The business model relies on **copyleft leverage**. You release your software publicly under a copyleft license—typically **AGPLv3** or **GPLv3**.

Because copyleft licenses impose conditions when covered software is distributed (and AGPL has additional requirements for certain network use), companies that want proprietary deployments may prefer to obtain a separate commercial license.

- **Option A (Free Open Source):** Hobbyists, academics, and open-source developers use your project for free under the applicable copyleft license, while complying with its terms.
- **Option B (Paid Commercial):** Enterprise clients purchase a commercial license that permits proprietary use under separate terms.
- **Notable Examples:** MySQL, Qt, and some other commercial open-source projects have used dual-licensing or related open-core/commercial models.

## Prerequisites for Dual-Licensing

Before setting up a dual-licensing structure, keep these critical prerequisites in mind:

- **Copyright Ownership / Licensing Rights:** You need sufficient rights to offer the code under both licenses. Third-party code remains subject to its original license unless you have additional rights.
- **Contributor Agreements:** If external developers submit contributions, you need a contribution policy that gives you the rights necessary to relicense those contributions commercially. A **Contributor License Agreement (CLA)** is one possible mechanism; some projects instead use copyright assignment or other contribution terms.
- **Third-Party Dependencies:** Check the licenses of dependencies and included code carefully. You generally cannot simply relicense third-party code as if you owned it.

## How to Implement Dual-Licensing on GitHub

### Step 1: Set Up Your Root License

Add your primary open-source license file named `LICENSE` to the root directory using a copyleft framework such as **AGPLv3**.

### Step 2: Update Your `README.md`

Clearly communicate the two-tier structure at the top of your `README.md` so enterprise users understand their options immediately:

```markdown
## Licensing

This project is dual-licensed:

1. **Open Source (AGPLv3):** Free under the terms of the GNU Affero General Public License v3.0.
2. **Commercial License:** Required for proprietary deployments where AGPL compliance is not suitable.

To purchase a commercial license or discuss custom enterprise terms, visit [your website URL] or contact us at [your email].
```

### Step 3: Handle Commercial Sales and Delivery

While GitHub manages your public code, you need a fulfillment strategy for your commercial tier:

- **Payment Processing:** Services such as Stripe or Lemon Squeezy can be used to process commercial subscriptions and invoices.
- **Key Generation & Feature Access:** Depending on your product, commercial customers can receive license keys, private package access, private repositories, or other entitlement mechanisms.

## Important Caveat: Licensing Is Not Legal Advice

This guide is a practical overview, not legal advice. License obligations can depend on how software is combined, modified, distributed, or offered as a service. If your project becomes commercially important, consult a qualified lawyer or licensing specialist.

## Optimized Medium Title Ideas (for SEO & Click-Throughs)

To maximize search traffic and Medium engagement, choose one of these titles based on your primary target audience:

- **High-Intent SEO Title:** *How to Choose the Right Open-Source License for Your GitHub Project (MIT vs Apache vs GPL)*
- **Developer/Beginner Friendly:** *The Ultimate Guide to GitHub Licenses: MIT, Apache 2.0, and GPL Explained*
- **Commercial/Monetization Focus:** *How to Pick a GitHub License (And Use Dual-Licensing to Monetize Your Code)*
