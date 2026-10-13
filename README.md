# Cupergram APK updates

This repository distributes Cupergram APKs that passed the Android checks. Telegram account credentials and signing private keys are not included.

Download the latest offered APK from [Releases](https://github.com/RastyDima/cupergram-updates/releases). The app reads [update.json](https://raw.githubusercontent.com/RastyDima/cupergram-updates/main/update.json) without a GitHub login, checks the version and SHA256, and requires the APK to have the same package and signing certificate as the installed app.

Each release includes the APK, its SHA256 and corresponding sources (GPL v2 or later). The source repository stays separate from this distribution channel.

Publication runs only for candidates submitted after the private Android check succeeds. The channel independently checks the signing identity and APK package/version, publishes the APK and source archive, then updates the feed. Installation requires Android's confirmation.
