# Oldagram – Instagram-style feed of old-master painters

A mobile-width Instagram clone where the posters are Van Gogh, Courbet and
Ducreux. The starter is Scrimba's solo project from the Fullstack Developer
Path; the brief is to build the feed from a design image with semantic HTML
and flexbox, then render the posts from a JavaScript array. Each lesson gets
its own issue, branch and pull request, so the commit history reads as a log
of the changes.

**Status:** in progress. The top bar and the first post's header are built;
the icon row, likes, caption and JavaScript rendering are next.

## What was built

- **Head metadata.** Viewport tag, page title and Source Sans 3 from Google
  Fonts, with preconnect hints so the font loads early.
- **Top bar.** Logo and user avatar in a flex row with space between, a
  bottom border and a fixed 375px page width to match the phone design.
- **First post header.** Poster avatar, name and location above the post
  image, with descriptive alt text on the images.

## Run it locally

```
npm install
npm run dev
```

Vite serves the page at http://localhost:5173.

## Built with

HTML, CSS, JavaScript and Vite. No frameworks.

## Course

Built while working through Scrimba's
[Fullstack Developer Path](https://scrimba.com/fullstack-path-c0fullstack).
The starter code and images are Scrimba's; the markup and styling are mine.
