# SemVer (Semantic Versioning)

SemVer (Semantic Versioning) is a simple and clear version number management rule designed to help developers and users understand the nature of version updates and avoid "dependency hell".

Its core idea is to convey the changes in the underlying code through the format of the version number.

- https://devhints.io/semver

---

### 1. Core Format: `MAJOR.MINOR.PATCH`

A standard SemVer version number must use the `X.Y.Z` format, where X, Y, and Z are non-negative integers, and leading zeros are not allowed (e.g., `1.02.3` is invalid).

* **`MAJOR` (Major Version)**: You must increment the major version number when you make **incompatible API changes**.
    * For example, you delete a public function, modify a function signature, or change the behavior of a function, causing code that depends on your old version to fail to work properly.
    * `1.7.2` -> `2.0.0`

* **`MINOR` (Minor Version)**: You must increment the minor version number when you **add new features** in a **backward-compatible** manner.
    * For example, you add a new public function, add optional parameters to an existing API, etc. Code that depends on your old version can still work properly.
    * `1.7.2` -> `1.8.0`

* **`PATCH` (Patch Version)**: You must increment the patch version number when you make **backward-compatible bug fixes**.
    * For example, you fix an internal implementation error without changing any API behavior or signature.
    * `1.7.2` -> `1.7.3`

### 2. Special Case: 0.y.z (Initial Development Phase)

When the major version number is `0` (e.g., `0.1.0`), it indicates that the project is in the **initial development phase**, and its API is considered unstable.

During this phase, **any changes may contain incompatible changes**. Therefore, the `^` and `~` symbols will be more conservative when handling `0.y.z` versions.

### 3. Pre-release Version (Pre-release)

If you want to release an unstable version for testing, you can append a hyphen and a series of dot-separated identifiers after `MAJOR.MINOR.PATCH`.

* **Format**: `X.Y.Z-[identifier]`
* **Examples**: `1.0.0-alpha`, `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1` (rc = Release Candidate)
* **Priority**: Pre-release versions have lower priority than their corresponding official versions. For example, `1.0.0-rc.1` has lower priority than `1.0.0`.

### 4. npm Version Range Symbols

In `package.json`, we usually don't write a fixed version but specify an acceptable version range. The most common symbols are `^` and `~`.

* **`^` (Caret)**: **"Do not change the leftmost non-zero digit"**
    * This is the default behavior of `npm install --save`.
    * It allows updates to minor and patch versions but **does not allow updates to major versions** (because major version updates mean incompatibility).
    * `^1.2.3` matches all versions `>= 1.2.3` and `< 2.0.0`.
    * `^0.2.3` matches all versions `>= 0.2.3` and `< 0.3.0` (because the leftmost non-zero digit is `2`).
    * `^0.0.3` only matches versions `>= 0.0.3` and `< 0.0.4` (because the leftmost non-zero digit is `3`).

* **`~` (Tilde)**: **"Only allow patch version updates"** (if minor version is specified)
    * It is more conservative than `^`.
    * `~1.2.3` matches all versions `>= 1.2.3` and `< 1.3.0` (only allows patch updates).
    * `~1.2` matches all versions `>= 1.2.0` and `< 1.3.0` (equivalent to `1.2.x`).
    * `~1` matches all versions `>= 1.0.0` and `< 2.0.0` (equivalent to `1.x`).

* **Other Symbols**:
    * `*` or `x`: Matches any version.
    * `>`,`<`,`>=`,`<=`: Specify ranges.
    * `1.2.3 - 2.3.4`: Specify a closed range.
    * `||`: "Or" logic, used to combine multiple ranges, e.g., `^1.0.0 || ^2.0.0`.

By following SemVer, library authors can clearly communicate the risk level of updates to users, and users can control the update risk they are willing to accept through version ranges in `package.json`, thereby achieving more stable and predictable dependency management.

---

Now, let's thoroughly explain the `~` (Tilde) symbol.

You are right. The statement "only allows patch version updates" is correct but indeed a bit abstract.

A more specific and accurate "golden rule" is:

**`~` will keep the `major version` and `minor version` you specify unchanged, only allowing the `patch version` to increase.**

Let's break down this rule through several examples:

---

### Scenario 1: Most Common Usage `~1.2.3`

Suppose you write in `package.json`: `"some-package": "~1.2.3"`

* **Analysis**:
    * The major version you specified is `1`.
    * The minor version you specified is `2`.
    * The patch version you specified is `3`.

* **Rule**:
    * The major version **must** be `1`.
    * The minor version **must** be `2`.
    * The patch version **must** be greater than or equal to `3`.

* **In other words, this is equivalent to the version range**: `>= 1.2.3` and `< 1.3.0`.

* **Specific Matching**:
    * `1.2.3` -> **Matches** (this is the minimum version)
    * `1.2.4` -> **Matches** (patch version increased)
    * `1.2.99` -> **Matches** (patch version increased)
    * `1.2.2` -> **Does Not Match** (patch version is too old)
    * `1.3.0` -> **Does Not Match** (minor version changed, which `~` does not allow)
    * `2.0.0` -> **Does Not Match** (major version changed)

**Core Purpose**: You tell npm: "I depend on `some-package` version `1.2`, and I trust the subsequent bug fixes in this version (such as `1.2.4`), but I don't want to take any risks using version `1.3.0` that may contain new features, even if it claims to be backward compatible."

---

### Scenario 2: Only Specify Major and Minor Versions `~1.2`

This is actually a shorthand for Scenario 1, which npm interprets as `~1.2.0`.

* **`"some-package": "~1.2"`** is equivalent to **`"some-package": "~1.2.0"`**
* **Matching Range**: `>= 1.2.0` and `< 1.3.0`.
* **Also Equivalent To**: `1.2.x`

---

### Key Differences Between `~` (Tilde) and `^` (Caret)

Now compare it with the default `^`, and you will fully understand the use of `~`.

| Version Range | Matches `1.2.4`? | Matches `1.3.0`? | Matches `1.3.5`? | Matches `2.0.0`? | Risk Level |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `~1.2.3` | ✅ | ❌ | ❌ | ❌ | **Lowest** (only accepts bug fixes) |
| `^1.2.3` | ✅ | ✅ | ✅ | ❌ | **Medium** (accepts bug fixes and new features) |

**Summary**:

* `^` (default) says: "I trust the author of this library. As long as the major version is not upgraded, I want both new features and bug fixes."
* `~` (more conservative) says: "I only want bug fixes. I don't want any new features for now, even if they are compatible, because new features may introduce new bugs. I will manually upgrade the minor version when I am ready."

In some projects with extremely high stability requirements and where any unexpected behavior changes are not desired, developers will choose to use `~` to lock the minor version for maximum predictability.

---

Of course, this is a very good deepening question. The behavior of `~` and `^` is significantly different when the major version number is `0` and when it is not `0`. Here is a detailed comparison table.

### Table 1: Major Version Number >= 1 (e.g., `1.x.y`)

This is the most common case for stable version dependencies.

| Input Version | Symbol | Equivalent Range | Explanation |
| :--- | :--- | :--- | :--- |
| **`1.2.3`** | `~` | `>= 1.2.3 < 1.3.0` | **Only allows patch version updates**. Locks major version `1` and minor version `2`. |
| | `^` | `>= 1.2.3 < 2.0.0` | **Allows minor and patch version updates**. Only locks major version `1`. |
| **`1.2`** | `~` | `>= 1.2.0 < 1.3.0` | **Only allows patch version updates**. Locks `1.2`. |
| | `^` | `>= 1.2.0 < 2.0.0` | **Allows minor and patch version updates**. Locks `1`. |
| **`1`** | `~` | `>= 1.0.0 < 2.0.0` | **Allows minor and patch version updates**. Because no minor version is specified, behavior is the same as `^`. |
| | `^` | `>= 1.0.0 < 2.0.0` | **Allows minor and patch version updates**. |

**Core Difference**: When the minor version number is specified (such as `1.2` or `1.2.3`), `~` is stricter than `^`, as it also locks the minor version number.

---

### Table 2: Major Version Number is 0 (e.g., `0.x.y`)

This case is used for the initial development phase (API is unstable), and the behavior of `^` becomes more conservative to avoid introducing destructive updates.

| Input Version | Symbol | Equivalent Range | Explanation |
| :--- | :--- | :--- | :--- |
| **`0.2.3`** | `~` | `>= 0.2.3 < 0.3.0` | **Only allows patch version updates**. Locks `0.2`. |
| | `^` | `>= 0.2.3 < 0.3.0` | **Only allows patch version updates**. For `0.x.y` (x>0), `^` behavior degrades to be the same as `~`. |
| **`0.2`** | `~` | `>= 0.2.0 < 0.3.0` | **Only allows patch version updates**. Locks `0.2`. |
| | `^` | `>= 0.2.0 < 0.3.0` | **Only allows patch version updates**. For `0.x` (x>0), `^` behavior degrades to be the same as `~`. |
| **`0.0.3`** | `~` | `>= 0.0.3 < 0.1.0` | **Only allows patch version updates**. Locks `0.0`. |
| | `^` | `>= 0.0.3 < 0.0.4` | **Does not allow any updates**. `^` rule is to lock the leftmost non-zero digit, here it is `3`, so the version is completely locked. |
| **`0`** | `~` | `>= 0.0.0 < 1.0.0` | **Allows minor and patch version updates**. Because no minor version is specified, behavior is the same as `^`. |
| | `^` | `>= 0.0.0 < 1.0.0` | **Allows minor and patch version updates**. |

**Core Differences**:
1. For `0.x.y` (and x > 0), the behavior of `^` and `~` is **exactly the same**.
2. For `0.0.y`, `^` will **completely lock** the version, which is stricter than `~`.
3. If only the major version is specified (`1` or `0`), the behavior of `^` and `~` is **no different**.