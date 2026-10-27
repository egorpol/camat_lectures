# Free models in VS Code: seminar research

Checked **25 October 2026**, using official documentation and a public model
catalogue. This is access research, not an MEI quality benchmark. Account access,
remaining quota and an actual VS Code request still need rehearsal before class.

For this workshop, I would offer **Copilot Free** to students who want a quick
start, and **Continue with a free API** to pairs comparing named models. Prepare
**Continue + Ollama** on the instructor's machine as the local demonstration.
Everyone can do the same XML exercise manually if access fails.

An extension, a model and a provider are different things. A free extension can
connect to a paid API. Free web chat does not supply free API access. “Free” here
means a documented ongoing free allowance or local inference; it does not mean
unlimited capacity, open-source licensing, or a guaranteed classroom service.

## 1. Copilot Free — convenient access, automatic model selection

- **Access:** GitHub account; enrol in Copilot Free in VS Code. No subscription
  payment is required. Some managed/organization accounts follow a different
  access route. [Getting started](https://docs.github.com/en/copilot/how-tos/manage-your-account/get-started-with-a-copilot-plan).
- **Models:** current Free and Student plans use **Auto only**. Do not promise
  a selectable GPT or Claude model from Copilot's full paid catalogue.
- **Allowance:** 2,000 inline completions/month plus a monthly AI-credit
  allowance. The current plan/billing pages do not specify a numeric Free chat
  credit allocation. Inspect the account's usage display; the older “50 premium
  requests/month” description is not a reliable current class budget.
  [Plans](https://docs.github.com/en/copilot/get-started/plans),
  [current billing](https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing).
- **Seminar use:** ask for one proposed XML fragment, review it, then paste it.
  Record `Auto; underlying model not exposed` if the response does not identify
  its model. This is an interface/access comparison, not a controlled comparison
  of two named models. Verified Student access is an optional advance setup;
  teacher eligibility for free Pro is separate from universal Free access.

## 2. Gemini API — named cloud models with a free tier

The current pricing page lists free input/output on **`gemini-3.8-flash`** and
**`gemini-3.5-flash-lite`**. These are two candidates for the same short MEI patch;
the pricing listing does not establish their relative MEI accuracy.
[Model pricing](https://ai.google.dev/gemini-api/docs/pricing).

Use an eligible Google account and a personal **Free Tier** project/API key in
AI Studio. Keep billing disabled for this exercise; a key from a paid project
uses that project's pricing. Google documents free-tier access in the EEA too.
[API keys](https://ai.google.dev/gemini-api/docs/api-key),
[billing](https://ai.google.dev/gemini-api/docs/billing).

Limits depend on the model/project/account. Record the **active RPM, TPM and
RPD** shown in AI Studio rather than copying an old universal limit. Quotas
apply per project, not per key; daily request limits reset at midnight Pacific
time. Capacity is not guaranteed. [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

Use Continue's Gemini provider, or VS Code's own model-provider setup described
below. Model/API compatibility has not been tested in a student account here.
Google's terms require users to be 18+ and distinguish personal experimentation
from distributing API clients. Their EEA/UK/Swiss data provisions apply the
paid-service data-use rules even to unpaid quota; avoid the blanket claim that
all free-tier prompts everywhere train the model.
[Terms](https://ai.google.dev/gemini-api/terms).

**Do not install the old free Gemini Code Assist route:** Google says its
consumer IDE extensions stopped serving requests on **18 June 2026**. Gemini's
separate API remains a different route. Antigravity is another product and is
not the standard VS Code extension used in this exercise.
[Deprecation notice](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals).

## 3. OpenRouter free variants — several named models through one provider

The [saved catalogue snapshot](../../02-building-an-edition/teacher/references/free-models/openrouter-2026-10-25.json)
contains **17** `:free` variants with zero prompt/completion prices. Suitable
*candidates to try*, with no MEI quality claim:

- [`poolside/laguna-xs-2.1:free`](https://openrouter.ai/poolside/laguna-xs-2.1:free): text/code candidate.
- [`nvidia/nemotron-3.5-lightning:free`](https://openrouter.ai/nvidia/nemotron-3.5-lightning:free): another text candidate.
- [`google/gemma-4-31b-it:free`](https://openrouter.ai/google/gemma-4-31b-it:free): catalogue lists image input as well as text; optional crop experiment.

All three advertise tool support in the retrieved catalogue; that does not
prove reliable editing or music reading. The full snapshot also includes
non-editing specialists, so the count is not a list of 17 recommended editors.
Source: [public models API](https://openrouter.ai/api/v1/models).

An OpenRouter account/API key is needed. The free plan requires no purchase;
the documented caps are **20 requests/minute and 50/day**, increasing to
1,000/day after at least $10 of credits purchased. The seminar uses the
no-purchase tier. An agent may make several requests for one user prompt.
[Pricing and limits](https://openrouter.ai/pricing).

Choose the exact `:free` entry. A paid sibling has different pricing; appending
`:free` to an arbitrary model does not create a free endpoint.
[Free variants](https://openrouter.ai/docs/guides/routing/model-variants/free).
The [`openrouter/free` router](https://openrouter.ai/openrouter/free) randomly
chooses among eligible free models, so avoid it for a named-model comparison.
Availability varies and provider data policies differ; for example, the Laguna
page explicitly describes possible training use. Stricter privacy settings may
reduce the available provider pool.
[Data handling](https://openrouter.ai/docs/guides/privacy/data-collection).

To refresh the public metadata without an API key or an inference request:

```sh
python tools/snapshot_free_models.py --output /tmp/openrouter-free-new.json
```

Existing snapshots are preserved. Metadata is not a successful inference test.

## 4. Ollama — local inference on a prepared machine

Use **`qwen2.5-coder:7b`** as a modest, established text-code example:
the Q4_K_M download is **4.7 GB**, with an Apache-2.0 notice. The smaller
**`qwen2.5-coder:3b`** download is **1.9 GB** and has a different Qwen research
license. These sizes describe weights, not required RAM. Neither example is a
vision model. [7B model](https://ollama.com/library/qwen2.5-coder:7b),
[3B model](https://ollama.com/library/qwen2.5-coder:3b).

After installing Ollama, download before class:

```sh
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

Local inference has no provider token bill or monthly provider quota. It uses
the machine's RAM/CPU/GPU and electricity; context size affects memory. CPU
inference is possible, but classroom speed needs measurement. Start with a
4,096-token context and one measure. Ollama says locally run prompts stay local;
its cloud-model feature is separate. [Ollama FAQ](https://docs.ollama.com/faq).

Use the [Continue Ollama provider](https://docs.continue.dev/customize/model-providers/top-level/ollama).
This local route has not been downloaded or benchmarked in this preparation.

## Connect a provider in VS Code

**Current native VS Code route:** run **Chat: Manage Language Models → Add
Models**, choose the provider and enter its key/configuration. BYOK chat works
without a Copilot plan or GitHub sign-in; provider billing still applies. Models
used in agent chat must support tool calling. For local Ollama, current docs
deprecate the built-in provider and point to the official Ollama extension.
Some agent-harness combinations remain experimental. Rehearse with the exact
student VS Code version. [VS Code model setup](https://code.visualstudio.com/docs/agent-customization/language-models).

**Portable comparison route:** install the official
[Continue extension](https://docs.continue.dev/ide-extensions/install), then open
**Local Config** using its configuration selector/gear. Merge one supplied
example into your existing configuration; do not replace your whole setup.
Templates are in [examples/model-configs](../../02-building-an-edition/examples/model-configs/README.md).
They use the documented [Gemini](https://docs.continue.dev/customize/model-providers/top-level/gemini),
[OpenRouter](https://docs.continue.dev/customize/model-providers/top-level/openrouter)
and [Ollama](https://docs.continue.dev/customize/model-providers/top-level/ollama)
providers. Begin in Chat with a patch proposal; automatic tool-driven editing is
optional. Manual application works even when tool support is weak.

Continue resolves the templates' secret references from a local `.env` file,
including `~/.continue/.env`; an export in a terminal is not sufficient for its
IDE extension. Keep actual keys outside the course repository, notebooks and
experiment log. [Local secrets](https://docs.continue.dev/faqs#local-config).

## Codex and other existing subscriptions

The current OpenAI pricing page advertises **GPT-6 Luna for Free in the desktop
app, subject to rollout**; its Plus entry explicitly includes the IDE extension.
That does not establish a universal free VS Code entitlement. Treat Codex as
an optional route for accounts that already have IDE access, and inspect their
actual usage limits. An API key uses separate API billing. Earlier promotional
descriptions should not become the seminar's free-access promise.
[OpenAI pricing](https://learn.chatgpt.com/docs/pricing),
[IDE extension](https://learn.chatgpt.com/docs/codex/ide).

## What to rehearse and compare

The [26 October SVG editorial extension](../guides/svg-editorial-workflow.md) adds
source/engraving inspection and an optional tool-assisted candidate loop. Its
main A/B comparison holds the model fixed and varies whether SVG source is
supplied. Use an image-capable route for that task; text-only models can inspect
SVG source and work from a verified verbal reading. Free access does not
establish music/SVG accuracy or guarantee that an extension sends SVG as text.
The prepared five-measure SVG is about 50 KB before its MEI context; a small
4,096-token local setup may need a shorter passage or a larger context and more
memory. Do not silently truncate glyph definitions to make it fit. Treat the
local Qwen example as a modest code/text option, and rehearse the visual/SVG
exercise on the actual model chosen for the demonstration.

Before class, make **one small request per chosen route**, check its actual
model/endpoint and remaining quota, then repeat the chosen route on a student
account/machine. The documentation review and catalogue GET above are completed;
provider sign-up, extension login, inference, latency and MEI quality tests
are **not yet performed**.

For the classroom, use [the same Schumann prompt](../../02-building-an-edition/examples/model-prompts/restore-forte.md)
in a fresh conversation on two named models. Keep the source-verified text,
MEI excerpt and instructions identical. Record time, proposed patch, unexpected
changes, parse/schema/render outcome and human source check in the
[experiment template](../../02-building-an-edition/examples/model-prompts/experiment-template.json).
Do not rank models by a single successful render. The
[editing guide](../guides/live-editing.md) fits this comparison into the existing 30-minute
exercise; account setup and model downloads happen before the session.
