# AI Agent Protocol

For Claude Code, ChatGPT, Copilot and any other AI tool. Humans: read this once. Agents: follow it every session.

## What the hackathon allows
AI tools may be used "the same way working engineers do": to debug, explain concepts or speed up routine code. The team must understand and be able to explain everything in the project, and finalists are asked about their choices live.

So the AI is a fast colleague, not the author. The ideas, the design decisions and the understanding are ours.

## For humans

**Good uses**
- "Explain this error" and "why is my loss not going down?"
- Routine code: loading data, plots, a training loop for a model *we* chose
- "What are three ways to do X, and the trade-offs?" Then we choose and write down why.
- Reviewing our code and our write-up for mistakes

**Not allowed**
- "Build me a project for this challenge." The idea and approach must be ours.
- Pushing code you haven't read line by line.
- Accepting a number the AI states without running the code yourself.
- Letting the AI write the write-up from nothing. Draft it yourself, then let it edit.

**The explain-back rule**
Before a task is `done`, its owner fills in "How it works" in the task note, in their own words, and can answer on the call:
1. What does this code do, step by step?
2. Why this approach and not the obvious alternative?
3. Where could it be wrong?

If you can't, ask the AI to teach it to you, or replace the code with something simpler that you do understand. Simple and understood beats clever and opaque, both for the rubric and in the finals.

## For agents

**Start of a session**
1. Get the latest: `git pull --rebase --autostash`
2. Read Home, Idea, the open tasks in `Tasks/`, and everything in `Decisions/`.
3. Confirm with your human which task you're on. If it has no task note, create one from the template. Set `status: doing` and the owner's handle.

**While working**
- One task. Don't fix or refactor things outside it. Note them as new `todo` tasks instead.
- Prefer the simplest code that works. A beginner on the team must be able to read it. Plain functions, clear names, short cells, a comment where the *why* isn't obvious.
- Explain as you go: what you're about to do and why, before the code.
- Offer options for real design choices (model, metric, split, data source) and let the human pick. Record the choice in `Decisions/`.
- Don't add a dependency without saying so. Add it to `requirements.txt` and Credits.
- **Never invent results.** Every number in Evaluation, the write-up or the README comes from code that was actually run, and names the notebook and commit. If something wasn't run or tested, say so plainly.
- Never tune on the test set. See [[Evaluation Protocol]].
- No project code before kickoff (Sat 14 Nov 06:00 CET).

**Hard limits**
- No force-push, no rewriting pushed history.
- Push only what runs. `main` is shared by everyone the moment you sync.
- `git sync` commits everything in the folder. Run `git status` first. If there are changes that aren't from your task or aren't ready, ask your human, or commit only your files.
- If a pull stops with a conflict, show your human. Don't resolve someone else's file by guessing.
- Don't edit another person's notebook, task note or log.
- No secrets in any file. No full names, school, phone numbers, emails or private links anywhere: the repo becomes public.
- Don't submit, publish, or change repo settings unless your human asks in that session.

**End of a session**
Claude Code: run the `push` skill, which does all of this. Other tools, by hand:
1. Task note: update `status`, add the `link`, and draft "How it works" for the owner to check and rewrite in their own words.
2. Log: append an entry to `Log/<handle>.md` using the [[Session Log]] template, including the line "AI used for".
3. Share: `git status`, then `git sync "<what changed>"`. If the code isn't in a state that runs, sync only the notes (`git add vault && git commit -m "notes" && git pull --rebase && git push`) and say so.
