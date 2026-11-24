# Beyond Obvious — Privacy Policy

_Last updated: November 2026_

Beyond Obvious ("we", "us") operates an automated publishing tool that posts our
own short educational videos to our own social media accounts, including TikTok.

## What this app does
This application authenticates to the account owner's own TikTok account (via
TikTok's official OAuth) and uploads videos that we created, to that same
account, on a schedule. It acts only on behalf of the account owner.

## Data we access
- **TikTok account authorization.** When the owner authorizes the app, TikTok
  issues an access token and a refresh token. These are stored securely as
  encrypted secrets in our deployment environment (GitHub Actions secrets) and
  are used solely to upload and publish our own videos. They are never shared
  with any third party.
- **Basic account info** (`user.info.basic`), used only to confirm the
  authorized account and the privacy options available to it.

## Data we do NOT collect
- We do not collect, store, or process any personal data about viewers of our
  videos.
- We do not sell, rent, or share any data with advertisers or other third
  parties.
- We do not use tracking cookies or analytics beyond the public statistics
  TikTok itself provides to the account owner.

## Content
All videos published are original content created by Beyond Obvious. Narration
is synthetic (AI text-to-speech). Videos are labeled as AI-assisted where the
platform provides that option.

## Retention and deletion
Tokens are kept only as long as the automation is in use and can be revoked by
the account owner at any time from their TikTok account settings
(Security & permissions → Manage app permissions), which immediately stops this
app's access.

## Contact
For any privacy question, contact the account owner through the Beyond Obvious
TikTok profile.
