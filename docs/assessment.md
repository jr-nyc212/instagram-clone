# Instagram Clone: Time and Skills Assessment

Date: 2026-10-07
Project: Scrimba solo project, Instagram clone (`~/Downloads/Dev/Instagram-clone`)
Basis: starter files, course transcript, and your last five repos (portfolio-css, NFT-Site, WCAG_project, Password-generator, Game Timer)

## Summary

| Scope | Estimate | Confidence |
|---|---|---|
| Core requirements (first post, semantic HTML, icon hover) | 2 to 3 hours, one sitting | High |
| Stretch 1 (render all three posts with JavaScript) | 2 to 4 hours | Medium |
| Stretch 2 (increment likes on click) | 1 to 2 hours on top of stretch 1 | Medium |

The core project uses nothing you haven't already shipped. The stretch goals introduce JavaScript patterns you haven't used yet, and that's where the time goes.

## Requirements against your existing work

| Requirement | Where you've done it | Gap |
|---|---|---|
| Semantic HTML (header, article, figure, time) | portfolio-css, NFT-Site | None |
| Flexbox rows: avatar beside name, three icons in a line | WCAG_project (ten flex containers with align-items and justify-content), Password-generator (five) | None |
| Circular avatar, full-width post image | border-radius in four repos, container widths in portfolio-css | Small: `object-fit: cover` if an avatar image isn't square |
| Hover effect on icons using opacity | opacity in WCAG_project, hover states in every repo | None |
| Centered fixed-width column | portfolio-css container pattern | None |
| Stretch 1: loop over the `posts` array and render HTML | Your JS so far uses getElementById and addEventListener only | Real gap: `forEach`, template literals, `innerHTML` |
| Stretch 2: update likes on click | addEventListener in Password-generator | Partial: changing state and re-rendering per post is new |

## Core requirements breakdown

| Step | Time | Notes |
|---|---|---|
| Set up: lang, charset, viewport, title, issue and branch | 15 min | The starter HTML has none of these |
| Hand-write the first post from `index.js` into semantic markup | 30 min | header with avatar and name, figure for the image, icon row, likes, caption |
| CSS: column, header row, image, icon row, text | 60 to 90 min | Flex for the header and icon row, `width: 100%` on the post image, `border-radius: 50%` on the avatar |
| Icon hover with opacity | 10 min | One rule with `:hover` |
| Compare against the Scrimba design and adjust | 20 to 30 min | See the first risk below |
| Commit, push, PR, merge | 15 min | Same flow as the portfolio lessons |

## Where you're likely to lose time

1. **No design image in the starter folder.** The reference only exists in the Scrimba scrim's mini-browser. Screenshot it before you start and keep it open beside your editor.
2. **The icon row.** Three images in a flex row is simple, but matching their size and spacing is fiddly. Check the pixel dimensions of the icon files in `images/` first, then decide whether to set a width on them.
3. **Image sizing.** The post images may not share one aspect ratio. `width: 100%` handles the width; decide early whether you also want a fixed height with `object-fit`.
4. **Stretch 1 is a learning task, not a typing task.** The loop is three lines once you know the pattern, but `forEach`, template literals, and `innerHTML` are new to you. Budget time to read about them, not just to write them.
5. **Stretch 2 with dynamically rendered posts.** A click handler on one hard-coded button is easy. Attaching handlers to buttons that were created in a loop, and updating the right post's count, is the part that usually stalls people.

## Suggested plan

1. **Core in one session.** Issue, branch, build the first post, publish. You should have a finished project on GitHub by hour three.
2. **Stretch 1 as its own issue and branch.** Replace the hard-coded post with a rendered one. Keep the hard-coded version in git history so you can diff against it.
3. **Stretch 2 as a third issue and branch.** Only if stretch 1 felt comfortable.

Treating each stretch goal as a separate PR keeps the core project done and shippable regardless of how far you get with the JavaScript.

## What this project will add to your skills

- First time structuring a card-style component with a header, media, actions, and caption.
- First real use of `object-fit` and image sizing in a layout, if the images need it.
- If you do stretch 1: your first data-driven rendering, which is the bridge to everything in the JavaScript modules that follow.
