# Rules

Ten rules. If a situation isn't covered, pick whatever keeps `main` working and the team informed.

1. **`main` always runs.** Code reaches `main` through a pull request linked to its task (Claude does this when you say "push"). Only finished, running work is merged. Anyone can open the main notebook at any moment and run it top to bottom. If you break it, fixing it is your only task.
2. **No project code before kickoff.** Everything is written between Sat 06:00 CET and the deadline. This is a hackathon rule and breaking it can disqualify us.
3. **If you can't explain it, it doesn't merge.** That includes code an AI wrote for you. Finalists are questioned live. See [[AI Agent Protocol]].
4. **One owner per task, one task at a time.** No card on the board, no work. A card takes 30 seconds. See [[Task Protocol]].
5. **Stuck for 20 minutes? Say so.** Unmute and ask. Being blocked quietly is the most expensive thing we can do.
6. **Decisions get written down.** If it was agreed on the call and affects someone else's work, it goes in `Decisions/` or it didn't happen.
7. **Baseline first, measure everything.** No model result counts without a number next to a baseline. See [[Evaluation Protocol]].
8. **Credit as you go.** Every dataset, pre-trained model and library goes into Credits the moment you first use it.
9. **Cut scope, never the deadline.** We submit Sunday 21:00 CET with whatever works. P0 tasks only until the MVP gate.
10. **Sleep and eat.** Nobody is expected online between 23:00 and 08:00. Tired people break `main`.

Hackathon rules we must not break (from the Project Briefs, all in Hackathon Brief):
- **AI must be central.** The model does the main job. An app built with AI coding tools is not enough.
- **Make it your own.** Our own user, data or question on top of any suggested project.
- **Public or synthetic data only,** no personal information without permission, every source cited.
- **Health or finance:** the exact prototype disclaimer in the write-up.
- **Honest results,** on test data the model never saw.
- **No help from the organisers** on technical problems. We help each other.

Two housekeeping rules that protect us:
- No API keys, passwords or tokens in git, ever. Use Colab Secrets or a local `.env`.
- No full names, school, faces, phone numbers, emails or private links anywhere in the repo, the write-up or the video. That includes this vault: the repo becomes public for the judges, and Round 1 is judged blind. Use handles (see Team).
