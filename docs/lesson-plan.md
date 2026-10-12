# Instagram clone — lesson plan

How to use this file: each lesson has a **goal**, the **concepts** you need, a **hint
ladder**, and a collapsed **answer**. Work the hints first. Open the answer only when
you've typed something, it didn't work, and you can say *what* didn't work. Then read
the answer line by line and retype it rather than pasting.

Each lesson ends with a **check** so you know it's done before moving on.

Time budget from the assessment: core in one sitting (2 to 3 hours), each stretch goal
as its own session.

---

## Lesson 0 — Set up the repo and the page head (15 min)

### Goal

The project is a git repo, lives on GitHub, and `index.html` has the four pieces of
head metadata every page needs.

### Part A — git and GitHub from the VS Code terminal

Open the integrated terminal in VS Code with **Ctrl + `** (the backtick key, top-left
of the keyboard). Make sure the prompt shows you are in `Instagram-clone`. If not:

```
cd ~/Downloads/Dev/Instagram-clone
```

This project is different from your portfolio lessons in one way: there is no repo
yet. So the first publish has two extra steps (init and create) that you won't repeat.

```
git init -b main
```
Turns this folder into a git repo whose first branch is called `main`.

```
git status
```
Look at the list. You should see your files but **not** `.DS_Store`. That's
`.gitignore` doing its job. Read `.gitignore` and tell me why `node_modules` is listed.

```
git add .
git commit -m "Add Scrimba starter files and project scaffolding"
```
Stage everything, then record the first snapshot. This commit is your "before" picture.

```
gh repo create Instagram-clone --public --source=. --remote=origin --push
```
Creates the GitHub repo, wires this folder to it as `origin`, and pushes `main`.

```
gh repo view --web
```
Opens it in the browser so you can confirm it's there.

### Part B — the lesson flow (you'll repeat this for every lesson)

```
gh issue create --title "Build the first post" --body "Hand-write the first post from index.js in semantic HTML and style it to match the Scrimba design. Icons fade on hover."
```
Creates issue #1. Note the number it prints.

```
git switch -c first-post
```
Creates a branch and moves onto it. Branch names: short, lowercase, hyphens.

Now do Lessons 1 to 3 on this branch. Commit after each lesson, not just at the end.
When done, come back to Lesson 4 to publish.

### Part C — the page head

Open `index.html`. The starter is missing four things that your portfolio-css repo
has. Without looking at that repo first, try to name them.

<details>
<summary>Hint 1</summary>

One tells the browser the document type. One tells it the language. One tells it the
character encoding. One tells phones not to zoom out. And the tab needs a name.
</details>

<details>
<summary>Hint 2</summary>

`<!DOCTYPE ...>`, `<html lang="...">`, `<meta charset="...">`,
`<meta name="viewport" content="...">`, `<title>`.
</details>

<details>
<summary>Answer</summary>

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram clone</title>
        <link rel="stylesheet" href="index.css">
    </head>
```

Why each line matters:

- `<!DOCTYPE html>` puts the browser in standards mode. Without it, old quirks
  change how box sizing and heights work.
- `lang="en"` lets screen readers pick the right voice and lets browsers offer
  translation.
- `charset="UTF-8"` makes sure characters like curly quotes and emoji render.
- The viewport meta stops phones from rendering the page at 980px and shrinking it.
- `<title>` is what shows in the tab, bookmarks, and search results.

One more: change the script tag at the bottom to
`<script type="module" src="index.js"></script>`. Vite needs `type="module"` to
bundle the file when you run `npm run build`. In dev it works either way.
</details>

### Check

`git status` shows `index.html` modified. Commit it:

```
git add index.html
git commit -m "Add doctype, lang, charset, viewport, and title"
```

---

## Lesson 1 — The first post in semantic HTML (30 min)

### Goal

`index.html` has a top bar and one post, written by hand from the first object in
`index.js` (Vincent van Gogh). No CSS yet. Ugly is fine.

### Concepts

- **Semantic HTML** means picking the element that says what the content *is*, not
  how it looks. A `div` says nothing. A `header` says "this is the introduction to
  the thing it's inside."
- Semantic elements can nest. A page can have a `header`; an `article` inside the
  page can have its own `header` too.

### Think before you type

Look at the Scrimba design and list the pieces of one post from top to bottom. You
should get something like: avatar + name + location, big image, three icons, like
count, username + comment.

Now ask of each piece: *what is it?*

- A post in a feed is a self-contained piece of content → which element?
- The avatar, name, and location introduce the post → which element?
- The big image is the main media of the post → which element?
- The three icons are things the user can do → which element wraps each one?
- The like count and the comment are just text → which element?

<details>
<summary>Hint 1 — the skeleton</summary>

```
header (page top bar: logo on the left, user avatar on the right)
main
  article (one post)
    header (avatar, name, location)
    img or figure (the post image)
    div or section (the three icons)
    p (likes)
    p (username + comment)
```
</details>

<details>
<summary>Hint 2 — the details that trip people up</summary>

- Every `img` needs `alt`. For the avatar, the person's name is a good alt. For a
  purely decorative icon, use `alt=""` (empty, not missing).
- The heart should be something clickable later. Wrap the icon in a `<button>` now
  and you won't have to restructure in stretch 2. A `button` with an `img` inside is
  fine.
- The name is bold in the design. Don't use `<b>`. Put the name in its own element
  (a `<p>` or `<span>`) and make it bold with CSS later. Bold is a *look*; HTML
  describes *meaning*.
- Likes: the number is data from `index.js`, so `<p>21 likes</p>` is fine for now.
  Stretch 1 will replace it.
</details>

<details>
<summary>Answer</summary>

```html
<body>
    <header class="top-bar">
        <img src="images/logo.png" alt="Instagram" class="logo">
        <img src="images/user-avatar.png" alt="Your profile" class="user-avatar">
    </header>

    <main>
        <article class="post">
            <header class="post-header">
                <img src="images/avatar-vangogh.jpg" alt="Vincent van Gogh" class="avatar">
                <div>
                    <p class="name">Vincent van Gogh</p>
                    <p class="location">Zundert, Netherlands</p>
                </div>
            </header>

            <img src="images/post-vangogh.jpg" alt="Painting by Vincent van Gogh" class="post-image">

            <div class="actions">
                <button class="icon-button" aria-label="Like">
                    <img src="images/icon-heart.png" alt="">
                </button>
                <button class="icon-button" aria-label="Comment">
                    <img src="images/icon-comment.png" alt="">
                </button>
                <button class="icon-button" aria-label="Share">
                    <img src="images/icon-dm.png" alt="">
                </button>
            </div>

            <p class="likes">21 likes</p>
            <p class="caption">
                <span class="username">vincey1853</span>
                just took a few mushrooms lol
            </p>
        </article>
    </main>

    <script type="module" src="index.js"></script>
</body>
```

Why these choices:

- `article` because a post makes sense on its own, outside this page.
- Two `header` elements, one for the page and one for the post. That is allowed
  and correct. CSS classes tell them apart.
- The `div` around name and location is not semantic, and that's okay. It exists
  only so flexbox can put the avatar beside a *stack* of two lines. A `div` for
  layout is the right tool when no semantic element fits.
- `aria-label` on each button gives screen readers a name, because the image
  inside has an empty alt.
- `span` for the username so you can bold it without breaking the paragraph.
</details>

### Check

Run `npm install` once (if you haven't) then `npm run dev`, open the URL it prints.
You should see a huge logo, a huge avatar, a giant painting, three huge icons, and
some text. Ugly, but everything is there. Commit:

```
git add index.html
git commit -m "Write the first post in semantic HTML"
```

---

## Lesson 2 — CSS layout (60 to 90 min)

Do this lesson in the order below. Each step changes one thing. Refresh after each.

### Step 1 — the column (10 min)

**Concept:** a centered fixed-width column is `width` or `max-width` plus
`margin: 0 auto`. `auto` on left and right margins splits the leftover space evenly.
You did this in portfolio-css with the container class.

Where should the column width go? On `body`? On `main`? On each `.post`?

<details>
<summary>Hint</summary>

Put it on the things that should be narrow: the top bar and each post. Or wrap both
in one container and put it there once. Either works. A single rule on `body` is
simplest if the top bar should be the same width as the posts.
</details>

<details>
<summary>Answer</summary>

```css
body {
    font-family: Arial, Helvetica, sans-serif;
    color: #262626;
}

.top-bar,
.post {
    max-width: 470px;
    margin: 0 auto;
}
```

Measure the actual width from your screenshot. Instagram's real feed column is 470px.
If the Scrimba design looks narrower, change the number.

`max-width` instead of `width` so the column shrinks on a phone instead of forcing a
horizontal scrollbar.
</details>

### Step 2 — the top bar (10 min)

**Concept:** flexbox with `justify-content: space-between` pushes the first child to
the left edge and the last child to the right edge. `align-items: center` lines them
up vertically. You wrote ten of these in WCAG_project.

The logo is 460×220 pixels and the user avatar is 400×400. Both need a size.

<details>
<summary>Answer</summary>

```css
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #dbdbdb;
}

.logo {
    height: 30px;
}

.user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
}
```

Set only `height` on the logo so its width scales to keep the aspect ratio. Set both
on the avatar because it should be a circle, and `border-radius: 50%` only makes a
circle out of a square.
</details>

### Step 3 — the post header (15 min)

Same tools: flex row, items centered, a gap between avatar and text.

**Concept:** `gap` is the modern way to space flex children. It replaces the old
"margin-right on every child except the last" trick.

Two things to figure out on your own:

1. The name and location are two `p` elements stacked. Browsers give `p` a top and
   bottom margin. What happens to the spacing between name and location? How do you
   fix it?
2. The name is bold and the location is smaller and lighter. Which properties?

<details>
<summary>Hint</summary>

`p { margin: 0 }` scoped to the header, or reset margins on `.name` and `.location`.
Then `font-weight: 700` on the name and `font-size: 12px` on the location.
</details>

<details>
<summary>Answer</summary>

```css
.post-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
}

.post-header p {
    margin: 0;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.name {
    font-weight: 700;
    font-size: 14px;
}

.location {
    font-size: 12px;
}
```

`object-fit: cover` is insurance. The three avatar files are square so you won't see
it do anything, but if you ever swap in a non-square avatar it crops instead of
squashing. The assessment flagged this as the one new CSS property in the core
project.
</details>

### Step 4 — the post image (5 min)

**Concept:** an `img` is an inline element with its own natural size. Two problems
follow: it ignores the column width (it's 792px wide), and inline elements sit on the
text baseline, which leaves a few pixels of mystery gap underneath.

<details>
<summary>Answer</summary>

```css
.post-image {
    width: 100%;
    display: block;
}
```

`width: 100%` means "as wide as my parent," which is the 470px column.
`display: block` removes the baseline gap. Get in the habit of putting both on any
full-width image.

The three post images are nearly square (792×792, 472×472, 1159×1121) so you don't
need a fixed height. If you want all three exactly the same height later, add
`aspect-ratio: 1 / 1; object-fit: cover;`.
</details>

### Step 5 — the icon row (15 min)

The icons are 128×128 PNGs. They need a size, a row, and a gap.

The `button` element is the fiddly part. Browsers give buttons a grey background, a
border, and padding. You want none of that.

<details>
<summary>Hint</summary>

Reset the button: `background: none; border: none; padding: 0; cursor: pointer;`.
Then size the `img` inside it, not the button.
</details>

<details>
<summary>Answer</summary>

```css
.actions {
    display: flex;
    gap: 16px;
    padding: 12px 16px;
}

.icon-button {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
}

.icon-button img {
    width: 24px;
    height: 24px;
    display: block;
}
```

`cursor: pointer` is the hand cursor. Buttons don't get it by default. It's a small
signal that says "this does something."
</details>

### Step 6 — likes and caption (10 min)

<details>
<summary>Answer</summary>

```css
.likes,
.caption {
    margin: 0 16px 8px;
    font-size: 14px;
}

.likes,
.username {
    font-weight: 700;
}
```

Grouping selectors like this is the DRY habit from your NFT-Site refactor.
</details>

### Check

Compare against your screenshot side by side. Adjust numbers, not structure. Commit:

```
git add index.css
git commit -m "Style the feed column, post header, image, and icon row"
```

---

## Lesson 3 — Icon hover (10 min)

**Concept:** `:hover` is a pseudo-class. It matches an element while the mouse is
over it. `opacity` takes 0 (invisible) to 1 (solid). A `transition` makes the change
glide instead of snap.

Write one rule that makes an icon go to 60% opacity on hover. Then add a transition.

<details>
<summary>Answer</summary>

```css
.icon-button img {
    transition: opacity 0.2s;
}

.icon-button:hover img,
.icon-button:focus-visible img {
    opacity: 0.6;
}
```

`:focus-visible` gives keyboard users the same feedback when they tab to the button.
Your WCAG project is the reason you know to add this.

Put the `transition` on the base rule, not the hover rule. If it's only on the hover
rule, the fade-in glides but the fade-out snaps.
</details>

### Check

Hover each icon. Commit:

```
git add index.css
git commit -m "Fade icons on hover and focus"
```

---

## Lesson 4 — Publish (15 min)

```
git push -u origin first-post
```
Sends the branch to GitHub. `-u` remembers the pairing so later pushes are just
`git push`.

```
gh pr create --title "Build the first post" --body "Closes #1"
```
Opens a pull request. `Closes #1` links it to the issue; merging closes the issue
automatically.

```
gh pr merge --merge --delete-branch
```
Merges into `main`, deletes the branch locally and on GitHub, and switches you back to
`main`.

```
git pull
```
Brings the merge commit down. Always do this before creating the next branch.

Then update `PROGRESS.md`: mark M1 shipped, make M2 current. Or ask me to run the
session handoff and I'll do it with you.

---

## Stretch 1 — Render all three posts with JavaScript (2 to 4 hours)

This is a learning task. Read the concepts before typing. Budget time for the reading.

### Setup

```
gh issue create --title "Render posts from the array" --body "Replace the hard-coded post with HTML generated by looping over the posts array."
git switch -c render-posts
```

### Concept 1 — template literals

A string with backticks instead of quotes. Inside it, `${ }` drops in any
JavaScript value. Line breaks are allowed.

```js
const name = "Vincent"
const greeting = `Hello, ${name}!`
```

Try it: in `index.js`, log a template literal that includes `posts[0].name`.

### Concept 2 — `innerHTML`

Every element has an `innerHTML` property. Set it to a string of HTML and the
browser builds the elements. `+=` appends.

```js
document.getElementById("feed").innerHTML = "<p>hi</p>"
```

Try it: give your `main` an `id="feed"`, delete the hard-coded `article` from
`index.html` (it's safe, it's in git history), and set `innerHTML` to a single
`<p>` from JavaScript. Confirm you see it.

### Concept 3 — `forEach`

Arrays have a `forEach` method. You hand it a function; it calls that function once
per item, passing the item in.

```js
posts.forEach(function(post) {
    console.log(post.name)
})
```

Try it: log all three names.

### Now combine them

Build a function that takes one post object and returns the HTML for one `article`
as a template literal. Then loop over `posts`, call the function for each, and append
to `innerHTML`.

<details>
<summary>Hint 1</summary>

Copy the `article` you deleted from `index.html` into the template literal. Then
replace each hard-coded value with `${post.something}`. There are seven: name,
username, location, avatar, post, comment, likes.
</details>

<details>
<summary>Hint 2</summary>

```js
function getPostHtml(post) {
    return `
        <article class="post">
            ...
        </article>
    `
}

posts.forEach(function(post) {
    feed.innerHTML += getPostHtml(post)
})
```
</details>

<details>
<summary>Answer</summary>

```js
const feed = document.getElementById("feed")

function getPostHtml(post) {
    return `
        <article class="post">
            <header class="post-header">
                <img src="${post.avatar}" alt="${post.name}" class="avatar">
                <div>
                    <p class="name">${post.name}</p>
                    <p class="location">${post.location}</p>
                </div>
            </header>

            <img src="${post.post}" alt="Post by ${post.name}" class="post-image">

            <div class="actions">
                <button class="icon-button" aria-label="Like">
                    <img src="images/icon-heart.png" alt="">
                </button>
                <button class="icon-button" aria-label="Comment">
                    <img src="images/icon-comment.png" alt="">
                </button>
                <button class="icon-button" aria-label="Share">
                    <img src="images/icon-dm.png" alt="">
                </button>
            </div>

            <p class="likes">${post.likes} likes</p>
            <p class="caption">
                <span class="username">${post.username}</span>
                ${post.comment}
            </p>
        </article>
    `
}

function renderFeed() {
    let html = ""
    posts.forEach(function(post) {
        html += getPostHtml(post)
    })
    feed.innerHTML = html
}

renderFeed()
```

Why build the string first and set `innerHTML` once, instead of `+=` inside the
loop? Each `innerHTML +=` throws away and rebuilds everything already rendered.
With three posts it doesn't matter. With three hundred it would. Building the string
then assigning once is the habit to form.

Why a `renderFeed` function instead of loose code? Because stretch 2 needs to
re-render after a like, and a function can be called again.
</details>

### Check

All three posts show. The hard-coded article is gone from `index.html`. Publish with
the Lesson 4 flow using the new issue number.

---

## Stretch 2 — Increment likes on click (1 to 2 hours)

```
gh issue create --title "Increment likes on click" --body "Clicking the heart on a post adds one to that post's like count."
git switch -c like-button
```

### The problem to understand first

You already know `addEventListener`. The new problem is **which post** was clicked.
Three hearts, one array. When a heart is clicked, how does the code know it was the
second post?

Second problem: the buttons were created by `innerHTML`. If you re-render after a
click, the old buttons are destroyed and any listeners on them die with them.

### Concept 1 — data attributes

Any HTML attribute starting with `data-` is yours to use. JavaScript reads them
through `element.dataset`. So `<button data-index="1">` gives `button.dataset.index`
→ `"1"` (a string; convert with `Number()`).

How do you get the index inside `forEach`? It passes a second argument:

```js
posts.forEach(function(post, index) { ... })
```

### Concept 2 — event delegation

Instead of a listener on each heart, put **one** listener on the `feed` container.
Clicks bubble up from the heart to the container. Inside the handler,
`event.target` is the element actually clicked. Check whether it has the data
attribute you care about. One listener, never destroyed by re-rendering.

Try it: add a listener to `feed` that logs `event.target`. Click around. Notice that
clicking the heart logs the `img`, not the `button`. How would you get from the
`img` to the `button`? Look up `closest()`.

<details>
<summary>Hint</summary>

1. In `getPostHtml`, give the like button `data-index="${index}"`. That means
   `getPostHtml` needs to accept `index` as a second parameter.
2. One listener on `feed`. Inside: `const button = event.target.closest("[data-index]")`.
   If it's null, the click wasn't on a heart; return.
3. `posts[Number(button.dataset.index)].likes += 1`, then `renderFeed()`.
</details>

<details>
<summary>Answer</summary>

Change the button line inside `getPostHtml`:

```js
function getPostHtml(post, index) {
    return `
        ...
                <button class="icon-button" aria-label="Like" data-index="${index}">
                    <img src="images/icon-heart.png" alt="">
                </button>
        ...
    `
}
```

Pass the index in `renderFeed`:

```js
posts.forEach(function(post, index) {
    html += getPostHtml(post, index)
})
```

Add the listener once, after `renderFeed()`:

```js
feed.addEventListener("click", function(event) {
    const likeButton = event.target.closest("[data-index]")
    if (!likeButton) {
        return
    }
    const index = Number(likeButton.dataset.index)
    posts[index].likes += 1
    renderFeed()
})
```

The flow: click → find the heart button (or bail) → read which post → change the
data → redraw from the data. Data changes first, screen follows. That order is the
core idea behind every framework you'll meet later.

Bonus from the Icebox: a `dblclick` listener on `.post-image` with its own
`data-index` does the Instagram double-tap.
</details>

### Check

Click each heart. Each post's count goes up independently. Refresh: counts reset to
the array values, which is correct for this project. Publish.
