# Build Small Submission Checklist

Submission deadline: **June 15, 2026**

This checklist separates completed project work from the evidence and
submission work that still needs to be finished.

## Already complete

- [x] Registered for the hackathon and joined the organization.
- [x] Deployed a public Gradio Space under `build-small-hackathon`.
- [x] Used a model below the 32B parameter limit.
- [x] Published the source in a public GitHub repository.
- [x] Linked the GitHub repository from the Space README.
- [x] Added Codex-attributed commits for the OpenAI Codex Track.
- [x] Deployed the model with Modal and `llama.cpp`.
- [x] Added Backyard AI and technology tags to the Space.
- [x] Published privacy-safe traces on the Hugging Face Hub.
- [x] Published detailed field notes.
- [x] Documented the target tracks, sponsor awards, and bonus quests.

## Still required

- [ ] Record and publish a short demo video.
- [ ] Ask at least one target user to try the app.
- [ ] Capture honest evidence of the user test and what changed as a result.
- [ ] Publish a social-media post.
- [ ] Add the final video and social-post links to the Space README.
- [ ] Submit the Space, demo video, and social post through the official
  submission flow by June 15.

## Monday, June 8: Test the complete experience

- [ ] Open the public Space in a private browser window.
- [ ] Test one text message and one screenshot with the live Modal endpoint.
- [ ] Confirm cold-start errors and retries are understandable.
- [ ] Test the layout on desktop and a phone.
- [ ] Confirm the disclaimer and official reporting links are visible.
- [ ] Confirm public traces do not contain raw text, screenshots, phone
  numbers, URLs, explanations, or reply drafts.

## Tuesday, June 9: Target-user session

Ask a person who receives Pakistani bank, courier, tax, traffic, or utility
messages to try the public Space.

- [ ] Obtain permission before recording their face, voice, screen, name, or
  feedback.
- [ ] Use a synthetic or already-public scam example, not a private message
  containing real personal information.
- [ ] Let the person use the app without coaching them through every step.
- [ ] Ask whether the risk label, red flags, and next steps are understandable.
- [ ] Ask what they would do differently after seeing the result.
- [ ] Record one short quote or anonymized feedback statement with permission.
- [ ] Note one concrete improvement or confirm why no change was needed.
- [ ] Add the user-test result to `FIELD_NOTES.md`.

Useful questions:

1. What did you think this message was before using the app?
2. Was the result understandable without technical knowledge?
3. Which warning or next step was most useful?
4. What was confusing or missing?
5. Would you use this before opening a payment link or sharing information?

## Wednesday, June 10: Apply feedback

- [ ] Fix any high-impact issue found during the user test.
- [ ] Add or update a focused test for behavioral code changes.
- [ ] Run `python -m pytest -q`.
- [ ] Run `python app.py --self-test`.
- [ ] Push the tested update to GitHub and the Space.
- [ ] Verify the Space returns to the `RUNNING` state.

## Thursday, June 11: Record the demo

Target length: roughly **60-120 seconds**, unless the submission form states a
different limit.

Suggested sequence:

1. State the problem: suspicious Pakistani notices are difficult to assess.
2. Paste a suspicious text message and show the structured result.
3. Upload a screenshot and show the multimodal analysis.
4. Point out the safe next steps and non-verification disclaimer.
5. Briefly show the custom Gradio interface.
6. Explain that Qwen3.6 27B runs through `llama.cpp` on Modal.
7. Show the public privacy-safe trace dataset.
8. Mention that Codex helped build and test the project.
9. Include the target user's reaction or summarize their feedback with
   permission.

Before publishing:

- [ ] Remove tokens, secrets, personal messages, browser autofill, and private
  account details from the recording.
- [ ] Add captions or clear narration.
- [ ] Put the Space URL and GitHub URL in the video description.
- [ ] Confirm the published video is publicly viewable without requesting
  access.

## Friday, June 12: Publish the social post

An `@` mention is **not stated as a submission requirement**. Mentions and
hashtags are optional and can improve visibility. Use the correct account
handles for the platform you choose, and do not delay submission over a
missing mention.

Draft:

> I built Pakistan Notice Helper for the Build Small Hackathon. It helps people
> assess suspicious Pakistani notices, bank alerts, courier messages, challans,
> and scam screenshots using Qwen3.6 27B MTP through llama.cpp on Modal.
>
> The app has a custom Gradio interface, publishes privacy-safe traces, and was
> built with Codex as my coding agent.
>
> Try it: [SPACE URL]
> Demo: [VIDEO URL]
> Code: [GITHUB URL]
>
> #BuildSmall #Gradio #HuggingFace #llamacpp #Modal #Codex

- [ ] Add the Space, demo, and GitHub links.
- [ ] Include one screenshot or the demo video.
- [ ] Optionally mention the official Gradio, Hugging Face, OpenAI/Codex, and
  Modal accounts using their current handles on that platform.
- [ ] Confirm the post is public.
- [ ] Save the final post URL.

## Weekend, June 13-14: Final audit

- [ ] Add a `Demo and user testing` section to the Space README.
- [ ] Add the public demo-video URL.
- [ ] Add the public social-post URL.
- [ ] Add the anonymized user-test evidence and resulting improvement.
- [ ] Verify the Space, GitHub, dataset, video, and social links.
- [ ] Confirm the Space is public and running.
- [ ] Confirm no credentials or private participant codes are committed.
- [ ] Confirm the latest GitHub commits retain Codex attribution.
- [ ] Take backup screenshots of the running app and submission materials.

## Monday, June 15: Submit

- [ ] Recheck the official hackathon page and Discord for the submission link
  and any newly published form requirements.
- [ ] Submit the Hugging Face Space URL.
- [ ] Submit the public demo-video URL.
- [ ] Submit the public social-post URL.
- [ ] Select **Backyard AI** as the main track.
- [ ] Select the OpenAI Codex Track and Modal Awards where the form permits.
- [ ] Claim Llama Champion, Off-Brand, Sharing is Caring, and Field Notes.
- [ ] Do not claim Off the Grid because live inference uses Modal.
- [ ] Save a screenshot or confirmation URL after submitting.
- [ ] Submit early enough to correct a broken link before the deadline.

## Final links

- Space: https://huggingface.co/spaces/build-small-hackathon/pakistan-notice-helper
- GitHub: https://github.com/kingabzpro/pakistan-notice-helper
- Traces: https://huggingface.co/datasets/build-small-hackathon/pakistan-notice-helper-traces
- Demo video: TODO
- Social post: TODO
- Submission confirmation: TODO
