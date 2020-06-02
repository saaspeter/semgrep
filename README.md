# Semgrep

![Homebrew](https://github.com/returntocorp/homebrew-semgrep/workflows/homebrew/badge.svg)
[![r2c Community Slack](https://img.shields.io/badge/r2c_slack-join-brightgreen?style=flat&logo=slack&labelColor=4A154B)](https://join.slack.com/t/r2c-community/shared_invite/enQtNjU0NDYzMjAwODY4LWE3NTg1MGNhYTAwMzk5ZGRhMjQ2MzVhNGJiZjI1ZWQ0NjQ2YWI4ZGY3OGViMGJjNzA4ODQ3MjEzOWExNjZlNTA)
[![r2c Twitter](https://img.shields.io/twitter/follow/r2cdev?label=Follow%20r2cdev&style=social&color=blue)](https://twitter.com/intent/follow?screen_name=r2cdev)

<p align="center">
  <a href="#overview">Overview</a>
  <span> · </span>
  <a href="#installation">Installation</a>
  <span> · </span>
  <a href="#usage">Usage</a>
  <br/>
  <a href="#resources">Resources</a>
  <span> · </span>
  <a href="#contributing">Contributing</a>
  <span> · </span>
  <a href="#commercial-support">Commercial Support</a>
</p>

<h3 align="center">
  A fast, lightweight static analysis tool that lets you search code like you’d write it.
</h3>  
<h3 align="center">
  Find security bugs. Enforce coding standards. Scan every PR.
</h3>
<h3 align="center">  
  Easily block bad code so you can get back to building the next great thing.
</h3>

`semgrep` is a tool for easily detecting and preventing bugs and anti-patterns
in your codebase. It combines the convenience and rapid iteration speed of
`grep`, but is "code-aware"; that is, you can easily match function calls, class
or method definitions, and more.

## Quickstart

After [installing semgrep](#installation), run the default set of checks with:

```bash
$ semgrep --config=r2c path/to/repo
```



Or try `semgrep` in your browser: [https://semgrep.live](https://semgrep.live/).

## Overview

### Key features

* **Language aware**: `semgrep` parses source code into Abstract Syntax Trees (ASTs), so it understands function calls, method and class definitions, conditionals, and more. 
  * Unlike regexes, `semgrep` won't get tripped up matching things you don't care about in comments or string literals.
* **Fast**: Static analysis should take seconds to minutes, not hours or days.
* Does **not** require compilation, run on source code directly. 
* **Handles multiple languages**: No need to learn and maintain multiple tools for your polyglot environment (e.g. ESLint, find-sec-bugs, rubocop, gosec, ...) 
* **Intuitive rule syntax**: Don't spend hours or days learning a tool's complicated DSL syntax. `semgrep` lets you search for code like you'd write it, with a few helpful abstractions.  
* **Easy to integrate**: Run `semgrep` in your CI/CD pipeline regardless of what tools and services you use. Run via CLI or Docker and output `--json`.

### Language support

| **Python** | **Javascript** | **Go &nbsp; &nbsp; &nbsp;** | **Java &nbsp;** | **C &nbsp; &nbsp; &nbsp; &nbsp;** | **Ruby** | **Typescript** | **PHP &nbsp; &nbsp;** |
|:-----------|:---------------|:----------------------------|:----------------|:----------------------------------|:---------|:---------------|:----------------------|
| ✅          | ✅              | ✅                           | ✅               | ✅                                 | 🚧 |  Coming...      | Coming...             |

... and many more coming.

### Pattern Syntax Teaser

One of the most unique and useful things about `semgrep` is how easy it is to write and iterate on queries. 

The goal is to make it as *easy as possible* to go from an idea in your head to finding the code patterns you intend to.

**Example**: Let's say you want to find all calls to a function named `exec`, and you don't care about the arguments. With `semgrep`, you could simply supply the pattern `exec(...)` and you'd match:

~~~python
# Simple cases grep could find
exec("ls")
exec(some_var)

# But you don't have to worry about whitespace
exec (foo)

# Or calls across multiple lines
exec (
    bar
)
~~~

Importantly, `semgrep` would *not* match the following:

~~~python
# grep would match this, but semgrep ignores it because 
# it doesn't have the right function name
other_exec(bar)

# semgrep ignores commented out lines
# exec(foo)

# and hard-coded strings
print("exec(bar)")
~~~

`semgrep` can even do fancy things like matching aliased imports:

~~~python
# Semgrep knows that safe_function refers to exec so it
# will still match!
#   Oof, try finding this with grep
import exec as safe_function
safe_function(tricksy)
~~~

Play with this example in your browser here: https://semgrep.live/QrkD.

For more info on what you can do in patterns, see the [pattern features
docs](docs/pattern-features.md).

## Installation

On macOS, binaries are available via [Homebrew](https://formulae.brew.sh/formula/semgrep):

```bash
$ brew install returntocorp/semgrep/semgrep
```

On Ubuntu, an install script is available on each release [here](https://github.com/returntocorp/semgrep/releases/download/v0.8.1/semgrep-v0.8.1-ubuntu-generic.sh)
```bash
$ ./semgrep-v0.8.1-ubuntu-generic.sh
```

To try `semgrep` without installation, you can also run it via [Docker](https://docs.docker.com/install/):

```
$ docker run --rm -v "${PWD}:/home/repo" returntocorp/semgrep --help
```

## Usage

Generally when you're using `semgrep` you're going to be doing one of three things:

1. Manually scanning your source code using existing rules.
1. Running `semgrep` in CI so every pull request (PR) is checked.
1. Writing new rules.


The following sections cover each in more detail.

### 🔍 1. Run Existing Rules

The easiest way to get started with `semgrep` (other than [semgrep.live](https://semgrep.live/)) is to scan your code with an existing set of rules.

You can use one our existing [Check Packs](https://semgrep.live/packs), that contain sets of rules grouped by language and/or framework:

```bash
$ semgrep --config=https://semgrep.live/c/p/java
$ semgrep --config=https://semgrep.live/c/p/python
$ semgrep --config=https://semgrep.live/c/p/golang
$ semgrep --config=https://semgrep.live/c/p/javascript
...
```

Or you can run all of our default rules for all languages as appropriate (note: each rule says what language it's for, so `semgrep` won't try to run a Python rule on Java code).

```bash
$ semgrep --config=r2c
```

You can also run a specific rule or group of rules:

```bash
# Run a specific rule
$ semgrep --config=https://semgrep.live/c/r/java.spring.security.audit.cookie-missing-samesite

# Run a set of rules
$ semgrep --config=https://semgrep.live/c/r/java.spring.security
```

All `semgrep` rules can be viewed on the [Rule Registry page](https://semgrep.live/r), which pulls the rules from YAML files defined in the [semgrep-rules](https://github.com/returntocorp/semgrep-rules) GitHub repo.


### 🛡️ 2. Integrate into CI

`semgrep` can be run via CLI or Docker and output results as JSON (via the `--json` flag), so it can be inserted into any CI pipeline and have its results processed by whatever tools you're using.

`semgrep` is aware of *diffs*, so it can report only findings that occur in newly added code, for example, in a commit or pull request.

Currently, the easiest way to integrate `semgrep` into CI is via a GitHub action we've built. See the [integrations docs](docs/integrations.md) for more details.

`semgrep` can also output results in the standardized Static Analysis Results Interchange Format ([SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/cs01/sarif-v2.1.0-cs01.html)) with the `--sarif` flag, if you use tools that accept this format. 

### ✍️ 3. Writing Rules

One of the strengths of `semgrep` is how easy it is to write rules.

This makes it possible to:
* Quickly port rules from other tools.
* Think of an interesting code pattern, and then find instances of it in your
    code.
* Find code base or org-specific bugs and antipatterns - things that built-in
    checks for existing tools won't find because they're unique to you.
* and more!

#### Simple Rules

For iterating on simple patterns, you can use the `--lang` and `--pattern`
flags.

```bash
$ semgrep --lang javascript --pattern 'eval(...)' path/to/file.js
```

The `--lang` flag tells `semgrep` which language you're targeting and `--pattern` is the code pattern to search for.

#### Advanced Rules

Some rules need more than one line of pattern to express.Sometimes you want to express code patterns, like: `X` must be true AND `Y` must be too, or `X` but NOT `Y`, or `X` must occur inside a block of code that `Y` matches.

For these cases, `semgrep` has a more powerful and flexible [YAML syntax](docs/configuration-files.md).

You can run a single rule or directory of rules specified in YAML by:
```bash
$ semgrep --config my_rule.yml path/to/dir_or_file

$ semgrep --config yaml_dir/ path/to/dir_or_file
```

**Example Advanced Rule**

Let's say we are building a financial trading application in which every `Transaction` object must first be passed to `verify_transaction()` before being passed to `make_transaction()`, or it's a business logic bug.

We can express this behavior with the following `semgrep` YAML pattern:

```yaml
rules:
- id: find-unverified-transactions
  patterns:
    - pattern: |
        public $RETURN $METHOD(...){
            ...
            make_transaction($T);
            ...
        }
    - pattern-not: |
        public $RETURN $METHOD(...){
            ...
            verify_transaction($T);
            ...
            make_transaction($T);
            ...
        }        
  message: |
    In $METHOD, there's a call to make_transaction() without first calling verify_transaction() on the Transaction object.
```

* `$RETURN`, `$METHOD`, and `$T` are *metavariables*, an abstraction that `semgrep` provides when you want to match something but you don't know exactly what it is ahead of time. 
  * You can think of *metavariables* like a [capture group](https://regexone.com/lesson/capturing_groups) in regular expressions.
* The `pattern` clause defines what we're looking for: any method that calls `make_transaction()`.
* The `pattern-not` clause *filters out* matches we don't want; in this case, methods where a transaction (`$T`) is passed to `verify_transaction()` before `make_transaction()`.
* The `message` is what's returned in `semgrep` output, either to STDOUT or as a comment on the pull request on GitHub or other systems. 
  * Note that *metavariables* can be used to customize messages and make them
    contextually relevant. Here we're helpfully telling the user the method
    where we've identified the bug.

You can play with this transaction example here: https://semgrep.live/4b4g.

**Learn More**

* See the [pattern features docs](docs/pattern-features.md) for more info and
  examples on the flexibility and power of `semgrep` patterns.
* See the [YAML configuration file docs](docs/configuration-files.md) for
  details on all of the keys that can be used and how they work.

## Resources

Learn more:
* [Semgrep presentation](https://www.youtube.com/watch?v=pul1bRIOYc8) and [slides](https://web-assets.r2c.dev/presentations/r2c-semgrep-OWASP-BayArea-21-May-2020.pdf) from the Bay Area OWASP meetup. Check out the [r2c YouTube channel](https://www.youtube.com/channel/UC5ahcFBorwzUTqPipFhjkWg) for more videos.
* More detailed [semgrep docs](docs/README.md)

Get in touch:
* Submit a [bug report](https://github.com/returntocorp/semgrep/issues)
* Join our [community Slack](https://join.slack.com/t/r2c-community/shared_invite/enQtNjU0NDYzMjAwODY4LWE3NTg1MGNhYTAwMzk5ZGRhMjQ2MzVhNGJiZjI1ZWQ0NjQ2YWI4ZGY3OGViMGJjNzA4ODQ3MjEzOWExNjZlNTA) to say "hi" or ask questions

## Contributing

`semgrep` is LGPL-licensed, feel free to help out: [CONTRIBUTING](https://github.com/returntocorp/semgrep/blob/develop/CONTRIBUTING.md).

`semgrep` is a frontend to a larger program analysis library named [`pfff`](https://github.com/returntocorp/pfff/). `pfff` began and was open-sourced at [Facebook](https://github.com/facebookarchive/pfff) but is now archived. The primary maintainer now works at [r2c](https://r2c.dev). `semgrep` was originally named `sgrep` and was renamed to avoid collisons with existing projects.

## Commercial Support

`semgrep` is proudly supported by [r2c](https://r2c.dev). We're hiring!

Interested in a fully-supported, hosted version of semgrep? [Drop your email](https://forms.gle/dpUUvSo1WtELL8DW6) and we'll ping you!

--------------

-----------

----------


## TODO: the below will be cut and/or moved into other doc files




Example patterns:

| **Pattern**                                                        | **Matches**                                                |
|:-------------------------------------------------------------------|:-----------------------------------------------------------|
| [`$X == $X`](https://semgrep.live/20B)                             | `if (node.id == node.id): ...`                             |
| [`requests.get(..., verify=False, ...)`](https://semgrep.live/jqn) | `requests.get(url, timeout=3, verify=False)`               |
| [`os.system(...)`](https://semgrep.live/1W5)                       | `from os import system; system('echo semgrep')`            |
| [`$ELEMENT.innerHTML`](https://semgrep.live/9ze)                   | ``el.innerHTML = "<img src='x' onerror='alert(`XSS`)'>";`` |
| [`$TOKEN.SignedString([]byte("..."))`](https://semgrep.live/rXW)   | `ss, err := token.SignedString([]byte("HARDCODED KEY"))`   |

→ [see more example patterns in the live registry viewer](https://semgrep.live/registry)



### Example Usage

Here is a simple Python example, `test.py`. We want to retrieve an object by ID:

```python3
def get_node(node_id, nodes):
    for node in nodes:
        if node.id == node.id:  # Oops, supposed to be 'node_id'
            return node
    return None
```

This is a bug. Let's use `semgrep` to find bugs like it, using a simple search pattern: `$X == $X`. It will find all places in our code where the left- and right-hand sides of a comparison are the same expression:

```
$ semgrep --lang python --pattern '$X == $X' test.py
test.py
3:        if node.id == node.id:  # Oops, supposed to be 'node_id'
```

## Configuration

For simple patterns use the `--lang` and `--pattern` flags. This mode of
operation is useful for quickly iterating on a pattern on a single file or
folder:

```bash
semgrep --lang javascript --pattern 'eval(...)' path/to/file.js
```

### Configuration Files

For advanced configuration use the `--config` flag. This flag automagically
handles a multitude of input configuration types:

* `--config <file|folder|yaml_url|tarball_url|registy_name>`

In the absence of this flag, a default configuration is loaded from `.semgrep.yml`
or multiple files matching `.semgrep/**/*.yml`.

### Registry

As mentioned above, you may also specify a `registry_name` as configuration.
[r2c](https://r2c.dev) provides a [registry](https://semgrep.live/r)
of rules. These rules have been tuned on thousands of repositories
using our [analysis platform](https://app.r2c.dev).

You can browse the registry at [semgrep.live/r](https://semgrep.live/r). To run a set of rules, use a rule ID or namespace.

```bash
# Run a specific rule
semgrep --config=https://semgrep.live/c/r/java.spring.security.audit.cookie-missing-samesite

# Run a set of rules
semgrep --config=https://semgrep.live/c/r/java.spring.security
```

The registry features rules for many programming errors, including security issues and correctness bugs. Security rules are annotated with CWE and OWASP metadata when applicable. OWASP rule coverage per language is displayed below.

<p align="center">
    <img width="600" src="https://web-assets.r2c.dev/semgrep-rules-owasp-coverage-20200520.png" style="max-width:100%;" />
</p>


#### Pattern Features

`semgrep` patterns make use of two primary features:

* **Metavariables like `$X`, `$WIDGET`, or `$USERS_2`.** Metavariable names can
only contain uppercase characters, or `_`, or digits, and must start with
an uppercase character or `_`. Names like `$x` or `$some_value` are
invalid.  Metavariables are used to track a variable across a specific code
scope.
* **The `...` (ellipsis) operator.** The ellipsis operator abstracts away
sequences of zero or more arguments, statements, characters, [and more](docs/pattern-features.md).

For example,
```yaml
$FILE = open(...)
```
will find all occurrences in your code where the result of an `open()` call with zero or more arguments is assigned
to a variable.

#### Composing Patterns

You can also construct rules by composing multiple patterns together.

Let's consider an example:

```yaml
rules:
  - id: open-never-closed
    patterns:
      - pattern: $FILE = open(...)
      - pattern-not-inside: |
          $FILE = open(...)
          ...
          $FILE.close()
    message: "file object opened without corresponding close"
    languages: [python]
    severity: ERROR
```

This rule looks for files that are opened but never closed. It accomplishes
this by looking for the `open(...)` pattern _and not_ a following `close()`
pattern. The `$FILE` metavariable ensures that the same variable name is used
in the `open` and `close` calls. The ellipsis operator allows for any arguments
to be passed to `open` and any sequence of code statements in-between the `open`
and `close` calls. We don't care how `open` is called or what happens up to
a `close` call, we just need to make sure `close` is called.

**For more information on rule fields like `patterns` and `pattern-not-inside`
see the [configuration documentation](docs/configuration-files.md).**

#### Equivalences

Equivalences are another key concept in `semgrep`. `semgrep` automatically searches
for code that is semantically equivalent. For example, the following patterns
are semantically equivalent. The pattern `subprocess.Popen(...)` will fire on both.

```python
subprocess.Popen("ls")
```

```python
from subprocess import Popen as sub_popen

result = sub_popen("ls")
```

For a full list of `semgrep` feature support by language see the
[language matrix](docs/matrix.md).

### Programmatic Usage

To integrate semgrep's results with other tools,
you can get results in machine-readable JSON format with the `--json` option,
or formatted according to the
[SARIF standard](https://docs.oasis-open.org/sarif/sarif/v2.1.0/cs01/sarif-v2.1.0-cs01.html)
with the `--sarif` flag.

See our [output documentation](docs/output.md) for details.